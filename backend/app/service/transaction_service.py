from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status

from app.dto.generic import Page
from app.dto.transaction_dto import TransactionDto
from app.repository.transaction_repository import TransactionRepository

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

        transactions: list[TransactionDto] = []
        for txn, gateway_name, fee_version_code, owner_display_name, parent_txn_ref, settlement_ref in rows:
            transactions.append(
                TransactionDto(
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
                    total_fee=txn.total_fee,
                    expected_net=txn.expected_net,
                    settled_amount=txn.settled_amount,
                    variance_amount=txn.variance_amount,
                    mismatch_flag=txn.mismatch_flag,
                    mismatch_code=txn.mismatch_code,
                )
            )
        return Page(items=transactions, total=total, page=page, page_size=page_size)


def _hk_day_start(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=HK)
