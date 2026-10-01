from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.dto.user_dto import UserDto

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)] #All sub path check jwt header
)


@router.get("/me", response_model=UserDto)
def me(current_user: UserDto = Depends(get_current_user)) -> UserDto:
    return current_user
