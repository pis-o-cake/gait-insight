from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.auth.deps import CurrentUser
from app.domain.exercise import service
from app.domain.exercise.schemas import ExerciseOut

router = APIRouter(tags=["exercise"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[ExerciseOut], summary="운동 목록")
async def list_exercises(user: CurrentUser, session: Session) -> list[ExerciseOut]:
    return await service.list_exercises(session)


@router.get("/{exercise_id}", response_model=ExerciseOut, summary="운동 상세")
async def get_exercise(exercise_id: str, user: CurrentUser, session: Session) -> ExerciseOut:
    return await service.get_exercise(session, exercise_id)
