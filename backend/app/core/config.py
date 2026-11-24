"""환경 설정. 값은 .env 또는 컨테이너 환경 변수에서만 온다."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정.

    Attributes:
        database_url: SQLAlchemy async 접속 문자열.
        data_dir: parquet·seed 파일이 있는 디렉토리.
        auth_secret: JWT 서명 키. 비우면 기동에 실패한다.
        auth_token_ttl_hours: 로그인 쿠키 유효 시간.
        cors_origins: 개발 모드에서 허용할 출처. 비면 CORS 미들웨어를 달지 않는다.
        demo_login_id: 시연용 계정 아이디. 비면 시연 계정을 만들지 않는다.
        demo_password: 시연용 계정 비밀번호. 로그인 화면에 그대로 보인다.
        demo_display_name: 시연용 계정 표시 이름.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://gait:gait@localhost:5432/gait_insight"
    data_dir: Path = Path("data")
    auth_secret: str = ""
    auth_token_ttl_hours: int = 12
    cors_origins: str = ""
    static_dir: Path = Path("static")
    log_level: str = "INFO"
    demo_login_id: str = ""
    demo_password: str = ""
    demo_display_name: str = ""

    @property
    def demo_enabled(self) -> bool:
        return bool(self.demo_login_id and self.demo_password)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.auth_secret:
        raise RuntimeError("AUTH_SECRET is not set")
    return settings
