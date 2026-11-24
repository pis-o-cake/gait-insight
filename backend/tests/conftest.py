"""테스트 픽스처. compose 의 Postgres 에 별도 DB 를 만들어 쓴다."""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("AUTH_SECRET", "test-secret-not-for-production-32bytes-minimum")
os.environ.setdefault("DATA_DIR", str(ROOT / "data"))
os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get("TEST_DATABASE_URL", "postgresql+asyncpg://gait:gait@localhost:5433/gait_insight_test"),
)

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.db import Base, engine  # noqa: E402
from app.domain.analysis import models as analysis_models  # noqa: F401,E402
from app.domain.auth import models as auth_models  # noqa: F401,E402
from app.domain.exercise import models as exercise_models  # noqa: F401,E402
from app.domain.record import models as record_models  # noqa: F401,E402
from app.main import app  # noqa: E402


@pytest_asyncio.fixture(scope="session", autouse=True)
async def schema():
    """테이블을 새로 만들고 참조 데이터를 seed 한다. 마이그레이션은 별도로 검증한다."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    from tools.seed import main as seed_main

    await seed_main()
    yield
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_users():
    """테스트마다 사용자와 분석 캐시를 비운다. 참조 데이터는 seed 로 채운 그대로 둔다."""
    yield
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE app_user RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE analysis_result RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def logged_in(client):
    await client.post(
        "/api/auth/register",
        json={"loginId": "tester", "password": "pw", "displayName": "시험"},
    )
    return client
