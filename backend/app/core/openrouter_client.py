import httpx

_client: httpx.Client | None = None

def load_http_client() -> None:
    global _client
    _client = httpx.Client(
        base_url="https://openrouter.ai/api/v1",
        timeout=httpx.Timeout(30.0, connect=5.0),
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
    )

def get_http_client() -> httpx.Client:
    if _client is None:
        raise RuntimeError("http client is not loaded")
    return _client

def close_http_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
            