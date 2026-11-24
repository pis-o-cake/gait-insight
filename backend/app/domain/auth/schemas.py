from pydantic import BaseModel, ConfigDict, Field


class DemoAccount(BaseModel):
    """로그인 화면에 보여 줄 시연용 계정."""

    login_id: str = Field(serialization_alias="loginId")
    password: str


class Credentials(BaseModel):
    login_id: str = Field(alias="loginId", min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)
    model_config = ConfigDict(populate_by_name=True)


class RegisterRequest(Credentials):
    display_name: str = Field(alias="displayName", default="", max_length=64)


class User(BaseModel):
    id: int
    login_id: str = Field(serialization_alias="loginId")
    display_name: str = Field(serialization_alias="displayName")
    model_config = ConfigDict(from_attributes=True)
