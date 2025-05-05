from pydantic import BaseModel
from typing import List
from datetime import datetime

# Existing schemas
class User(BaseModel):
    id: int
    username: str
    email: str
    role: int
    is_blocked: bool

class UserList(BaseModel):
    users: List[User]

class RoleUpdate(BaseModel):
    role: int

class DeleteUserRequest(BaseModel):
    reason: str

class Report(BaseModel):
    id: int
    post_id: int | None
    comment_id: int | None
    reason: str
    reported_by: int
    timestamp: str

class ReportList(BaseModel):
    reports: List[Report]

class AuditLogEntry(BaseModel):
    id: int
    admin_id: int
    action: str
    target_id: int
    reason: str | None
    timestamp: datetime

class AuditLogList(BaseModel):
    logs: List[AuditLogEntry]

class AdminStats(BaseModel):
    total_users: int
    blocked_users: int
    active_users: int
    total_posts: int
    total_comments: int

# New schema for user activity statistics
class UserActivityStats(BaseModel):
    total_active_users: int
    posts_created: int
    comments_created: int