from fastapi import APIRouter, Depends

from app.api.auth.auth_deps import get_auth_service
from app.dto.auth_dto import LoginRequest, LoginResponse
from app.dto.generic import GenericResponse, ok
from app.service.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=GenericResponse[LoginResponse])
def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> GenericResponse[LoginResponse]:
    return ok(auth_service.login(request.email, request.password))