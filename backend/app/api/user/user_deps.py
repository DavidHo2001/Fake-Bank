from fastapi import Depends
from app.repository.user_repository import UserRepository
from app.db.session import get_db
from sqlalchemy.orm import Session

def get_user_repository(db: Session =Depends(get_db)) -> UserRepository:
    return UserRepository(db)