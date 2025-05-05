import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models import Subscription
from app.database import get_db, async_session
from unittest.mock import AsyncMock
from app.clients import AuthClient, PostClient
import httpx

client = TestClient(app)


@pytest.fixture
async def db_session():
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_get_all_users(db_session: AsyncSession, monkeypatch):
    monkeypatch.setattr("app.core.deps.get_current_user", AsyncMock(return_value=1))
    monkeypatch.setattr("app.clients.AuthClient.get_all_users", AsyncMock(return_value=[
        {"id": 1, "username": "user1"},
        {"id": 2, "username": "user2"}
    ]))

    response = client.get("/subscriptions/users")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["username"] == "user1"


@pytest.mark.asyncio
async def test_subscribe_to_user(db_session: AsyncSession, monkeypatch):
    monkeypatch.setattr("app.core.deps.get_current_user", AsyncMock(return_value=1))
    monkeypatch.setattr("app.clients.AuthClient.get_user_id_by_token", AsyncMock(return_value=1))

    response = client.post("/subscriptions/subscribe/2")
    assert response.status_code == 200
    assert response.json() == {"detail": "Subscribed successfully"}

    subscription = await db_session.execute(
        select(Subscription).where(
            Subscription.user_id == 2,
            Subscription.follower_id == 1
        )
    )
    assert subscription.scalars().first() is not None


@pytest.mark.asyncio
async def test_subscribe_to_user_by_username(db_session: AsyncSession, monkeypatch):
    monkeypatch.setattr("app.core.deps.get_current_user", AsyncMock(return_value=1))
    monkeypatch.setattr("app.clients.AuthClient.get_user_id_by_token", AsyncMock(return_value=1))

    async def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200

            def json(self):
                return {"user_id": 2}

        return MockResponse()

    monkeypatch.setattr(httpx.AsyncClient, "get", AsyncMock(side_effect=mock_get))

    response = client.post("/subscriptions/subscribe/username/testuser")
    assert response.status_code == 200
    assert response.json() == {"detail": "Subscribed successfully"}

    subscription = await db_session.execute(
        select(Subscription).where(
            Subscription.user_id == 2,
            Subscription.follower_id == 1
        )
    )
    assert subscription.scalars().first() is not None


@pytest.mark.asyncio
async def test_unsubscribe_from_user(db_session: AsyncSession, monkeypatch):
    monkeypatch.setattr("app.core.deps.get_current_user", AsyncMock(return_value=1))

    subscription = Subscription(user_id=2, follower_id=1)
    db_session.add(subscription)
    await db_session.commit()

    response = client.delete("/subscriptions/unsubscribe/2")
    assert response.status_code == 200
    assert response.json() == {"detail": "Unsubscribed successfully"}

    subscription = await db_session.execute(
        select(Subscription).where(
            Subscription.user_id == 2,
            Subscription.follower_id == 1
        )
    )
    assert subscription.scalars().first() is None


@pytest.mark.asyncio
async def test_get_user_posts(db_session: AsyncSession, monkeypatch):
    monkeypatch.setattr("app.core.deps.get_current_user", AsyncMock(return_value=1))
    monkeypatch.setattr("app.clients.PostClient.get_user_posts", AsyncMock(return_value=[
        {"id": 1, "user_id": 2, "content": "Test post"}
    ]))

    response = client.get("/subscriptions/users/2/posts")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["content"] == "Test post"


@pytest.mark.asyncio
async def test_list_subscriptions(db_session: AsyncSession, monkeypatch):
    monkeypatch.setattr("app.core.deps.get_current_user", AsyncMock(return_value=1))

    subscription = Subscription(user_id=2, follower_id=1)
    db_session.add(subscription)
    await db_session.commit()

    response = client.get("/subscriptions/subscriptions")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == 2
    assert response.json()[0]["follower_id"] == 1


@pytest.mark.asyncio
async def test_get_feed(db_session: AsyncSession, monkeypatch):
    monkeypatch.setattr("app.core.deps.get_current_user", AsyncMock(return_value=1))
    monkeypatch.setattr("app.clients.PostClient.fetch_posts", AsyncMock(return_value=[
        {"id": 1, "user_id": 2, "content": "Test post"}
    ]))

    subscription = Subscription(user_id=2, follower_id=1)
    db_session.add(subscription)
    await db_session.commit()

    response = client.get("/subscriptions/feed")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["content"] == "Test post"