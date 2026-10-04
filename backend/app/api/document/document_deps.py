import httpx
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repository.document_repository import DocumentRepository
from app.service.document_service import DocumentService

from sentence_transformers import SentenceTransformer
from app.core.embedding import get_embedding_model
from app.core.openrouter_client import get_http_client
from app.service.openrouter_service import OpenRouterService


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