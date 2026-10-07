from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status

from app.dto.generic import Page
from app.dto.transaction_dto import TransactionDto
from app.models.transaction import Transaction
from app.read_models.gateway_settlement_currency import GatewaySettlementCurrency
from app.repository.transaction_repository import TransactionRepository

import re

# Case-insensitive ref: 3 letters, "-", letters/digits, "-", 4–6 digits.
# A letter may follow the digits, so NSP-FX-0001NSP-VER-0002 still yields the first ref.
# More digits, or a digit before the second ref, do not match.
TXN_REF = re.compile(
    r"(?<![A-Za-z0-9])[A-Z]{3}-[A-Z0-9]+-\d{4,6}(?![0-9])",
    re.IGNORECASE,
)

HK = ZoneInfo("Asia/Hong_Kong")


class TransactionService:
    def __init__(self, repository: TransactionRepository) -> None:
        self.repository = repository

    def list_transactions(
        self,
        user_id: int,
        role: str,
        page: int,
        page_size: int,
        occurred_from: date | None,
        occurred_to: date | None,
    ) -> Page[TransactionDto]:
        if occurred_from is not None and occurred_to is not None and occurred_from > occurred_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="occurred_from must be on or before occurred_to",
            )

        owner_user_id = None if role == "admin" else user_id
        occurred_start = _hk_day_start(occurred_from) if occurred_from is not None else None
        occurred_end = _hk_day_start(occurred_to + timedelta(days=1)) if occurred_to is not None else None
        rows, total = self.repository.find_page(
            owner_user_id,
            occurred_start,
            occurred_end,
            page,
            page_size,
        )

        transactions = [map_to_transaction_dto(*row) for row in rows]
        return Page(items=transactions, total=total, page=page, page_size=page_size)

    def list_settlement_currencies(self) -> list[GatewaySettlementCurrency]:
        return self.repository.list_settlement_currencies()

    def get_transaction_from_question(self, question: str, user_id: int, role: str) -> list[TransactionDto]:
        owner_user_id = None if role == "admin" else user_id
        txn_refs = txn_refs_in(question)
        if txn_refs:
            rows = self.repository.find_by_txn_refs(owner_user_id, txn_refs)
            if len(rows) != len(txn_refs):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some transaction references are not found or not belong to the user",
                )
            return [map_to_transaction_dto(*row) for row in rows]
        return []


def _hk_day_start(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=HK)

def txn_refs_in(question: str) -> list[str]:
    refs = TXN_REF.findall(question)
    upper_refs = [ref.upper() for ref in refs]
    unique_refs = list(dict.fromkeys(upper_refs))
    return unique_refs

def map_to_transaction_dto(
    txn: Transaction,
    gateway_name: str,
    fee_version_code: str,
    owner_display_name: str,
    parent_txn_ref: str | None,
    settlement_ref: str | None,
) -> TransactionDto:
    return TransactionDto(
        txn_ref=txn.txn_ref,
        gateway_name=gateway_name,
        fee_version_code=fee_version_code,
        owner_display_name=owner_display_name,
        parent_txn_ref=parent_txn_ref,
        settlement_ref=settlement_ref,
        txn_type=txn.txn_type,
        status=txn.status,
        occurred_at=txn.occurred_at,
        gross_amount=txn.gross_amount,
        gross_currency=txn.gross_currency,
        settlement_currency=txn.settlement_currency,
        settlement_gross=txn.settlement_gross,
        mid_rate=txn.mid_rate,
        fx_markup_bps=txn.fx_markup_bps,
        percent_rate=txn.percent_rate,
        total_fee=txn.total_fee,
        expected_net=txn.expected_net,
        settled_amount=txn.settled_amount,
        variance_amount=txn.variance_amount,
        mismatch_flag=txn.mismatch_flag,
        mismatch_code=txn.mismatch_code,
    )