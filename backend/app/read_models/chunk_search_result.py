from dataclasses import dataclass

@dataclass(frozen=True)
class ChunkSearchResult:
    doc_code: str
    version_code: str
    section_path: str
    content: str
    cosine_similarity: float
