from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, BigInteger, CheckConstraint, Date, DateTime, ForeignKey, Identity, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GatewaySettlement(Base):
    __tablename__ = "gateway_settlement_tb"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    gateway_id: Mapped[int] = mapped_column(ForeignKey("payment_gateway_tb.id"))
    settlement_ref: Mapped[str] = mapped_column(Text, unique=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(CHAR(3))
    settled_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    status: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("period_end >= period_start", name="gateway_settlement_period_chk"),
        CheckConstraint("currency ~ '^[A-Z]{3}$'", name="gateway_settlement_ccy_chk"),
        CheckConstraint("status IN ('open', 'paid')", name="gateway_settlement_status_chk"),
    )