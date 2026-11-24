"""로그인 의존성. auth 를 뺀 모든 라우터가 이것을 요구한다."""
from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.errors import UnauthorizedError
from app.domain.auth import crud, security
from app.domain.auth.models import AppUser


async def current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    gait_session: Annotated[str | None, Cookie(alias=security.COOKIE_NAME)] = None,
) -> AppUser:
    if not gait_session:
        raise UnauthorizedError("auth.required")
    user_id = security.read_token(gait_session)
    if user_id is None:
        raise UnauthorizedError("auth.required")
    user = await crud.get_by_id(session, user_id)
    if user is None:
        raise UnauthorizedError("auth.required")
    return user


CurrentUser = Annotated[AppUser, Depends(current_user)]
