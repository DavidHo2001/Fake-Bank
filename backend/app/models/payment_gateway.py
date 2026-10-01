from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Boolean, CheckConstraint, DateTime, Identity, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class PaymentGateway(Base):
    __tablename__ = "payment_gateway_tb"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    settlement_currency: Mapped[str] = mapped_column(CHAR(3))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint("code ~ '^[A-Z0-9]{2,12}$'", name="payment_gateway_code_chk"),
        CheckConstraint("settlement_currency ~ '^[A-Z]{3}$'", name="payment_gateway_ccy_chk"),
    )