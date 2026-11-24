"""판정 기준 세트와 분석 결과 캐시."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class RuleSet(Base):
    """임계값 묶음. 여러 버전이 공존하고 status='active' 인 하나만 분석에 쓴다."""

    __tablename__ = "rule_set"
    # IMPORTANT: 활성 규칙 세트는 언제나 하나뿐이어야 한다. partial unique index 로 DB 가 보장한다.
    __table_args__ = (
        Index("ix_rule_set_active", "status", unique=True, postgresql_where=text("status = 'active'")),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(32), unique=True)
    status: Mapped[str] = mapped_column(String(16), default="draft")
    thresholds: Mapped[dict] = mapped_column(JSONB)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    links: Mapped[list["LinkRule"]] = relationship(back_populates="rule_set", lazy="selectin")


class LinkRule(Base):
    """보행 유형 -> 운동 프로그램 연결. 해당된 유형마다 링크 하나가 만들어진다."""

    __tablename__ = "link_rule"

    id: Mapped[int] = mapped_column(primary_key=True)
    rule_set_id: Mapped[int] = mapped_column(ForeignKey("rule_set.id", ondelete="CASCADE"), index=True)
    target: Mapped[str] = mapped_column(String(8))
    exercise_ids: Mapped[list] = mapped_column(JSONB)
    reason: Mapped[str] = mapped_column(Text)
    recheck: Mapped[list] = mapped_column(JSONB, default=list)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    rule_set: Mapped[RuleSet] = relationship(back_populates="links")


class AnalysisResult(Base):
    """기록 x 규칙 세트 단위 캐시. 규칙이 바뀌면 새 행이 쌓인다."""

    __tablename__ = "analysis_result"
    __table_args__ = (UniqueConstraint("record_id", "rule_set_id", name="uq_analysis_record_rule"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    record_id: Mapped[str] = mapped_column(ForeignKey("record.id", ondelete="CASCADE"), index=True)
    rule_set_id: Mapped[int] = mapped_column(ForeignKey("rule_set.id", ondelete="CASCADE"), index=True)
    payload: Mapped[dict] = mapped_column(JSONB)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
