import httpx
from fastapi import HTTPException
from app.core.config import settings
from typing import List, Dict

class PostClient:
    def __init__(self, base_url: str = settings.url_post_service):
        self.base_url = base_url

    async def fetch_posts(self, user_ids: List[int]) -> List[Dict]:
        """Fetch posts for a list of user IDs."""
        try:
            url = f"{self.base_url}/posts"
            params = [("user_ids", str(uid)) for uid in user_ids]
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            raise HTTPException(status_code=500, detail=f"Post service error: {response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Post service error: {str(e)}")

    async def get_user_posts(self, user_id: int) -> List[Dict]:
        """Fetch all posts of a specific user."""
        try:
            url = f"{self.base_url}/posts/users/{user_id}/posts"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            raise HTTPException(status_code=500, detail=f"Post service error: {response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch user posts: {str(e)}")
