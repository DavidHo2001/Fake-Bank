from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.api.fee_schedule.fee_schedule_deps import get_fee_schedule_service
from app.dto.fee_schedule_dto import FeeScheduleDto
from app.dto.generic import GenericResponse, Page, ok
from app.service.fee_schedule_service import FeeScheduleService

router = APIRouter(
    prefix="/fee-schedules",
    tags=["fee-schedules"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=GenericResponse[Page[FeeScheduleDto]])
def list_fee_schedules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    fee_schedule_service: FeeScheduleService = Depends(get_fee_schedule_service),
) -> GenericResponse[Page[FeeScheduleDto]]:
    return ok(fee_schedule_service.list_schedules(page, page_size))
