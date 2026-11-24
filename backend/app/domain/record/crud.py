from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.record.models import Record


async def list_all(session: AsyncSession) -> list[Record]:
    result = await session.execute(select(Record).order_by(Record.sort_order, Record.id))
    return list(result.scalars())


async def get(session: AsyncSession, record_id: str) -> Record | None:
    return await session.get(Record, record_id)
