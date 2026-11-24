"""운동 콘텐츠. review_status 로 시연안과 학과 검토본을 구분한다."""
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Exercise(Base):
    __tablename__ = "exercise"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    purpose: Mapped[str] = mapped_column(Text)
    steps: Mapped[list] = mapped_column(JSONB)
    caution: Mapped[list] = mapped_column(JSONB)
    # 전문가 자료의 운동량 예시. 개인별로 검증된 처방값이 아니다.
    dosage: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(Text, default="")
    review_status: Mapped[str] = mapped_column(String(16), default="demo")
    is_general: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
