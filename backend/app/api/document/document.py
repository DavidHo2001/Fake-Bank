from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.api.document.document_deps import get_document_service
from app.dto.document_dto import DocumentDto
from app.dto.generic import GenericResponse, Page, ok
from app.service.document_service import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=GenericResponse[Page[DocumentDto]])
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    document_service: DocumentService = Depends(get_document_service),
) -> GenericResponse[Page[DocumentDto]]:
    return ok(document_service.list_documents(page, page_size))
