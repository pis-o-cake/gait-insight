"""기록 메타. 센서 시계열은 file_path 가 가리키는 parquet 에 있다."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Record(Base):
    __tablename__ = "record"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    participant_code: Mapped[str] = mapped_column(String(64), default="")
    condition: Mapped[str] = mapped_column(String(32), default="normal")
    measured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_sec: Mapped[float] = mapped_column(Numeric(10, 3))
    sample_rate: Mapped[int] = mapped_column(Integer, default=100)
    source: Mapped[str] = mapped_column(String(64), default="synthetic")
    license: Mapped[str] = mapped_column(String(64), default="")
    file_path: Mapped[str] = mapped_column(String(256))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    # 인솔로 잴 수 없는 보장·보행 속도. 영상·보행 매트·10m 보행검사 결과를 함께 넣어 둔다.
    walk_test: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
