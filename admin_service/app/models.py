from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    target_id = Column(Integer, nullable=False)
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)