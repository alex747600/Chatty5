from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# ========== Подключаемся к settings ==========

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Добавляем путь к приложению
sys.path.append(str(BASE_DIR / "subscription_service"))

from app.core.config import settings
from db_base import Base

# ========== Alembic config ==========
config = context.config
fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.async_database_url)

target_metadata = Base.metadata


# ========== Offline migrations ==========

def run_migrations_offline():
    url = settings.async_database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ========== Online migrations ==========

async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn,
                target_metadata=target_metadata,
                compare_type=True,
            )
        )
        await connection.run_sync(lambda conn: context.run_migrations())



# ========== Entrypoint ==========

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())



