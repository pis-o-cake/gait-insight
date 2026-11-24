from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.analysis import service
from app.domain.analysis.schemas import Analysis
from app.domain.auth.deps import CurrentUser

router = APIRouter(tags=["analysis"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.get("/{record_id}", response_model=Analysis, summary="기록 분석 결과")
async def get_analysis(record_id: str, user: CurrentUser, session: Session) -> Analysis:
    return await service.analyze(session, record_id)
