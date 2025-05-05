from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Post(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SubscriptionOut(BaseModel):
    user_id: int  # подписчик
    target_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    username: str

class SubscriptionResponse(BaseModel):
    user_id: int
    target_user_id: int

    class Config:
        from_attributes = True