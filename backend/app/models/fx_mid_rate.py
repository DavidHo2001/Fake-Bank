from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, BigInteger, CheckConstraint, Date, DateTime, Identity, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FxMidRate(Base):
    __tablename__ = "fx_mid_rate_tb"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    base_currency: Mapped[str] = mapped_column(CHAR(3))
    quote_currency: Mapped[str] = mapped_column(CHAR(3))
    as_of_date: Mapped[date] = mapped_column(Date)
    mid_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("base_currency", "quote_currency", "as_of_date", name="fx_mid_rate_pair_uq"),
        CheckConstraint(
            "base_currency ~ '^[A-Z]{3}$' AND quote_currency ~ '^[A-Z]{3}$' AND base_currency <> quote_currency",
            name="fx_mid_rate_ccy_chk",
        ),
        CheckConstraint("mid_rate > 0", name="fx_mid_rate_positive_chk"),
    )