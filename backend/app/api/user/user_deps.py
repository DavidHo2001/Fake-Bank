from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repository.user_repository import UserRepository
from app.service.user_service import UserService


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository)
