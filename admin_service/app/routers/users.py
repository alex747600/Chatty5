import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import requests
from app.schemas import User, UserList, RoleUpdate, DeleteUserRequest
from app.dependencies import get_current_admin, TokenData
from app.database import get_db
from app.models import AuditLog
from app.utils import log_to_sentry
from datetime import datetime

router = APIRouter(prefix="/admin/users", tags=["Users"])

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8003")

@router.get("", response_model=UserList)
async def list_users(token: TokenData = Depends(get_current_admin)):
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/users")
        response.raise_for_status()
        users = response.json()
        return {"users": users}
    except requests.RequestException as e:
        log_to_sentry(token.user_id, "list_users", 0, str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth Service unavailable")

@router.post("/{user_id}/block")
async def block_user(user_id: int, token: TokenData = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/users/{user_id}/block")
        response.raise_for_status()
        log = AuditLog(
            admin_id=token.user_id,
            action="block_user",
            target_id=user_id,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        log_to_sentry(token.user_id, "block_user", user_id)
        return {"message": f"User {user_id} blocked"}
    except requests.RequestException as e:
        log_to_sentry(token.user_id, "block_user", user_id, str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth Service unavailable")

@router.post("/{user_id}/unblock")
async def unblock_user(user_id: int, token: TokenData = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/users/{user_id}/unblock")
        response.raise_for_status()
        log = AuditLog(
            admin_id=token.user_id,
            action="unblock_user",
            target_id=user_id,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        log_to_sentry(token.user_id, "unblock_user", user_id)
        return {"message": f"User {user_id} unblocked"}
    except requests.RequestException as e:
        log_to_sentry(token.user_id, "unblock_user", user_id, str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth Service unavailable")

@router.patch("/{user_id}/role")
async def update_role(user_id: int, role_data: RoleUpdate, token: TokenData = Depends(get_current_admin), db: Session = Depends(get_db)):
    if role_data.role not in [0, 1, 2]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be 0, 1, or 2")
    try:
        response = requests.patch(f"{AUTH_SERVICE_URL}/users/{user_id}/role", json={"role": role_data.role})
        response.raise_for_status()
        log = AuditLog(
            admin_id=token.user_id,
            action="change_role",
            target_id=user_id,
            reason=f"Role changed to {role_data.role}",
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        log_to_sentry(token.user_id, "change_role", user_id, f"Role changed to {role_data.role}")
        return {"message": f"User {user_id} role updated to {role_data.role}"}
    except requests.RequestException as e:
        log_to_sentry(token.user_id, "change_role", user_id, str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth Service unavailable")

@router.delete("/{user_id}")
async def delete_user(user_id: int, request: DeleteUserRequest, token: TokenData = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        response = requests.delete(f"{AUTH_SERVICE_URL}/users/{user_id}")
        response.raise_for_status()
        log = AuditLog(
            admin_id=token.user_id,
            action="delete_user",
            target_id=user_id,
            reason=request.reason,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        log_to_sentry(token.user_id, "delete_user", user_id, request.reason)
        return {"message": f"User {user_id} deleted"}
    except requests.RequestException as e:
        log_to_sentry(token.user_id, "delete_user", user_id, str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth Service unavailable")