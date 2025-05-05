import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import requests
from app.schemas import UserActivityStats
from app.dependencies import get_current_admin, TokenData
from app.database import get_db
from app.models import AuditLog
from app.utils import log_to_sentry
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["User Activity"])

POST_SERVICE_URL = os.getenv("POST_SERVICE_URL", "http://post_service:8003")

@router.get("/activity", response_model=UserActivityStats)
async def get_user_activity(token: TokenData = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        # Fetch user activity stats from Post Service
        response = requests.get(f"{POST_SERVICE_URL}/user-activity")
        response.raise_for_status()
        activity_stats = response.json()

        stats = UserActivityStats(
            total_active_users=activity_stats.get("total_active_users", 0),
            posts_created=activity_stats.get("posts_created", 0),
            comments_created=activity_stats.get("comments_created", 0)
        )

        # Log the activity stats retrieval action
        log = AuditLog(
            admin_id=token.user_id,
            action="view_user_activity",
            target_id=0,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        log_to_sentry(token.user_id, "view_user_activity", 0)

        return stats
    except requests.RequestException as e:
        log_to_sentry(token.user_id, "view_user_activity", 0, str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Post Service unavailable")