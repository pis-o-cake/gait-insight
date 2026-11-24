from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.auth.deps import CurrentUser
from app.domain.record import service
from app.domain.record.schemas import RecordData, RecordSummary

router = APIRouter(tags=["record"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[RecordSummary], summary="내 보행 기록 목록")
async def list_records(user: CurrentUser, session: Session) -> list[RecordSummary]:
    return await service.list_summaries(session)


@router.get("/{record_id}", response_model=RecordData, summary="기록 본문")
async def get_record(
    record_id: str,
    user: CurrentUser,
    session: Session,
    step: Annotated[int, Query(ge=1, le=100, description="표시용 간격. 1이면 원본 해상도")] = 1,
) -> RecordData:
    return await service.get_data(session, record_id, step)
