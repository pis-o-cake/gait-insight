"""seed/*.json 을 DB 에 넣는다. 여러 번 실행해도 결과가 같다(upsert).

사용자 계정은 파일에 두지 않는다. 예외로 DEMO_LOGIN_ID·DEMO_PASSWORD 환경 변수가 있으면
시연용 계정 하나를 만들고, 매번 그 비밀번호로 되돌린다. 나머지 계정은 가입 API 로 만든다.
"""
import asyncio
import json
import pathlib
import sys
from datetime import datetime

from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.core.config import get_settings  # noqa: E402
from app.core.db import SessionFactory  # noqa: E402
from app.domain.analysis.models import AnalysisResult, LinkRule, RuleSet  # noqa: E402
from app.domain.auth.models import AppUser  # noqa: E402
from app.domain.auth.security import hash_password  # noqa: E402
from app.domain.exercise.models import Exercise  # noqa: E402
from app.domain.record.models import Record  # noqa: E402

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
SEED = DATA / "seed"


def _load(name: str):
    return json.loads((SEED / name).read_text(encoding="utf-8"))


async def _seed_records(session) -> int:
    rows = []
    for item in _load("records.json"):
        item = {k: v for k, v in item.items() if k != "synth"}
        if item.get("measured_at"):
            item["measured_at"] = datetime.fromisoformat(item["measured_at"])
        path = DATA / item["file_path"]
        if not path.is_file():
            logger.warning("record file not found, skipping: {}", path)
            continue
        rows.append(item)
    if not rows:
        return 0
    stmt = insert(Record).values(rows)
    await session.execute(
        stmt.on_conflict_do_update(
            index_elements=[Record.id],
            set_={c: stmt.excluded[c] for c in rows[0] if c != "id"},
        )
    )
    return len(rows)


async def _seed_exercises(session) -> int:
    rows = _load("exercises.json")
    stmt = insert(Exercise).values(rows)
    await session.execute(
        stmt.on_conflict_do_update(
            index_elements=[Exercise.id],
            set_={c: stmt.excluded[c] for c in rows[0] if c != "id"},
        )
    )
    return len(rows)


async def _seed_rule_set(session) -> str:
    payload = _load("rule_set.json")
    known = {e["id"] for e in _load("exercises.json")}
    for link in payload["links"]:
        unknown = [e for e in link["exercise_ids"] if e not in known]
        if unknown:
            raise ValueError(f"link rule {link['target']} points at unknown exercises: {unknown}")

    existing = (
        await session.execute(select(RuleSet).where(RuleSet.version == payload["version"]))
    ).scalar_one_or_none()

    if existing is None:
        rule_set = RuleSet(
            version=payload["version"], status="draft",
            thresholds=payload["thresholds"], note=payload.get("note", ""),
        )
        session.add(rule_set)
        await session.flush()
    else:
        rule_set = existing
        rule_set.thresholds = payload["thresholds"]
        rule_set.note = payload.get("note", "")
        await session.execute(delete(LinkRule).where(LinkRule.rule_set_id == rule_set.id))
        # 기준이 바뀌면 이 세트로 계산해 둔 캐시는 더 이상 맞지 않는다.
        await session.execute(delete(AnalysisResult).where(AnalysisResult.rule_set_id == rule_set.id))

    session.add_all(
        LinkRule(rule_set_id=rule_set.id, target=l["target"], exercise_ids=l["exercise_ids"],
                 reason=l["reason"], recheck=l.get("recheck", []), sort_order=l.get("sort_order", 0))
        for l in payload["links"]
    )

    if payload.get("status") == "active":
        # 활성 세트는 하나뿐이다(partial unique index). 먼저 기존 활성을 내린다.
        await session.execute(
            RuleSet.__table__.update().where(RuleSet.status == "active", RuleSet.id != rule_set.id)
            .values(status="retired")
        )
        await session.flush()
        rule_set.status = "active"
    return f"{rule_set.version}({rule_set.status})"


async def _seed_demo_user(session) -> str:
    settings = get_settings()
    if not settings.demo_enabled:
        return "-"
    user = (
        await session.execute(select(AppUser).where(AppUser.login_id == settings.demo_login_id))
    ).scalar_one_or_none()
    password_hash = hash_password(settings.demo_password)
    display_name = settings.demo_display_name or settings.demo_login_id
    if user is None:
        session.add(AppUser(login_id=settings.demo_login_id, password_hash=password_hash, display_name=display_name))
    else:
        # 누가 비밀번호를 바꿔도 시연 직전 seed 로 화면에 적힌 값과 다시 맞춘다.
        user.password_hash = password_hash
        user.display_name = display_name
    return settings.demo_login_id


async def main() -> None:
    get_settings()
    async with SessionFactory() as session:
        records = await _seed_records(session)
        exercises = await _seed_exercises(session)
        rule_set = await _seed_rule_set(session)
        demo_user = await _seed_demo_user(session)
        await session.commit()
    logger.info("seeded records={} exercises={} rule_set={} demo_user={}", records, exercises, rule_set, demo_user)
    print(f"seeded: records={records} exercises={exercises} rule_set={rule_set} demo_user={demo_user}")


if __name__ == "__main__":
    asyncio.run(main())
