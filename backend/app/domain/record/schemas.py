from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecordSummary(BaseModel):
    id: str
    name: str
    condition: str
    measured_at: datetime | None = Field(default=None, serialization_alias="measuredAt")
    duration_sec: float = Field(serialization_alias="durationSec")
    sample_rate: int = Field(serialization_alias="sampleRate")
    source: str
    license: str
    is_demo: bool = Field(serialization_alias="isDemo")
    preview: dict[str, list[float]] | None = None
    model_config = ConfigDict(from_attributes=True)


class SensorPosition(BaseModel):
    x: float
    y: float


class RecordData(BaseModel):
    id: str
    unit: str = "N"
    sample_rate: int = Field(serialization_alias="sampleRate")
    step: int
    time: list[float]
    left: list[list[float]]
    right: list[list[float]]
    left_sum: list[float] = Field(serialization_alias="leftSum")
    right_sum: list[float] = Field(serialization_alias="rightSum")
    sensor_left: list[SensorPosition] = Field(serialization_alias="sensorLeft")
    sensor_right: list[SensorPosition] = Field(serialization_alias="sensorRight")
