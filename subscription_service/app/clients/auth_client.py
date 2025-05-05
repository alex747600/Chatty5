import httpx
from fastapi import HTTPException, status
from app.core.config import settings

class AuthClient:
    def __init__(self, base_url: str = settings.url_auth_service):
        self.base_url = base_url

    async def get_user_id_by_username(self, username: str) -> int:
        """Fetch user ID by username from Auth Service (public endpoint)."""
        try:
            url = f"{self.base_url}/auth/user-id-by-username"  # Без internal
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params={"username": username})
            if response.status_code == 200:
                return response.json()["user_id"]
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")
            else:
                raise HTTPException(status_code=500, detail="Auth service error")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch user ID: {str(e)}")

    async def get_user_id_by_token(self, token: str) -> int:
        """Fetch user ID from token."""
        try:
            url = f"{self.base_url}/auth/internal/user-id"
            headers = {"Authorization": f"Bearer {token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()["user_id"]
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid token")
            else:
                raise HTTPException(status_code=500, detail="Auth service error")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Auth service error: {str(e)}")

    async def get_all_users(self) -> list[dict]:
        """Fetch all users from Auth Service."""
        try:
            url = f"{self.base_url}/auth/users"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
            if response.status_code == 200:
                return response.json()["users"]  # Предполагается, что в ответе ключ "users"
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch users from Auth Service")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching all users: {str(e)}")


