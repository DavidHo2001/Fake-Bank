from datetime import date, datetime

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, Identity, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class Document(Base):
    __tablename__ = "document_tb"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    doc_code: Mapped[str] = mapped_column(Text, unique=True)
    gateway_id: Mapped[int | None] = mapped_column(ForeignKey("payment_gateway_tb.id"))
    doc_type: Mapped[str] = mapped_column(Text)
    version_code: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date)
    source_path: Mapped[str] = mapped_column(Text, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "doc_type IN ('fee_schedule', 'fx_rules', 'reconciliation_sop')",
            name="document_type_chk",
        ),
        CheckConstraint("effective_to IS NULL OR effective_to >= effective_from", name="document_dates_chk"),
        CheckConstraint(
            "(doc_type = 'reconciliation_sop' AND gateway_id IS NULL) OR (doc_type <> 'reconciliation_sop' AND gateway_id IS NOT NULL)",
            name="document_gateway_chk",
        ),
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunk_tb"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("document_tb.id"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384))
    section_path: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int | None] = mapped_column(Integer)
    content_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="document_chunk_index_uq"),
        UniqueConstraint("document_id", "content_hash", name="document_chunk_hash_uq"),
        CheckConstraint("chunk_index >= 0", name="document_chunk_index_chk"),
    )