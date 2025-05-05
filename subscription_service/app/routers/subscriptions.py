from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.core.config import settings
from app.clients.auth_client import AuthClient
from app.clients.post_client import PostClient
from app.core.deps import get_current_user
from app.database import get_db
from app.models import Subscription
from app.schemas import Post, SubscriptionOut, User
from app.utils.cache import get_cached_feed, set_cached_feed
from app.services.subscription_service import get_user_id_by_username

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
security_scheme = HTTPBearer()
auth_client = AuthClient()
post_client = PostClient()


@router.get("/users", response_model=List[User], summary="Get all users")
async def get_all_users(current_user: int = Depends(get_current_user)):
    """Retrieve a list of all registered users."""
    try:
        users = await auth_client.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


@router.post("/subscribe/{user_id}", summary="Subscribe to a user by ID")
async def subscribe_to_user(
        user_id: int,
        current_user: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Subscribe to a user by their user ID."""
    if user_id == current_user:
        raise HTTPException(status_code=400, detail="Cannot subscribe to yourself")

    existing_subscription = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user,
            Subscription.target_user_id == user_id
        )
    )
    if existing_subscription.scalars().first():
        raise HTTPException(status_code=400, detail="Already subscribed")

    subscription = Subscription(user_id=current_user, target_user_id=user_id)
    db.add(subscription)
    await db.commit()
    return {"detail": "Subscribed successfully"}


@router.post("/subscribe/username/{username}", summary="Subscribe to a user by username")
async def subscribe_to_user_by_username(
        username: str,
        current_user: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Subscribe to a user by their username."""
    user_id = await get_user_id_by_username(username)

    if user_id == current_user:
        raise HTTPException(status_code=400, detail="Cannot subscribe to yourself")

    existing_subscription = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user,
            Subscription.target_user_id == user_id
        )
    )
    if existing_subscription.scalars().first():
        raise HTTPException(status_code=400, detail="Already subscribed")

    subscription = Subscription(user_id=current_user, target_user_id=user_id)
    db.add(subscription)
    await db.commit()
    return {"detail": "Subscribed successfully"}


@router.delete("/unsubscribe/{user_id}", summary="Unsubscribe from a user by ID")
async def unsubscribe_from_user(
        user_id: int,
        current_user: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Unsubscribe from a user by their user ID."""
    result = await db.execute(
        delete(Subscription).where(
            Subscription.user_id == current_user,
            Subscription.target_user_id == user_id
        )
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")

    await db.commit()
    return {"detail": "Unsubscribed successfully"}


@router.get("/users/{user_id}/posts", response_model=List[Post], summary="Get all posts of a user")
async def get_user_posts(
        user_id: int,
        current_user: int = Depends(get_current_user)
):
    """Retrieve all posts of a specific user by their user ID."""
    try:
        posts = await post_client.get_user_posts(user_id)
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts: {str(e)}")


@router.get("/subscriptions", response_model=List[SubscriptionOut], summary="List subscriptions")
async def list_subscriptions(
        current_user: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Retrieve a list of subscriptions for the current user."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user)
    )
    return result.scalars().all()


@router.get("/following", response_model=List[int], summary="List followed users")
async def get_following_users(
        current_user: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Retrieve a list of user IDs that the current user follows."""
    result = await db.execute(
        select(Subscription.target_user_id).where(Subscription.user_id == current_user)
    )
    return result.scalars().all()


@router.get("/followers", response_model=List[int], summary="List followers")
async def get_followers(
        current_user: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Retrieve a list of user IDs that follow the current user."""
    result = await db.execute(
        select(Subscription.user_id).where(Subscription.target_user_id == current_user)
    )
    return result.scalars().all()


@router.get("/feed", response_model=List[Post], summary="Get user feed")
async def get_user_feed(
        current_user: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Retrieve a feed of posts from users the current user follows."""
    cached = await get_cached_feed(current_user)
    if cached:
        return cached

    result = await db.execute(
        select(Subscription.target_user_id).where(Subscription.user_id == current_user)
    )
    user_ids = result.scalars().all()

    if not user_ids:
        return []

    posts = await post_client.fetch_posts(user_ids)
    await set_cached_feed(current_user, posts)
    return posts
