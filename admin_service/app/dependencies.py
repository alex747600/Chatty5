from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")  # Auth Service token endpoint

class TokenData(BaseModel):
    user_id: int
    role: int

def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET", "your-secret-key"), algorithms=["HS256"])
        user_id: int = payload.get("sub")
        role: int = payload.get("role")
        if user_id is None or role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        token_data = TokenData(user_id=user_id, role=role)
        if token_data.role != 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        return token_data
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")