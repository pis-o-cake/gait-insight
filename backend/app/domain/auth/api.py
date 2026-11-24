from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.domain.auth import security, service
from app.domain.auth.deps import CurrentUser
from app.domain.auth.schemas import Credentials, DemoAccount, RegisterRequest, User

router = APIRouter(tags=["auth"])
Session = Annotated[AsyncSession, Depends(get_session)]


def _set_cookie(response: Response, user_id: int) -> None:
    token, max_age = security.issue_token(user_id)
    # CAUTION: secure 를 켜지 않는다. 로컬망 http 시연이 전제다. 외부 공개 시 반드시 켠다.
    response.set_cookie(
        security.COOKIE_NAME, token, max_age=max_age, httponly=True, samesite="lax", path="/"
    )


@router.post("/register", response_model=User, summary="가입 후 바로 로그인")
async def register(body: RegisterRequest, response: Response, session: Session) -> User:
    user = await service.register(session, body.login_id, body.password, body.display_name)
    _set_cookie(response, user.id)
    return User.model_validate(user)


@router.post("/login", response_model=User, summary="로그인")
async def login(body: Credentials, response: Response, session: Session) -> User:
    user = await service.authenticate(session, body.login_id, body.password)
    _set_cookie(response, user.id)
    return User.model_validate(user)


@router.post("/logout", summary="로그아웃")
async def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(security.COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/demo-account", response_model=DemoAccount | None, summary="시연용 계정 (없으면 null)")
async def demo_account() -> DemoAccount | None:
    # CAUTION: 로그인 없이 비밀번호를 내준다. 로컬망 시연 전용이며 DEMO_* 를 비우면 null 이다.
    settings = get_settings()
    if not settings.demo_enabled:
        return None
    return DemoAccount(login_id=settings.demo_login_id, password=settings.demo_password)


@router.get("/me", response_model=User, summary="현재 로그인한 사용자")
async def me(user: CurrentUser) -> User:
    return User.model_validate(user)
