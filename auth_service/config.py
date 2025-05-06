from pydantic_settings import BaseSettings, SettingsConfigDict
from passlib.context import CryptContext

class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', extra='ignore', case_sensitive=False
    )

    # База данных
    db_host: str = 'auth_db'
    db_port: int = 5432
    db_name: str = 'AuthDB'
    db_user: str = 'postgres'
    db_password: str = 'postgres'

    # JWT
    jwt_secret: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    email_token_expire_minutes: int = 60

    # SMTP
    smtp_host: str = 'smtp.gmail.com'
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str

    @property
    def async_database_url(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

    @property
    def pwd_context(self) -> CryptContext:
        return CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = AuthSettings()

# Проверка наличия SMTP-учетных данных
if not settings.smtp_user or not settings.smtp_password:
    raise ValueError("SMTP_USER и SMTP_PASSWORD должны быть заданы в .env")