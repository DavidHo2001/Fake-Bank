from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CurrentUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str
    role: str


class UserDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    display_name: str
    role: str


class UserListDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str
    role: str
    is_active: bool
    created_at: datetime
