from pydantic_settings import BaseSettings, SettingsConfigDict

class PostSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',           # Загружает переменные из файла .env
        extra='ignore',            # Игнорирует лишние переменные
        case_sensitive=False       # Переменные нечувствительны к регистру
    )

    db_host: str = 'post_db'
    db_port: int = 5432
    db_name: str = 'PostDB'
    db_user: str = 'postgres'
    db_password: str = 'postgres'

    post_db_url: str

    @property
    def async_database_url(self) -> str:
        # Для asyncpg (используется в приложении с async ORM)
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

    @property
    def sync_database_url(self) -> str:
        # Для psycopg2 (например, в Alembic, который работает синхронно)
        return f'postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'


# Создание глобального объекта настроек
settings = PostSettings()

