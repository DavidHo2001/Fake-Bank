from app.dto.document_dto import DocumentDto
from app.dto.generic import Page
from app.repository.document_repository import DocumentRepository


class DocumentService:
    def __init__(self, repository: DocumentRepository) -> None:
        self.repository = repository

    def list_documents(self, page: int, page_size: int) -> Page[DocumentDto]:
        rows, total = self.repository.find_page(page, page_size)
        documents: list[DocumentDto] = []
        for document, gateway_name in rows:
            documents.append(
                DocumentDto(
                    doc_code=document.doc_code,
                    gateway_name=gateway_name,
                    doc_type=document.doc_type,
                    version_code=document.version_code,
                    title=document.title,
                    effective_from=document.effective_from,
                    effective_to=document.effective_to,
                    source_path=document.source_path,
                    created_at=document.created_at,
                )
            )
        return Page(items=documents, total=total, page=page, page_size=page_size)
