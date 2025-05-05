from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from fastapi import HTTPException
from app.models import Subscription
from app.clients.auth_client import AuthClient

auth_client = AuthClient()

async def get_user_id_by_username(username: str) -> int:
    """Wrapper to get user ID from Auth Service."""
    return await auth_client.get_user_id_by_username(username)

async def get_following(user_id: int, db: AsyncSession) -> List[int]:
    """Get list of user IDs whom the given user follows."""
    result = await db.execute(
        select(Subscription.target_user_id).where(Subscription.user_id == user_id)
    )
    return result.scalars().all()

async def get_followers_ids(user_id: int, db: AsyncSession) -> List[int]:
    """Get list of user IDs who follow the given user."""
    result = await db.execute(
        select(Subscription.user_id).where(Subscription.target_user_id == user_id)
    )
    return result.scalars().all()

