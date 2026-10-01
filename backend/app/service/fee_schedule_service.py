from app.dto.fee_schedule_dto import FeeScheduleDto, FeeSchedulePage
from app.repository.fee_schedule_repository import FeeScheduleRepository


class FeeScheduleService:
    def __init__(self, repository: FeeScheduleRepository) -> None:
        self.repository = repository

    def list_schedules(self, page: int, page_size: int) -> FeeSchedulePage:
        rows, total = self.repository.find_all_with_gateway_name(page, page_size)
        schedules: list[FeeScheduleDto] = []
        for schedule, gateway_name in rows:
            schedules.append(
                FeeScheduleDto(
                    id=schedule.id,
                    gateway_id=schedule.gateway_id,
                    gateway_name=gateway_name,
                    version_code=schedule.version_code,
                    txn_type=schedule.txn_type,
                    effective_from=schedule.effective_from,
                    effective_to=schedule.effective_to,
                    settlement_currency=schedule.settlement_currency,
                    percent_rate=schedule.percent_rate,
                    fixed_fee=schedule.fixed_fee,
                    min_fee=schedule.min_fee,
                    fx_markup_bps=schedule.fx_markup_bps,
                    failed_attempt_fee=schedule.failed_attempt_fee,
                    refund_returns_percent_fee=schedule.refund_returns_percent_fee,
                    created_at=schedule.created_at,
                )
            )
            
        return FeeSchedulePage(
            data=schedules,
            total=total,
            page=page,
            page_size=page_size,
        )
