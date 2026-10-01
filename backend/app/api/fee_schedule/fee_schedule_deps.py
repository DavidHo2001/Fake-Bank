from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repository.fee_schedule_repository import FeeScheduleRepository
from app.service.fee_schedule_service import FeeScheduleService


def get_fee_schedule_repository(db: Session = Depends(get_db)) -> FeeScheduleRepository:
    return FeeScheduleRepository(db)


def get_fee_schedule_service(
    repository: FeeScheduleRepository = Depends(get_fee_schedule_repository),
) -> FeeScheduleService:
    return FeeScheduleService(repository)
