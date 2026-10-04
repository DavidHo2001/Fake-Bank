import httpx
from app.core.config import settings
from app.read_models.chunk_search_result import ChunkSearchResult
from app.core.openrouter_client import get_http_client
class OpenRouterService:
    def __init__(self, http_client: httpx.Client) -> None:
        self.http_client = http_client

    def answer_from_chunks(self, question: str, chunks: list[ChunkSearchResult]) -> str:
        evidence = "\n\n".join(
            f"[{chunk.doc_code} {chunk.version_code} / {chunk.section_path}]\n{chunk.content}"
            for chunk in chunks
        )
        response = self.http_client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
            json={
                "model": settings.openrouter_model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Only answer based on the provided document chunks."
                            "If the chunk does not contain the information, answer \"Unable to confirm\"."
                            "Do not use your own rates."
                            "Reference doc_code and section."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Question: {question}\n\nDocument chunks from vector search: \n{evidence}",
                    },
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        # 有 </think>：只保留之後嘅答案
        # 冇 </think>：保留原本內容
        return content.rsplit("</think>", 1)[-1].strip()