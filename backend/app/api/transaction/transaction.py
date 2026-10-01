from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.api.transaction.transaction_deps import get_transaction_service
from app.dto.generic import GenericResponse, Page, ok
from app.dto.transaction_dto import TransactionDto
from app.dto.user_dto import CurrentUser
from app.service.transaction_service import TransactionService

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=GenericResponse[Page[TransactionDto]])
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    occurred_from: date | None = Query(None),
    occurred_to: date | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> GenericResponse[Page[TransactionDto]]:
    return ok(
        transaction_service.list_transactions(
            current_user.id,
            current_user.role,
            page,
            page_size,
            occurred_from,
            occurred_to,
        )
    )
