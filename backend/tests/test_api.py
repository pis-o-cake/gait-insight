"""API 계약 검증. 인증 가드와 오류 코드를 확인한다."""
import pytest

PROTECTED = ["/api/record", "/api/record/demo-01", "/api/analysis/demo-01", "/api/exercise", "/api/exercise/EX01"]


@pytest.mark.parametrize("path", PROTECTED)
async def test_requires_login(client, path):
    response = await client.get(path)
    assert response.status_code == 401
    assert response.json()["code"] == "auth.required"


async def test_register_then_use(client):
    created = await client.post("/api/auth/register", json={"loginId": "u1", "password": "x", "displayName": "사용자"})
    assert created.status_code == 200
    assert created.json()["loginId"] == "u1"
    assert (await client.get("/api/auth/me")).status_code == 200


async def test_duplicate_login_id_conflicts(client):
    await client.post("/api/auth/register", json={"loginId": "dup", "password": "x"})
    again = await client.post("/api/auth/register", json={"loginId": "dup", "password": "y"})
    assert again.status_code == 409
    assert again.json()["code"] == "auth.login_id_taken"


async def test_wrong_password_is_rejected(client):
    await client.post("/api/auth/register", json={"loginId": "u2", "password": "right"})
    await client.post("/api/auth/logout")
    bad = await client.post("/api/auth/login", json={"loginId": "u2", "password": "wrong"})
    assert bad.status_code == 401
    assert bad.json()["code"] == "auth.invalid_credentials"


async def test_unknown_login_id_gives_same_error(client):
    """계정 존재 여부를 흘리지 않는다."""
    response = await client.post("/api/auth/login", json={"loginId": "nobody", "password": "x"})
    assert response.json()["code"] == "auth.invalid_credentials"


async def test_demo_account_matches_settings_and_logs_in(client):
    """DEMO_* 가 있으면 그 계정을 보여 주고 seed 후 로그인되며, 없으면 null 이다."""
    from app.core.config import get_settings
    from app.core.db import SessionFactory
    from tools.seed import _seed_demo_user

    settings = get_settings()
    body = (await client.get("/api/auth/demo-account")).json()
    if not settings.demo_enabled:
        assert body is None
        return
    assert body == {"loginId": settings.demo_login_id, "password": settings.demo_password}

    async with SessionFactory() as session:
        await _seed_demo_user(session)
        await session.commit()
    login = await client.post("/api/auth/login", json={"loginId": body["loginId"], "password": body["password"]})
    assert login.status_code == 200


async def test_logout_clears_session(logged_in):
    await logged_in.post("/api/auth/logout")
    assert (await logged_in.get("/api/auth/me")).status_code == 401


async def test_record_list_and_body(logged_in):
    records = (await logged_in.get("/api/record")).json()
    assert len(records) >= 1
    first = records[0]
    assert first["preview"]["left"] and first["preview"]["right"]

    body = (await logged_in.get(f"/api/record/{first['id']}", params={"step": 50})).json()
    assert len(body["time"]) == len(body["leftSum"]) == len(body["rightSum"])
    assert len(body["left"]) == len(body["time"])
    assert body["unit"] == "N"


async def test_missing_record_is_404(logged_in):
    response = await logged_in.get("/api/record/does-not-exist")
    assert response.status_code == 404
    assert response.json()["code"] == "record.not_found"


async def test_analysis_shape_and_cache(logged_in):
    first = (await logged_in.get("/api/analysis/demo-01")).json()
    assert set(first["metrics"]) == {f"M{i:02d}" for i in range(1, 11)}
    assert first["ruleSetVersion"] == "expert-1"
    assert first["window"]["to"] > first["window"]["from"]
    assert first["staticWindow"]["to"] < first["window"]["from"]
    assert [link["target"] for link in first["links"]] == ["T1"]
    for link in first["links"]:
        assert link["exerciseIds"] and link["reason"] and link["evidence"] and link["recheck"]

    second = (await logged_in.get("/api/analysis/demo-01")).json()
    assert second["computedAt"] is not None, "두 번째 호출은 캐시에서 와야 한다"
    assert second["metrics"] == first["metrics"]


async def test_exercise_detail(logged_in):
    exercise = (await logged_in.get("/api/exercise/EX01")).json()
    assert exercise["steps"] and exercise["caution"]
    assert exercise["reviewStatus"] == "expert"
    assert exercise["dosage"]
    assert (await logged_in.get("/api/exercise/NOPE")).status_code == 404
