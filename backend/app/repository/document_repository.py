from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document
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
