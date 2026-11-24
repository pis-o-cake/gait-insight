"""parquet 기록 로더.

기록 하나는 10분 × 100 Hz 로 6만 행이다. 요청마다 다시 읽지 않도록 캐시한다.
프로세스 메모리에만 두므로 worker 수만큼 중복 적재된다. 기록 수가 적어 감수한다.
"""
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

from app.core.config import get_settings
from app.core.errors import AppError

SENSOR_COLUMNS = [f"l{i}" for i in range(1, 9)] + [f"r{i}" for i in range(1, 9)]
REQUIRED_COLUMNS = ["time", *SENSOR_COLUMNS, "lsum", "rsum"]


class RecordArrays:
    """한 기록의 시계열. 센서는 (n, 8) 배열로 둔다."""

    __slots__ = ("time", "left", "right", "left_sum", "right_sum", "sample_rate")

    def __init__(self, frame: pd.DataFrame, sample_rate: int) -> None:
        self.time = frame["time"].to_numpy(dtype=np.float64)
        self.left = frame[[f"l{i}" for i in range(1, 9)]].to_numpy(dtype=np.float32)
        self.right = frame[[f"r{i}" for i in range(1, 9)]].to_numpy(dtype=np.float32)
        self.left_sum = frame["lsum"].to_numpy(dtype=np.float32)
        self.right_sum = frame["rsum"].to_numpy(dtype=np.float32)
        self.sample_rate = sample_rate

    @property
    def n(self) -> int:
        return int(self.time.size)

    @property
    def dt(self) -> float:
        return 1.0 / self.sample_rate


def resolve(file_path: str) -> Path:
    """기록의 상대 경로를 DATA_DIR 기준 절대 경로로 바꾼다."""
    root = get_settings().data_dir
    path = (root / file_path).resolve() if not Path(file_path).is_absolute() else Path(file_path)
    return path


@lru_cache(maxsize=16)
def load(file_path: str, sample_rate: int) -> RecordArrays:
    path = resolve(file_path)
    if not path.is_file():
        logger.error("record file missing: {}", path)
        raise AppError("record.file_missing")
    frame = pd.read_parquet(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        logger.error("record file has missing columns {} in {}", missing, path)
        raise AppError("record.file_missing")
    return RecordArrays(frame, sample_rate)
