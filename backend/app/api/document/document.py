from datetime import date
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Form

from app.api.deps import get_current_user
from app.api.document.document_deps import get_answer_service, get_document_service
from app.dto.document_dto import DocumentDto, QuestionRequest
from app.dto.user_dto import CurrentUser
from app.dto.generic import GenericResponse, Page, ok
from app.read_models.chunk_search_result import ChunkSearchResult
from app.service.answer_service import AnswerService
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

#Test endpoint for searching similar chunks
@router.post("/search", response_model=GenericResponse[list[ChunkSearchResult]])
def search_similar_chunks(
    question: Annotated[str, Form()],
    effective_at: Annotated[date, Form()],
    document_service: DocumentService = Depends(get_document_service),
) -> GenericResponse[list[ChunkSearchResult]]:
    return ok(document_service.search_similar_chunks(question, [effective_at]))

#RAG endpoint for answering questions
@router.post("/answer", response_model=GenericResponse[str])
def answer(
    request: QuestionRequest,
    answer_service: AnswerService = Depends(get_answer_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> GenericResponse[str]:
    return ok(answer_service.answer(request.question, request.effective_at, current_user))