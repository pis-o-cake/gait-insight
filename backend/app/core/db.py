"""비동기 엔진과 세션 의존성."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    """모든 도메인 모델의 공통 베이스. Alembic 이 이 메타데이터를 본다."""


_settings = get_settings()
engine = create_async_engine(_settings.database_url, pool_pre_ping=True, future=True)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session
