from fastapi import FastAPI

from app.api.auth.auth import router as auth_router
from app.api.fee_schedule.fee_schedule import router as fee_schedule_router
from app.api.user.user import router as user_router

app = FastAPI(title="My API")

app.include_router(user_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(fee_schedule_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
