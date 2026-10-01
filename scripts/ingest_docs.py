"""Split docs/source Markdown into document_chunk_tb. No LLM and no embeddings.

document_tb is the catalog. source_path says which file to open.
Each ## section becomes one chunk. Version and dates stay on document_tb;
search joins them back through document_id.

Re-running deletes that document's chunks and inserts them again.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.document import Document, DocumentChunk
from app.models.payment_gateway import PaymentGateway  # noqa: F401


def split_sections(markdown: str) -> list[tuple[str, str]]:
    """Return (heading, body) for each ## section. YAML front matter is not a chunk."""
    lines = markdown.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                start = index + 1
                break

    title = ""
    sections: list[tuple[str, str]] = []
    heading = ""
    body: list[str] = []

    def flush() -> None:
        if not heading:
            return
        text = "\n".join(body).strip()
        content = f"# {title}\n\n## {heading}\n\n{text}" if title else f"## {heading}\n\n{text}"
        sections.append((heading, content))

    for line in lines[start:]:
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            flush()
            heading = line[3:].strip()
            body = []
            continue
        if heading:
            body.append(line)
    flush()
    return sections


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def main() -> None:
    with SessionLocal() as session:
        documents = list(session.scalars(select(Document).order_by(Document.doc_code)))
        if not documents:
            raise SystemExit("document_tb is empty. Run the reference seed first.")

        session.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id.in_([document.id for document in documents])
            )
        )

        written = 0
        for document in documents:
            path = ROOT / document.source_path
            if not path.is_file():
                raise SystemExit(f"Missing file for {document.doc_code}: {document.source_path}")
            sections = split_sections(path.read_text(encoding="utf-8"))
            if not sections:
                raise SystemExit(f"No ## sections in {document.source_path}")
            for index, (heading, content) in enumerate(sections):
                session.add(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=index,
                        section_path=heading,
                        content=content,
                        token_count=len(content.split()),
                        content_hash=content_hash(content),
                    )
                )
            written += len(sections)
            print(f"{document.doc_code}  {len(sections)} chunks  {document.source_path}")

        session.commit()
        print(f"ingested {written} chunks from {len(documents)} documents")


if __name__ == "__main__":
    main()
