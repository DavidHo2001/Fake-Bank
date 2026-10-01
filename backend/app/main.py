from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth.auth import router as auth_router
from app.api.document.document import router as document_router
from app.api.fee_schedule.fee_schedule import router as fee_schedule_router
from app.api.transaction.transaction import router as transaction_router
from app.api.user.user import router as user_router

app = FastAPI(title="David Bank")

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
