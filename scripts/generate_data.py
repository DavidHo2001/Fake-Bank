"""Generate about 150 fee-bearing transactions. Does not rewrite the 10 golden rows.

Rates come from fee_schedule_tb and fx_mid_rate_tb, which match docs/source.
Same formula as sql/tables/transaction_tb.sql and the Markdown fee files.

Run from anywhere:
    cd backend && source .venv/bin/activate && python ../scripts/generate_data.py

Re-running deletes txn_ref LIKE '%-GEN-%' and NSP-BOUNDARY-0001, then inserts again.
random.seed(42) makes that regeneration identical.
"""

from __future__ import annotations

import os
import random
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.fee_schedule import FeeSchedule
from app.models.fx_mid_rate import FxMidRate
from app.models.gateway_settlement import GatewaySettlement  # noqa: F401
from app.models.payment_gateway import PaymentGateway
from app.models.transaction import Transaction
from app.models.user import User

MONEY = Decimal("0.0001")
RATE = Decimal("0.00000001")
PERCENT = Decimal("0.000001")
HK = timezone(timedelta(hours=8))
WINDOW_START = date(2026, 1, 1)
WINDOW_END = date(2026, 8, 31)
PRIMARY_COUNT = 150
BOUNDARY_REF = "NSP-BOUNDARY-0001"

PRIMARY_TYPE = {"NSP": "payment", "HFL": "payment", "CDG": "payout"}


@dataclass(frozen=True)
class Priced:
    settlement_gross: Decimal
    mid_rate: Decimal
    fx_markup_bps: int
    applied_fx_rate: Decimal
    fx_markup_amount: Decimal
    percent_rate: Decimal
    percent_fee: Decimal
    fixed_fee: Decimal
    min_fee: Decimal
    attempt_fee: Decimal
    min_fee_applied: bool
    total_fee: Decimal
    expected_net: Decimal


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def rate8(value: Decimal) -> Decimal:
    return value.quantize(RATE, rounding=ROUND_HALF_UP)


def percent6(value: Decimal) -> Decimal:
    return value.quantize(PERCENT, rounding=ROUND_HALF_UP)


def hk_civil_date(occurred_at: datetime) -> date:
    return occurred_at.astimezone(HK).date()


def at_hong_kong_noon_utc(civil: date) -> datetime:
    """04:00 UTC is 12:00 in Hong Kong, so the civil date cannot flip."""
    return datetime(civil.year, civil.month, civil.day, 4, 0, tzinfo=timezone.utc)


def price_success(
    gross: Decimal,
    *,
    same_currency: bool,
    mid: Decimal,
    markup_bps: int,
    percent_rate: Decimal,
    fixed_fee: Decimal,
    min_fee: Decimal,
) -> Priced:
    """Docs: markup is inside applied_fx_rate and is not added again to total_fee."""
    gross = money(gross)
    if same_currency:
        mid_rate = rate8(Decimal(1))
        bps = 0
        applied = rate8(Decimal(1))
        settlement_gross = gross
        markup_amount = money(Decimal(0))
    else:
        mid_rate = rate8(mid)
        bps = markup_bps
        applied = rate8(mid_rate * (1 - Decimal(bps) / Decimal(10000)))
        settlement_gross = money(gross * applied)
        markup_amount = money(abs(gross) * mid_rate) - money(abs(settlement_gross))

    percent_fee = money(abs(settlement_gross) * percent_rate)
    fixed = money(fixed_fee)
    minimum = money(min_fee)
    attempt = money(Decimal(0))
    total_fee = money(max(percent_fee + fixed, minimum) + attempt)
    return Priced(
        settlement_gross=settlement_gross,
        mid_rate=mid_rate,
        fx_markup_bps=bps,
        applied_fx_rate=applied,
        fx_markup_amount=markup_amount,
        percent_rate=percent6(percent_rate),
        percent_fee=percent_fee,
        fixed_fee=fixed,
        min_fee=minimum,
        attempt_fee=attempt,
        min_fee_applied=(percent_fee + fixed) < minimum,
        total_fee=total_fee,
        expected_net=money(settlement_gross - total_fee),
    )


def price_failure(gross: Decimal, attempt_fee: Decimal) -> Priced:
    """Failed rows zero the success fees. Only failed_attempt_fee remains."""
    attempt = money(attempt_fee)
    return Priced(
        settlement_gross=money(Decimal(0)),
        mid_rate=rate8(Decimal(1)),
        fx_markup_bps=0,
        applied_fx_rate=rate8(Decimal(1)),
        fx_markup_amount=money(Decimal(0)),
        percent_rate=percent6(Decimal(0)),
        percent_fee=money(Decimal(0)),
        fixed_fee=money(Decimal(0)),
        min_fee=money(Decimal(0)),
        attempt_fee=attempt,
        min_fee_applied=False,
        total_fee=attempt,
        expected_net=money(Decimal(0) - attempt),
    )


def self_test() -> None:
    fx = price_success(
        Decimal("100"),
        same_currency=False,
        mid=Decimal("1.08"),
        markup_bps=150,
        percent_rate=Decimal("0.029"),
        fixed_fee=Decimal("0.30"),
        min_fee=Decimal("0.50"),
    )
    assert fx.applied_fx_rate == Decimal("1.06380000")
    assert fx.settlement_gross == Decimal("106.3800")
    assert fx.fx_markup_amount == Decimal("1.6200")
    assert fx.percent_fee == Decimal("3.0850")
    assert fx.total_fee == Decimal("3.3850")
    assert fx.expected_net == Decimal("102.9950")
    assert fx.min_fee_applied is False

    revised = price_success(
        Decimal("100"),
        same_currency=False,
        mid=Decimal("1.08"),
        markup_bps=200,
        percent_rate=Decimal("0.026"),
        fixed_fee=Decimal("0.30"),
        min_fee=Decimal("0.50"),
    )
    assert revised.settlement_gross == Decimal("105.8400")
    assert revised.percent_fee == Decimal("2.7518")
    assert revised.total_fee == Decimal("3.0518")
    assert revised.expected_net == Decimal("102.7882")

    minimum = price_success(
        Decimal("1"),
        same_currency=True,
        mid=Decimal("1"),
        markup_bps=150,
        percent_rate=Decimal("0.029"),
        fixed_fee=Decimal("0.30"),
        min_fee=Decimal("0.50"),
    )
    assert minimum.total_fee == Decimal("0.5000")
    assert minimum.expected_net == Decimal("0.5000")
    assert minimum.min_fee_applied is True
    assert minimum.fx_markup_bps == 0

    harbor = price_success(
        Decimal("500"),
        same_currency=True,
        mid=Decimal("1"),
        markup_bps=80,
        percent_rate=Decimal("0.018"),
        fixed_fee=Decimal("0"),
        min_fee=Decimal("0"),
    )
    assert harbor.total_fee == Decimal("9.0000")
    assert harbor.expected_net == Decimal("491.0000")

    refund = price_success(
        Decimal("-500"),
        same_currency=True,
        mid=Decimal("1"),
        markup_bps=80,
        percent_rate=Decimal("0"),
        fixed_fee=Decimal("1"),
        min_fee=Decimal("0"),
    )
    assert refund.total_fee == Decimal("1.0000")
    assert refund.expected_net == Decimal("-501.0000")

    cedar_old = price_success(
        Decimal("200"),
        same_currency=True,
        mid=Decimal("1"),
        markup_bps=100,
        percent_rate=Decimal("0.005"),
        fixed_fee=Decimal("2"),
        min_fee=Decimal("2"),
    )
    assert cedar_old.total_fee == Decimal("3.0000")
    cedar_new = price_success(
        Decimal("200"),
        same_currency=True,
        mid=Decimal("1"),
        markup_bps=100,
        percent_rate=Decimal("0.005"),
        fixed_fee=Decimal("3.50"),
        min_fee=Decimal("3.50"),
    )
    assert cedar_new.total_fee == Decimal("4.5000")
    assert cedar_new.expected_net == Decimal("195.5000")

    failed = price_failure(Decimal("80"), Decimal("0.25"))
    assert failed.total_fee == Decimal("0.2500")
    assert failed.expected_net == Decimal("-0.2500")

    boundary_at = datetime(2026, 3, 31, 16, 30, tzinfo=timezone.utc)
    assert hk_civil_date(boundary_at) == date(2026, 4, 1)


def clean(value: str) -> str:
    return value.strip()


def schedule_for(
    schedules: list[FeeSchedule],
    gateway_id: int,
    txn_type: str,
    civil: date,
) -> FeeSchedule | None:
    matches = [
        row
        for row in schedules
        if row.gateway_id == gateway_id
        and row.txn_type == txn_type
        and row.effective_from <= civil
        and (row.effective_to is None or row.effective_to >= civil)
    ]
    if len(matches) != 1:
        return None
    return matches[0]


def mid_for(
    rates: list[FxMidRate],
    base: str,
    quote: str,
    civil: date,
) -> Decimal | None:
    found = [
        row
        for row in rates
        if clean(row.base_currency) == base
        and clean(row.quote_currency) == quote
        and row.as_of_date <= civil
    ]
    if not found:
        return None
    found.sort(key=lambda row: row.as_of_date, reverse=True)
    return found[0].mid_rate


def build_row(
    *,
    txn_ref: str,
    gateway: PaymentGateway,
    schedule: FeeSchedule,
    owner_id: int,
    txn_type: str,
    status: str,
    occurred_at: datetime,
    gross: Decimal,
    gross_currency: str,
    priced: Priced,
    parent_id: int | None,
    settled_amount: Decimal | None,
    mismatch_code: str | None,
) -> Transaction:
    return Transaction(
        txn_ref=txn_ref,
        gateway_id=gateway.id,
        fee_schedule_id=schedule.id,
        owner_user_id=owner_id,
        parent_txn_id=parent_id,
        settlement_id=None,
        txn_type=txn_type,
        status=status,
        occurred_at=occurred_at,
        gross_amount=money(gross),
        gross_currency=gross_currency,
        settlement_currency=clean(gateway.settlement_currency),
        settlement_gross=priced.settlement_gross,
        mid_rate=priced.mid_rate,
        fx_markup_bps=priced.fx_markup_bps,
        applied_fx_rate=priced.applied_fx_rate,
        fx_markup_amount=priced.fx_markup_amount,
        percent_rate=priced.percent_rate,
        percent_fee=priced.percent_fee,
        fixed_fee=priced.fixed_fee,
        min_fee=priced.min_fee,
        attempt_fee=priced.attempt_fee,
        min_fee_applied=priced.min_fee_applied,
        total_fee=priced.total_fee,
        expected_net=priced.expected_net,
        settled_amount=settled_amount,
        mismatch_code=mismatch_code,
    )


def main() -> None:
    self_test()
    random.seed(42)

    with SessionLocal() as session:
        gateways = list(session.scalars(select(PaymentGateway).order_by(PaymentGateway.code)))
        schedules = list(session.scalars(select(FeeSchedule)))
        rates = list(session.scalars(select(FxMidRate)))
        owners = list(session.scalars(select(User).where(User.role == "user").order_by(User.email)))
        if not gateways or not schedules or not owners:
            raise SystemExit("Seed gateways, fee schedules, and merchant users before generating.")

        golden = {
            row.txn_ref: row.total_fee
            for row in session.scalars(select(Transaction).where(~Transaction.txn_ref.like("%-GEN-%")))
            if row.txn_ref != BOUNDARY_REF
        }

        session.execute(
            delete(Transaction).where(
                Transaction.txn_ref.like("%-GEN-%"),
                Transaction.parent_txn_id.is_not(None),
            )
        )
        session.execute(delete(Transaction).where(Transaction.txn_ref.like("%-GEN-%")))
        session.execute(delete(Transaction).where(Transaction.txn_ref == BOUNDARY_REF))

        counters = {clean(gateway.code): 0 for gateway in gateways}
        primaries: list[Transaction] = []
        primary_days: list[date] = []

        for _ in range(PRIMARY_COUNT):
            gateway = random.choice(gateways)
            code = clean(gateway.code)
            txn_type = PRIMARY_TYPE[code]
            civil = WINDOW_START + timedelta(days=random.randint(0, (WINDOW_END - WINDOW_START).days))
            schedule = schedule_for(schedules, gateway.id, txn_type, civil)
            if schedule is None:
                raise SystemExit(f"No single {code} {txn_type} schedule for {civil}")

            settlement = clean(gateway.settlement_currency)
            foreign = sorted(
                {
                    clean(row.base_currency)
                    for row in rates
                    if clean(row.quote_currency) == settlement
                    and mid_for(rates, clean(row.base_currency), settlement, civil) is not None
                }
            )
            use_fx = bool(foreign) and random.random() < 0.20
            if use_fx:
                gross_currency = random.choice(foreign)
                gross = (Decimal(random.randint(2000, 40000)) / Decimal(100)).quantize(MONEY)
                mid = mid_for(rates, gross_currency, settlement, civil)
                assert mid is not None
                same_currency = False
            else:
                gross_currency = settlement
                if code == "NSP" and random.random() < 0.08:
                    gross = Decimal("1.0000")
                else:
                    gross = (Decimal(random.randint(1000, 80000)) / Decimal(100)).quantize(MONEY)
                mid = Decimal(1)
                same_currency = True

            roll = random.random()
            if roll < 0.92:
                status = "settled"
            elif roll < 0.97:
                status = "failed"
            else:
                status = "pending"
            if status == "failed":
                priced = price_failure(gross, schedule.failed_attempt_fee)
                settled_amount = priced.expected_net
                mismatch_code = None
            else:
                priced = price_success(
                    gross,
                    same_currency=same_currency,
                    mid=mid,
                    markup_bps=schedule.fx_markup_bps,
                    percent_rate=schedule.percent_rate,
                    fixed_fee=schedule.fixed_fee,
                    min_fee=schedule.min_fee,
                )
                if status == "pending":
                    settled_amount = None
                    mismatch_code = None
                elif priced.expected_net > Decimal("1") and random.random() < 0.02:
                    settled_amount = money(priced.expected_net - Decimal("0.50"))
                    mismatch_code = "short_pay"
                else:
                    settled_amount = priced.expected_net
                    mismatch_code = None

            counters[code] += 1
            primaries.append(
                build_row(
                    txn_ref=f"{code}-GEN-{counters[code]:06d}",
                    gateway=gateway,
                    schedule=schedule,
                    owner_id=random.choice(owners).id,
                    txn_type=txn_type,
                    status=status,
                    occurred_at=at_hong_kong_noon_utc(civil),
                    gross=gross,
                    gross_currency=gross_currency,
                    priced=priced,
                    parent_id=None,
                    settled_amount=settled_amount,
                    mismatch_code=mismatch_code,
                )
            )
            primary_days.append(civil)

        north = next((user for user in owners if user.email == "merchant.north@fakebank.local"), owners[0])
        nsp = next(gateway for gateway in gateways if clean(gateway.code) == "NSP")
        boundary_at = datetime(2026, 3, 31, 16, 30, tzinfo=timezone.utc)
        boundary_day = hk_civil_date(boundary_at)
        boundary_schedule = schedule_for(schedules, nsp.id, "payment", boundary_day)
        if boundary_schedule is None or boundary_schedule.version_code != "2026-04":
            raise SystemExit("NSP-BOUNDARY-0001 did not resolve to the 2026-04 payment schedule")
        boundary_priced = price_success(
            Decimal("100"),
            same_currency=False,
            mid=mid_for(rates, "EUR", "USD", boundary_day) or Decimal("1.08"),
            markup_bps=boundary_schedule.fx_markup_bps,
            percent_rate=boundary_schedule.percent_rate,
            fixed_fee=boundary_schedule.fixed_fee,
            min_fee=boundary_schedule.min_fee,
        )
        if boundary_priced.expected_net != Decimal("102.7882"):
            raise SystemExit("Boundary trade did not match NSP-VER-0002 fee math")

        session.add_all(primaries)
        session.flush()

        refunds: list[Transaction] = []
        for primary, civil in zip(primaries, primary_days, strict=True):
            if primary.status != "settled" or primary.mismatch_code is not None:
                continue
            if random.random() >= 0.05:
                continue
            gateway = next(row for row in gateways if row.id == primary.gateway_id)
            code = clean(gateway.code)
            refund_day = min(civil + timedelta(days=random.randint(1, 14)), WINDOW_END)
            refund_schedule = schedule_for(schedules, gateway.id, "refund", refund_day)
            if refund_schedule is None:
                continue
            settlement = clean(gateway.settlement_currency)
            gross_currency = clean(primary.gross_currency)
            same_currency = gross_currency == settlement
            mid = Decimal(1) if same_currency else mid_for(rates, gross_currency, settlement, refund_day)
            if mid is None:
                continue
            priced = price_success(
                -primary.gross_amount,
                same_currency=same_currency,
                mid=mid,
                markup_bps=refund_schedule.fx_markup_bps,
                percent_rate=refund_schedule.percent_rate,
                fixed_fee=refund_schedule.fixed_fee,
                min_fee=refund_schedule.min_fee,
            )
            counters[code] += 1
            refunds.append(
                build_row(
                    txn_ref=f"{primary.txn_ref}-R",
                    gateway=gateway,
                    schedule=refund_schedule,
                    owner_id=primary.owner_user_id,
                    txn_type="refund",
                    status="settled",
                    occurred_at=at_hong_kong_noon_utc(refund_day),
                    gross=-primary.gross_amount,
                    gross_currency=gross_currency,
                    priced=priced,
                    parent_id=primary.id,
                    settled_amount=priced.expected_net,
                    mismatch_code=None,
                )
            )

        session.add(
            build_row(
                txn_ref=BOUNDARY_REF,
                gateway=nsp,
                schedule=boundary_schedule,
                owner_id=north.id,
                txn_type="payment",
                status="settled",
                occurred_at=boundary_at,
                gross=Decimal("100"),
                gross_currency="EUR",
                priced=boundary_priced,
                parent_id=None,
                settled_amount=boundary_priced.expected_net,
                mismatch_code=None,
            )
        )
        session.add_all(refunds)
        session.commit()

        for txn_ref, total_fee in golden.items():
            current = session.scalar(select(Transaction.total_fee).where(Transaction.txn_ref == txn_ref))
            if current != total_fee:
                raise SystemExit(f"{txn_ref} total_fee changed from {total_fee} to {current}")

        boundary = session.scalar(select(Transaction).where(Transaction.txn_ref == BOUNDARY_REF))
        boundary_fee = session.get(FeeSchedule, boundary.fee_schedule_id)
        if boundary_fee.version_code != "2026-04" or boundary.expected_net != Decimal("102.7882"):
            raise SystemExit("Boundary row was stored with the wrong fee version")

        version = session.scalar(
            select(FeeSchedule.version_code)
            .join(Transaction, Transaction.fee_schedule_id == FeeSchedule.id)
            .where(Transaction.txn_ref == "NSP-VER-0002")
        )
        if version != "2026-04":
            raise SystemExit("NSP-VER-0002 no longer points at 2026-04")

        gen_count = len(session.scalars(select(Transaction.id).where(Transaction.txn_ref.like("%-GEN-%"))).all())
        print(f"generated {gen_count} rows ({PRIMARY_COUNT} primary, {len(refunds)} refunds)")
        print(f"boundary {BOUNDARY_REF} uses {boundary_fee.version_code}, expected_net {boundary.expected_net}")
        print(f"golden rows unchanged: {len(golden)}")
        if gen_count != PRIMARY_COUNT + len(refunds):
            raise SystemExit("Generated row count does not match the insert")


if __name__ == "__main__":
    main()
