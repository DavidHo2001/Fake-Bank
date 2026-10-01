from app.dto.generic import Page
from app.dto.user_dto import UserListDto
from app.repository.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def list_users(self, page: int, page_size: int) -> Page[UserListDto]:
        rows, total = self.repository.find_page(page, page_size)
        users: list[UserListDto] = []
        for user in rows:
            users.append(
                UserListDto(
                    id=user.id,
                    email=user.email,
                    display_name=user.display_name,
                    role=user.role,
                    is_active=user.is_active,
                    created_at=user.created_at,
                )
            )
        return Page(items=users, total=total, page=page, page_size=page_size)
