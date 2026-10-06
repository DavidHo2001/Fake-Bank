import httpx
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repository.document_repository import DocumentRepository
from app.service.document_service import DocumentService

from sentence_transformers import SentenceTransformer
from app.core.embedding import get_embedding_model
from app.core.openrouter_client import get_http_client
from app.service.answer_service import AnswerService
from app.service.openrouter_service import OpenRouterService
from app.service.transaction_service import TransactionService
from app.api.transaction.transaction_deps import get_transaction_service


def get_document_repository(db: Session = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db)


def get_document_service(
    repository: DocumentRepository = Depends(get_document_repository),
    embedding_model: SentenceTransformer = Depends(get_embedding_model),
) -> DocumentService:
    return DocumentService(repository, embedding_model)

def get_openrouter_service(
    http_client: httpx.Client = Depends(get_http_client),
) -> OpenRouterService:
    return OpenRouterService(http_client)


def get_answer_service(
    document_service: DocumentService = Depends(get_document_service),
    transaction_service: TransactionService = Depends(get_transaction_service),
    openrouter_service: OpenRouterService = Depends(get_openrouter_service),
) -> AnswerService:
    return AnswerService(document_service, transaction_service, openrouter_service)