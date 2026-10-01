from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorBody(BaseModel):
    message: str


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class GenericResponse(BaseModel, Generic[T]):
    status: Literal["success", "error"]
    data: T | None = None


def ok(data: T) -> GenericResponse[T]:
    return GenericResponse(status="success", data=data)
