import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.document import DocumentChunk
from app.models.payment_gateway import PaymentGateway  # noqa: F401

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)
    with SessionLocal() as session:
        chunks = list(
            session.scalars(
                select(DocumentChunk)
                .where(DocumentChunk.embedding.is_(None))
                .order_by(DocumentChunk.id)
            )
        )
        if not chunks:
            print("no empty embeddings")
            return
        vectors = model.encode(
            [chunk.content for chunk in chunks],
            normalize_embeddings=True,
        )
        for chunk, vector in zip(chunks, vectors, strict=True):
            chunk.embedding = vector.tolist()
        session.commit()
        print(f"embedded {len(chunks)} chunks with {MODEL_NAME}, dim {vectors.shape[1]}")


if __name__ == "__main__":
    main()