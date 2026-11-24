from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MetricOut(BaseModel):
    left: float | None = None
    right: float | None = None
    unit: str
    ok: bool
    value: float | None = None
    diff_pct: float | None = Field(default=None, serialization_alias="diffPct")
    reason: str | None = None
    extra: dict = Field(default_factory=dict)
    model_config = ConfigDict(populate_by_name=True)


class WindowOut(BaseModel):
    from_sec: float = Field(serialization_alias="from")
    to_sec: float = Field(serialization_alias="to")
    model_config = ConfigDict(populate_by_name=True)


class Observation(BaseModel):
    metric: str
    hit: bool
    status: str
    head: str
    text: str


class LinkOut(BaseModel):
    """해당된 보행 유형 하나와 그 운동 프로그램."""

    target: str
    head: str
    observation: str
    evidence: list[str]
    reason: str
    exercise_ids: list[str] = Field(serialization_alias="exerciseIds")
    recheck: list[str]
    model_config = ConfigDict(populate_by_name=True)


class Analysis(BaseModel):
    record_id: str = Field(serialization_alias="recordId")
    window: WindowOut
    static_window: WindowOut | None = Field(default=None, serialization_alias="staticWindow")
    metrics: dict[str, MetricOut]
    observations: list[Observation]
    links: list[LinkOut]
    watch: list[Observation]
    summary: str
    rule_set_version: str = Field(serialization_alias="ruleSetVersion")
    rule_set_status: str = Field(serialization_alias="ruleSetStatus")
    computed_at: datetime | None = Field(default=None, serialization_alias="computedAt")
    model_config = ConfigDict(populate_by_name=True)
