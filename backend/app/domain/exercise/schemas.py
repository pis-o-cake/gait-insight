from pydantic import BaseModel, ConfigDict, Field


class ExerciseOut(BaseModel):
    id: str
    name: str
    purpose: str
    steps: list[str]
    caution: list[str]
    dosage: str
    source: str
    review_status: str = Field(serialization_alias="reviewStatus")
    is_general: bool = Field(serialization_alias="isGeneral")
    model_config = ConfigDict(from_attributes=True)
