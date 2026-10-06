from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    txn_ref: str
    gateway_name: str
    fee_version_code: str
    owner_display_name: str
    parent_txn_ref: str | None
    settlement_ref: str | None
    txn_type: str
    status: str
    occurred_at: datetime
    gross_amount: Decimal
    gross_currency: str
    settlement_currency: str
    settlement_gross: Decimal
    mid_rate: Decimal
    fx_markup_bps: int
    percent_rate: Decimal
    total_fee: Decimal
    expected_net: Decimal
    settled_amount: Decimal | None
    variance_amount: Decimal | None
    mismatch_flag: bool
    mismatch_code: str | None
