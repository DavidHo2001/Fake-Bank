import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from datetime import date
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.document import Document, DocumentChunk

from sentence_transformers import SentenceTransformer
import json

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

"""
This script generates a question embedding for testing vector search.
Paste the result of your question vector into the query_vec parameter.

SQL:
SELECT d.doc_code, d.version_code, c.section_path,
       1 - (c.embedding <=> :query_vec) AS cosine_similarity
FROM document_chunk_tb c
JOIN document_tb d ON d.id = c.document_id
WHERE c.embedding IS NOT NULL
  AND d.effective_from <= DATE '2026-03-15'
  AND (d.effective_to IS NULL OR d.effective_to >= DATE '2026-03-15')
ORDER BY c.embedding <=> :query_vec
LIMIT 5;
"""

def test_find_vector() -> None:
    model = SentenceTransformer(MODEL_NAME)
    question = "NorthstarPay 喺 2026-03-15 嘅收單費率、固定費、最低費係幾多？"
    query = model.encode([question], normalize_embeddings=True)[0]

    # 輸出帶單引號的向量字串，方便貼入 DBeaver
    print("'" + json.dumps(query.tolist()) + "'")


"""
The actual vector search with SQLAlchemy.
"""

def search(question: str, hk_date: date, limit: int = 5) -> None:
    model = SentenceTransformer(MODEL_NAME)
    query = model.encode([question], normalize_embeddings=True)[0].tolist()
    distance = DocumentChunk.embedding.cosine_distance(query)
    statement = (
        select(
            Document.doc_code,
            Document.version_code,
            DocumentChunk.section_path,
            DocumentChunk.content,
            (1 - distance).label("cosine_similarity"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(
            DocumentChunk.embedding.is_not(None),
            Document.effective_from <= hk_date,
            (Document.effective_to.is_(None)) | (Document.effective_to >= hk_date),
        )
        .order_by(distance)
        .limit(limit)
    )
    with SessionLocal() as session:
        for row in session.execute(statement):
            print(f"{row.cosine_similarity:.3f}  {row.doc_code}  {row.version_code}  {row.section_path}")
            print("document content:", row.content)


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)
    question = "NorthstarPay 嘅收單費率、固定費、最低費係幾多？"
    search(question, date(2026, 3, 15))
    search(question, date(2026, 4, 2))

if __name__ == "__main__":
    main()