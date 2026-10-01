from fastapi import APIRouter, Depends

from app.api.auth.auth_deps import get_auth_service
from app.service.auth_service import AuthService
from app.dto.auth_dto import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest,
          auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    return auth_service.login(request.email, request.password)