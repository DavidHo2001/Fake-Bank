from sentence_transformers import SentenceTransformer

from app.core.config import settings

_model: SentenceTransformer | None = None


def load_embedding_model() -> None:
    global _model
    _model = SentenceTransformer(settings.embedding_model_name)


def get_embedding_model() -> SentenceTransformer:
    if _model is None:
        raise RuntimeError("embedding model is not loaded")
    return _model