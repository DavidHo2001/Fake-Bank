from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repository.transaction_repository import TransactionRepository
from app.service.transaction_service import TransactionService


def get_transaction_repository(db: Session = Depends(get_db)) -> TransactionRepository:
    return TransactionRepository(db)


def get_transaction_service(
    repository: TransactionRepository = Depends(get_transaction_repository),
) -> TransactionService:
    return TransactionService(repository)
