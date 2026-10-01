from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.fee_schedule import FeeSchedule
from app.models.payment_gateway import PaymentGateway


class FeeScheduleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all_with_gateway_name(self, page: int, page_size: int
    )-> tuple[list[tuple[FeeSchedule, str]], int]:
    
        total = self.db.scalar(select(func.count()).select_from(FeeSchedule)) or 0
        offset = (page - 1) * page_size

        statement = (
            select(FeeSchedule, PaymentGateway.name)
            .join(PaymentGateway, FeeSchedule.gateway_id == PaymentGateway.id)
            .order_by(FeeSchedule.id.desc()).limit(page_size).offset(offset)
        )
        rows = self.db.execute(statement).all()
        return [(schedule, gateway_name) for schedule, gateway_name in rows], total