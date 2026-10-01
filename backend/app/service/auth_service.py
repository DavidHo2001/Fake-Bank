from fastapi import HTTPException, status

from app.core.security import create_access_token, verify_password
from app.repository.user_repository import UserRepository
from app.dto.auth_dto import LoginResponse
from app.dto.user_dto import UserDto

class AuthService:
    def __init__(self, user_repository: UserRepository):
        #just like spring @Autowired to inject the dependency
        self.user_repository = user_repository

    def login(self, email: str, password: str) -> LoginResponse:
        if not email or not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")
        user = self.user_repository.find_by_email(email)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        jwt_token = create_access_token(user.id)
        user_dto = UserDto.model_validate(user)
        return LoginResponse(access_token=jwt_token, user_dto=user_dto)