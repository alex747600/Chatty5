import pytest
import httpx

BASE_URL = "http://localhost:8001"  # Адрес Auth Service
POST_URL = "http://localhost:8003"  # Адрес Post Service
SUBSCRIPTION_URL = "http://localhost:8004"  # Адрес Subscription Service

@pytest.mark.asyncio
async def test_create_post_without_auth():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{POST_URL}/posts/", json={
            "title": "Unauthorized",
            "content": "Should not work"
        })
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_subscribe_without_auth():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{SUBSCRIPTION_URL}/subscriptions/subscribe/1")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_feed_without_auth():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SUBSCRIPTION_URL}/feed")
        assert response.status_code == 401
