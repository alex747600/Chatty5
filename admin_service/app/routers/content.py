import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import requests
from app.schemas import ReportList
from app.dependencies import get_current_admin, TokenData
from app.database import get_db
from app.models import AuditLog
from app.utils import log_to_sentry
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Content Moderation"])

POST_SERVICE_URL = os.getenv("POST_SERVICE_URL", "http://post_service:8003")

@router.get("/reports", response_model=ReportList)
async def list_reports(token: TokenData = Depends(get_current_admin)):
    try:
        response = requests.get(f"{POST_SERVICE_URL}/reports")
        response.raise_for_status()
        reports = response.json()
        return {"reports": reports}
    except requests.RequestException as e:
        log_to_sentry(token.user_id, "list_reports", 0, str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Post Service unavailable")

@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, token: TokenData = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        response = requests.delete(f"{POST_SERVICE_URL}/posts/{post_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        response.raise_for_status()
        log = AuditLog(
            admin_id=token.user_id,
            action="delete_post",
            target_id=post_id,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        log_to_sentry(token.user_id, "delete_post", post_id)
        return {"message": f"Post {post_id} deleted"}
    except requests.RequestException as e:
        log_to_sentry(token.user_id, "delete_post", post_id, str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Post Service unavailable")

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, token: TokenData = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        response = requests.delete(f"{POST_SERVICE_URL}/comments/{comment_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        response.raise_for_status()
        log = AuditLog(
            admin_id=token.user_id,
            action="delete_comment",
            target_id=comment_id,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        log_to_sentry(token.user_id, "delete_comment", comment_id)
        return {"message": f"Comment {comment_id} deleted"}
    except requests.RequestException as e:
        log_to_sentry(token.user_id, "delete_comment", comment_id, str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Post Service unavailable")