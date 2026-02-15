import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/wallet_db",
)

# Создание асинхронного движка
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# Создание асинхронной сессии
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает и управляет асинхронной сессией базы данных.

    Автоматически выполняет commit при успешном завершении или rollback
    при возникновении ошибки.

    Yields:
        Асинхронная сессия базы данных для выполнения запросов.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

