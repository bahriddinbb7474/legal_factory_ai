from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def _normalize_async_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global engine, AsyncSessionLocal
    if AsyncSessionLocal is None:
        engine = create_async_engine(_normalize_async_database_url(settings.database_url), future=True)
        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    return AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
