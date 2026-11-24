from datetime import UTC, datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, UnauthorizedError
from app.domain.auth import crud, security
from app.domain.auth.models import AppUser


async def register(session: AsyncSession, login_id: str, password: str, display_name: str) -> AppUser:
    login_id = login_id.strip()
    if not login_id or not password:
        raise UnauthorizedError("auth.empty_credentials")
    if await crud.get_by_login_id(session, login_id):
        raise ConflictError("auth.login_id_taken")
    user = await crud.create(
        session,
        login_id=login_id,
        password_hash=security.hash_password(password),
        display_name=display_name.strip() or login_id,
    )
    logger.info("user registered id={} login_id={}", user.id, user.login_id)
    return user


async def authenticate(session: AsyncSession, login_id: str, password: str) -> AppUser:
    # IMPORTANT: 아이디 없음과 비밀번호 불일치를 같은 오류로 돌려준다. 계정 존재 여부를 흘리지 않는다.
    user = await crud.get_by_login_id(session, login_id.strip())
    if user is None or not security.verify_password(password, user.password_hash):
        logger.info("login rejected login_id={}", login_id)
        raise UnauthorizedError("auth.invalid_credentials")
    user.last_login_at = datetime.now(UTC)
    await session.commit()
    return user
