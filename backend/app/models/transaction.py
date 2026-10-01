from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    BigInteger,
    Boolean,
    CheckConstraint,
    Computed,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    Text,
    desc,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transaction_tb"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    txn_ref: Mapped[str] = mapped_column(Text, unique=True)
    gateway_id: Mapped[int] = mapped_column(ForeignKey("payment_gateway_tb.id"))
    fee_schedule_id: Mapped[int] = mapped_column(ForeignKey("fee_schedule_tb.id"))
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("user_tb.id"))
    parent_txn_id: Mapped[int | None] = mapped_column(ForeignKey("transaction_tb.id"))
    settlement_id: Mapped[int | None] = mapped_column(ForeignKey("gateway_settlement_tb.id"))
    txn_type: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    gross_currency: Mapped[str] = mapped_column(CHAR(3))
    settlement_currency: Mapped[str] = mapped_column(CHAR(3))
    settlement_gross: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    mid_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    fx_markup_bps: Mapped[int] = mapped_column(Integer)
    applied_fx_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    fx_markup_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    percent_rate: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    percent_fee: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    fixed_fee: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    min_fee: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    attempt_fee: Mapped[Decimal] = mapped_column(Numeric(19, 4), server_default="0")
    min_fee_applied: Mapped[bool] = mapped_column(Boolean)
    total_fee: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    expected_net: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    settled_amount: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    variance_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        Computed("settled_amount - expected_net", persisted=True),
    )
    mismatch_flag: Mapped[bool] = mapped_column(
        Boolean,
        Computed(
            "settled_amount IS NOT NULL AND settled_amount IS DISTINCT FROM expected_net",
            persisted=True,
        ),
    )
    mismatch_code: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("txn_type IN ('payment', 'refund', 'payout')", name="transaction_type_chk"),
        CheckConstraint("status IN ('pending', 'settled', 'failed')", name="transaction_status_chk"),
        CheckConstraint(
            "gross_currency ~ '^[A-Z]{3}$' AND settlement_currency ~ '^[A-Z]{3}$'",
            name="transaction_ccy_chk",
        ),
        CheckConstraint("gross_amount <> 0", name="transaction_gross_nonzero_chk"),
        CheckConstraint(
            "(txn_type = 'refund' AND parent_txn_id IS NOT NULL) OR (txn_type <> 'refund' AND parent_txn_id IS NULL)",
            name="transaction_refund_parent_chk",
        ),
        CheckConstraint(
            "percent_fee >= 0 AND fixed_fee >= 0 AND min_fee >= 0 AND attempt_fee >= 0 AND total_fee >= 0 AND fx_markup_amount >= 0 AND percent_rate >= 0 AND fx_markup_bps >= 0 AND mid_rate > 0 AND applied_fx_rate > 0",
            name="transaction_money_nonneg_chk",
        ),
        CheckConstraint(
            "total_fee = GREATEST(percent_fee + fixed_fee, min_fee) + attempt_fee",
            name="transaction_total_fee_chk",
        ),
        CheckConstraint("expected_net = settlement_gross - total_fee", name="transaction_expected_net_chk"),
        CheckConstraint(
            "min_fee_applied = ((percent_fee + fixed_fee) < min_fee)",
            name="transaction_min_flag_chk",
        ),
        CheckConstraint(
            "status = 'failed' OR gross_currency <> settlement_currency OR (mid_rate = 1 AND applied_fx_rate = 1 AND fx_markup_bps = 0 AND fx_markup_amount = 0 AND settlement_gross = gross_amount)",
            name="transaction_same_ccy_chk",
        ),
        CheckConstraint(
            "mismatch_code IS NULL OR mismatch_code IN ('short_pay', 'fee_drift', 'fx_rate_drift')",
            name="transaction_mismatch_code_chk",
        ),
        CheckConstraint(
            "(settled_amount IS NULL AND mismatch_code IS NULL) OR (settled_amount IS NOT NULL AND settled_amount = expected_net AND mismatch_code IS NULL) OR (settled_amount IS NOT NULL AND settled_amount <> expected_net AND mismatch_code IS NOT NULL)",
            name="transaction_mismatch_pair_chk",
        ),
        Index("transaction_owner_time_idx", "owner_user_id", desc("occurred_at")),
        Index("transaction_gateway_time_idx", "gateway_id", desc("occurred_at")),
        Index(
            "transaction_mismatch_idx",
            "gateway_id",
            "occurred_at",
            postgresql_where=text("mismatch_flag"),
        ),
    )