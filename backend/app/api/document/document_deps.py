from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repository.document_repository import DocumentRepository
from app.service.document_service import DocumentService


def get_document_repository(db: Session = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db)


def get_document_service(
    repository: DocumentRepository = Depends(get_document_repository),
) -> DocumentService:
    return DocumentService(repository)
