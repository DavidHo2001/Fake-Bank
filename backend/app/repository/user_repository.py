from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.scalar(statement)

    def find_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def add(self, user: User) -> None:
        self.db.add(user)

    def find_page(self, page: int, page_size: int) -> tuple[list[User], int]:
        total = self.db.scalar(select(func.count()).select_from(User)) or 0
        offset = (page - 1) * page_size
        statement = select(User).order_by(User.id.desc()).limit(page_size).offset(offset)
        return list(self.db.scalars(statement).all()), total