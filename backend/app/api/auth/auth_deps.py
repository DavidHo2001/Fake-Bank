from fastapi import Depends
from app.repository.user_repository import UserRepository
from app.service.auth_service import AuthService
from app.api.user.user_deps import get_user_repository

def get_auth_service(user_repository: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repository)