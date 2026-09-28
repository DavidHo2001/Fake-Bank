from fastapi import FastAPI

from app.api.users import router as users_router
from app.api.db_demo import router as db_demo_router

app = FastAPI(title="My API")

app.include_router(users_router, prefix="/api/v1")
app.include_router(db_demo_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
