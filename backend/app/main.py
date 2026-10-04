from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.embedding import load_embedding_model
from app.core.openrouter_client import load_http_client, close_http_client
from app.api.auth.auth import router as auth_router
from app.api.document.document import router as document_router
from app.api.fee_schedule.fee_schedule import router as fee_schedule_router
from app.api.transaction.transaction import router as transaction_router
from app.api.user.user import router as user_router
from app.db.session import engine

@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        load_embedding_model()
        load_http_client()
        yield
    finally:
        engine.dispose()
        close_http_client()


app = FastAPI(title="David Bank", version="1.0.0", docs_url=None, redoc_url=None, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(fee_schedule_router, prefix="/api/v1")
app.include_router(document_router, prefix="/api/v1")
app.include_router(transaction_router, prefix="/api/v1")


@app.exception_handler(HTTPException)
async def http_exception_handler(_request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "data": {"message": message}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, _exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"status": "error", "data": {"message": "Invalid request"}},
    )


@app.get("/health")
def health():
    return {"status": "ok"}
