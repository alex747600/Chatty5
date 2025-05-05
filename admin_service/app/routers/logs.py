from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas import AuditLogList
from app.dependencies import get_current_admin, TokenData
from app.database import get_db
from app.models import AuditLog

router = APIRouter(prefix="/admin", tags=["Audit Logs"])

@router.get("/logs", response_model=AuditLogList)
async def list_logs(token: TokenData = Depends(get_current_admin), db: Session = Depends(get_db)):
    logs = db.execute(select(AuditLog)).scalars().all()
    return {"logs": logs}