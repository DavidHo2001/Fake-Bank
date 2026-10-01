from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from app.core.security import ALGORITHM
from app.dto.user_dto import UserDto
from app.repository.user_repository import UserRepository
from app.api.user.user_deps import get_user_repository

bearer = HTTPBearer(auto_error=True)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserDto:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = user_repository.find_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token" if user is None else "User is not active"
        )
    return UserDto.model_validate(user)