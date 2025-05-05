from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
import schemas
from database import get_db
import smtplib
from email.mime.text import MIMEText
from config import settings  # Импортируем settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_password_hash(password: str) -> str:
    return settings.pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return settings.pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.algorithm)
    return token

def create_email_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.email_token_expire_minutes))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.algorithm)
    return token

def verify_email_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await db.execute(select(models.User).where(models.User.username == username))
    user = user.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def verify_token(token: str) -> schemas.TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    token_data = verify_token(token)
    user = await db.execute(select(models.User).where(models.User.username == token_data.username))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.smtp_user
    msg["To"] = to_email

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)