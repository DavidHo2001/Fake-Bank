from datetime import date
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk
from app.read_models.chunk_search_result import ChunkSearchResult
from app.models.payment_gateway import PaymentGateway


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_page(self, page: int, page_size: int) -> tuple[list[tuple[Document, str | None]], int]:
        total = self.db.scalar(select(func.count()).select_from(Document)) or 0
        offset = (page - 1) * page_size
        statement = (
            select(Document, PaymentGateway.name)
            .outerjoin(PaymentGateway, Document.gateway_id == PaymentGateway.id)
            .order_by(Document.id.desc())
            .limit(page_size)
            .offset(offset)
        )
        rows = self.db.execute(statement).all()
        return [(document, gateway_name) for document, gateway_name in rows], total

    def search_similar_chunks(
        self,
        question_vector: list[float],
        effective_at: date,
        limit: int = 5,
        gateway_name: str | None = None,
        version_code: str | None = None,
    ) -> list[ChunkSearchResult]:
        distance = DocumentChunk.embedding.cosine_distance(question_vector)
        statement = (
            select(
                Document.doc_code,
                Document.version_code,
                DocumentChunk.section_path,
                DocumentChunk.content,
                (1 - distance).label("cosine_similarity"),
            )
            .join(Document, Document.id == DocumentChunk.document_id)
        )
        filters = [
            DocumentChunk.embedding.is_not(None),
            Document.effective_from <= effective_at,
            (Document.effective_to.is_(None)) | (Document.effective_to >= effective_at),
        ]
        if gateway_name is not None and version_code is not None:
            statement = statement.join(PaymentGateway, Document.gateway_id == PaymentGateway.id)
            filters.extend([
                PaymentGateway.name == gateway_name,
                Document.version_code == version_code,
                Document.doc_type == "fee_schedule",
            ])
        statement = statement.where(*filters).order_by(distance).limit(limit)
        rows = self.db.execute(statement).all()
        return [ChunkSearchResult(
            doc_code=row.doc_code,
            version_code=row.version_code,
            section_path=row.section_path,
            content=row.content,
            cosine_similarity=row.cosine_similarity,
        ) for row in rows]