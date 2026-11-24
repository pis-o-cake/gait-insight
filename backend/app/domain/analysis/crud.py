from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.analysis.models import AnalysisResult, RuleSet


async def active_rule_set(session: AsyncSession) -> RuleSet | None:
    result = await session.execute(select(RuleSet).where(RuleSet.status == "active"))
    return result.scalar_one_or_none()


async def get_cached(session: AsyncSession, record_id: str, rule_set_id: int) -> AnalysisResult | None:
    result = await session.execute(
        select(AnalysisResult).where(
            AnalysisResult.record_id == record_id, AnalysisResult.rule_set_id == rule_set_id
        )
    )
    return result.scalar_one_or_none()


async def save(session: AsyncSession, record_id: str, rule_set_id: int, payload: dict) -> AnalysisResult:
    row = AnalysisResult(record_id=record_id, rule_set_id=rule_set_id, payload=payload)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row
