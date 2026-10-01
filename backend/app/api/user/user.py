from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_admin
from app.api.user.user_deps import get_user_service
from app.dto.generic import GenericResponse, Page, ok
from app.dto.user_dto import CurrentUser, UserDto, UserListDto
from app.service.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/me", response_model=GenericResponse[UserDto])
def me(current_user: CurrentUser = Depends(get_current_user)) -> GenericResponse[UserDto]:
    return ok(
        UserDto(
            email=current_user.email,
            display_name=current_user.display_name,
            role=current_user.role,
        )
    )


@router.get("", response_model=GenericResponse[Page[UserListDto]])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: CurrentUser = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
) -> GenericResponse[Page[UserListDto]]:
    return ok(user_service.list_users(page, page_size))
