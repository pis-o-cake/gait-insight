from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.domain.exercise import crud
from app.domain.exercise.schemas import ExerciseOut


async def list_exercises(session: AsyncSession) -> list[ExerciseOut]:
    return [ExerciseOut.model_validate(e) for e in await crud.list_all(session)]


async def get_exercise(session: AsyncSession, exercise_id: str) -> ExerciseOut:
    exercise = await crud.get(session, exercise_id)
    if exercise is None:
        raise NotFoundError("exercise.not_found")
    return ExerciseOut.model_validate(exercise)
