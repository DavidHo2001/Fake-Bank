from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FeeSchedule(Base):
    __tablename__ = "fee_schedule_tb"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    gateway_id: Mapped[int] = mapped_column(ForeignKey("payment_gateway_tb.id"))
    version_code: Mapped[str] = mapped_column(Text)
    txn_type: Mapped[str] = mapped_column(Text)
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date)
    settlement_currency: Mapped[str] = mapped_column(CHAR(3))
    percent_rate: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    fixed_fee: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    min_fee: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    fx_markup_bps: Mapped[int] = mapped_column(Integer)
    failed_attempt_fee: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    refund_returns_percent_fee: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("gateway_id", "version_code", "txn_type", name="fee_schedule_version_txn_uq"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="fee_schedule_dates_chk",
        ),
        CheckConstraint("percent_rate >= 0 AND percent_rate < 1", name="fee_schedule_percent_chk"),
        CheckConstraint(
            "fixed_fee >= 0 AND min_fee >= 0 AND failed_attempt_fee >= 0",
            name="fee_schedule_money_chk",
        ),
        CheckConstraint("fx_markup_bps BETWEEN 0 AND 1000", name="fee_schedule_bps_chk"),
        CheckConstraint("txn_type IN ('payment', 'refund', 'payout')", name="fee_schedule_type_chk"),
        CheckConstraint("settlement_currency ~ '^[A-Z]{3}$'", name="fee_schedule_ccy_chk"),
        Index("fee_schedule_lookup_idx", "gateway_id", "txn_type", "effective_from"),
    )