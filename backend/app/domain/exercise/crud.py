from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exercise.models import Exercise


async def list_all(session: AsyncSession) -> list[Exercise]:
    result = await session.execute(select(Exercise).order_by(Exercise.sort_order, Exercise.id))
    return list(result.scalars())


async def get(session: AsyncSession, exercise_id: str) -> Exercise | None:
    return await session.get(Exercise, exercise_id)
