from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FeeScheduleDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gateway_name: str
    version_code: str
    txn_type: str
    effective_from: date
    effective_to: date | None
    settlement_currency: str
    percent_rate: Decimal
    fixed_fee: Decimal
    min_fee: Decimal
    fx_markup_bps: int
    failed_attempt_fee: Decimal
    refund_returns_percent_fee: bool
    created_at: datetime
