"""기록 조회와 표시용 변환."""
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import io
from app.core.errors import NotFoundError
from app.domain.record import crud
from app.domain.record.models import Record
from app.domain.record.schemas import RecordData, RecordSummary, SensorPosition

# PhysioNet format.txt 의 왼발 센서 상대 좌표(mm). 오른발은 X 부호를 뒤집는다.
SENSOR_LEFT = [(-500, -800), (-700, -400), (-300, -400), (-700, 0), (-300, 0), (-700, 400), (-300, 400), (-500, 800)]
SENSOR_RIGHT = [(-x, y) for x, y in SENSOR_LEFT]
PREVIEW_SECONDS = 6
PREVIEW_POINTS = 60


async def list_summaries(session: AsyncSession) -> list[RecordSummary]:
    records = await crud.list_all(session)
    out: list[RecordSummary] = []
    for record in records:
        summary = RecordSummary.model_validate(record)
        summary.preview = _preview(record)
        out.append(summary)
    return out


def _preview(record: Record) -> dict[str, list[float]]:
    """목록의 스파크라인용 앞 6초 요약."""
    arrays = io.load(record.file_path, record.sample_rate)
    count = min(arrays.n, PREVIEW_SECONDS * record.sample_rate)
    step = max(1, count // PREVIEW_POINTS)
    idx = np.arange(0, count, step)
    return {
        "left": [round(float(v), 1) for v in arrays.left_sum[idx]],
        "right": [round(float(v), 1) for v in arrays.right_sum[idx]],
    }


async def get_data(session: AsyncSession, record_id: str, step: int) -> RecordData:
    record = await crud.get(session, record_id)
    if record is None:
        raise NotFoundError("record.not_found")
    arrays = io.load(record.file_path, record.sample_rate)
    step = max(1, min(step, 100))
    idx = np.arange(0, arrays.n, step)
    return RecordData(
        id=record.id,
        sample_rate=record.sample_rate,
        step=step,
        time=[round(float(v), 3) for v in arrays.time[idx]],
        left=[[round(float(v), 1) for v in row] for row in arrays.left[idx]],
        right=[[round(float(v), 1) for v in row] for row in arrays.right[idx]],
        left_sum=[round(float(v), 1) for v in arrays.left_sum[idx]],
        right_sum=[round(float(v), 1) for v in arrays.right_sum[idx]],
        sensor_left=[SensorPosition(x=x, y=y) for x, y in SENSOR_LEFT],
        sensor_right=[SensorPosition(x=x, y=y) for x, y in SENSOR_RIGHT],
    )
