from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.auth.models import AppUser


async def get_by_login_id(session: AsyncSession, login_id: str) -> AppUser | None:
    result = await session.execute(select(AppUser).where(AppUser.login_id == login_id))
    return result.scalar_one_or_none()


async def get_by_id(session: AsyncSession, user_id: int) -> AppUser | None:
    return await session.get(AppUser, user_id)


async def create(session: AsyncSession, login_id: str, password_hash: str, display_name: str) -> AppUser:
    user = AppUser(login_id=login_id, password_hash=password_hash, display_name=display_name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
