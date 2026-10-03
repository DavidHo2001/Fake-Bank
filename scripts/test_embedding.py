import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

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


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)
    question = "NorthstarPay 喺 2026-03-15 嘅收單費率、固定費、最低費係幾多？"
    query = model.encode([question], normalize_embeddings=True)[0]

    # 輸出帶單引號的向量字串，方便貼入 DBeaver
    print("'" + json.dumps(query.tolist()) + "'")

if __name__ == "__main__":
    main()