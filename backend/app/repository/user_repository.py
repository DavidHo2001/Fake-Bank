from sqlalchemy import select
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