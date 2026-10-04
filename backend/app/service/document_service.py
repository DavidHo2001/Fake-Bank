from datetime import date
from app.core.config import settings
from app.dto.document_dto import DocumentDto
from app.dto.generic import Page
from app.repository.document_repository import DocumentRepository
from app.read_models.chunk_search_result import ChunkSearchResult
from sentence_transformers import SentenceTransformer

class DocumentService:
    def __init__(self, repository: DocumentRepository, embedding_model: SentenceTransformer) -> None:
        self.repository = repository
        self.embedding_model = embedding_model

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
        
    def search_similar_chunks(self, question: str, effective_at: date, limit: int = 5
        ) -> list[ChunkSearchResult]:
        model = self.embedding_model
        question_vector = model.encode([question], normalize_embeddings=True)[0].tolist()
        return self.repository.search_similar_chunks(question_vector, effective_at, limit)