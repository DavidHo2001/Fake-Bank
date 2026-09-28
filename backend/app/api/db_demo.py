from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db


router = APIRouter()


@router.get("/db-check")
def db_check(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(text("SELECT 1")).scalar_one()
    return {"database": "connected", "result": result}
