"""비밀번호 해시와 로그인 토큰.

비밀번호 규칙·이메일 인증·비밀번호 찾기는 이 프로토타입의 범위가 아니다.
해시는 bcrypt, 토큰은 HS256 JWT 이며 서버는 세션을 저장하지 않는다.
"""
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings

ALGORITHM = "HS256"
COOKIE_NAME = "gait_session"
_BCRYPT_MAX_BYTES = 72


def _clip(password: str) -> bytes:
    # bcrypt 는 72바이트를 넘는 입력을 조용히 자른다. 길이 제한을 두지 않으므로 여기서 맞춘다.
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_clip(password), bcrypt.gensalt()).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_clip(password), password_hash.encode("ascii"))
    except ValueError:
        return False


def issue_token(user_id: int) -> tuple[str, int]:
    """(토큰, 최대 수명 초)를 돌려준다."""
    settings = get_settings()
    ttl = timedelta(hours=settings.auth_token_ttl_hours)
    payload = {"sub": str(user_id), "exp": datetime.now(UTC) + ttl}
    return jwt.encode(payload, settings.auth_secret, algorithm=ALGORITHM), int(ttl.total_seconds())


def read_token(token: str) -> int | None:
    """토큰에서 사용자 id 를 꺼낸다. 만료·위조면 None."""
    try:
        payload = jwt.decode(token, get_settings().auth_secret, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
