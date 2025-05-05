import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import requests
from app.schemas import AdminStats
from app.dependencies import get_current_admin, TokenData
from app.database import get_db
from app.models import AuditLog
from app.utils import log_to_sentry
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Statistics"])

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8003")
POST_SERVICE_URL = os.getenv("POST_SERVICE_URL", "http://post_service:8006")


@router.get("/stats", response_model=AdminStats)
async def get_stats(token: TokenData = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        # Fetch user stats from Auth Service
        user_response = requests.get(f"{AUTH_SERVICE_URL}/stats")
        user_response.raise_for_status()
        user_stats = user_response.json()

        # Fetch post and comment stats from Post Service
        post_response = requests.get(f"{POST_SERVICE_URL}/stats")
        post_response.raise_for_status()
        post_stats = post_response.json()

        stats = AdminStats(
            total_users=user_stats.get("total_users", 0),
            blocked_users=user_stats.get("blocked_users", 0),
            active_users=user_stats.get("active_users", 0),
            total_posts=post_stats.get("total_posts", 0),
            total_comments=post_stats.get("total_comments", 0)
        )

        # Log the stats retrieval action
        log = AuditLog(
            admin_id=token.user_id,
            action="view_stats",
            target_id=0,  # No specific target
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        log_to_sentry(token.user_id, "view_stats", 0)

        return stats
    except requests.RequestException as e:
        log_to_sentry(token.user_id, "view_stats", 0, str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable")