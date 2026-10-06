from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.models.fee_schedule import FeeSchedule
from app.models.gateway_settlement import GatewaySettlement
from app.models.payment_gateway import PaymentGateway
from app.models.transaction import Transaction
from app.models.user import User

TransactionRow = tuple[Transaction, str, str, str, str | None, str | None]


class TransactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_page(
        self,
        owner_user_id: int | None,
        occurred_start: datetime | None,
        occurred_end: datetime | None,
        page: int,
        page_size: int,
    ) -> tuple[list[TransactionRow], int]:
        parent = aliased(Transaction)
        filters = []
        if owner_user_id is not None:
            filters.append(Transaction.owner_user_id == owner_user_id)
        if occurred_start is not None:
            filters.append(Transaction.occurred_at >= occurred_start)
        if occurred_end is not None:
            filters.append(Transaction.occurred_at < occurred_end)

        count_statement = select(func.count()).select_from(Transaction)
        statement = (
            select(
                Transaction,
                PaymentGateway.name,
                FeeSchedule.version_code,
                User.display_name,
                parent.txn_ref,
                GatewaySettlement.settlement_ref,
            )
            .join(PaymentGateway, Transaction.gateway_id == PaymentGateway.id)
            .join(FeeSchedule, Transaction.fee_schedule_id == FeeSchedule.id)
            .join(User, Transaction.owner_user_id == User.id)
            .outerjoin(parent, Transaction.parent_txn_id == parent.id)
            .outerjoin(GatewaySettlement, Transaction.settlement_id == GatewaySettlement.id)
            .order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
        )
        if filters:
            count_statement = count_statement.where(*filters)
            statement = statement.where(*filters)

        total = self.db.scalar(count_statement) or 0
        offset = (page - 1) * page_size
        statement = statement.limit(page_size).offset(offset)
        rows = self.db.execute(statement).all()
        return [
            (txn, gateway_name, fee_version_code, owner_display_name, parent_txn_ref, settlement_ref)
            for txn, gateway_name, fee_version_code, owner_display_name, parent_txn_ref, settlement_ref in rows
        ], total

    def find_by_txn_refs(
        self,
        owner_user_id: int | None,
        txn_refs: list[str],
    ) -> list[TransactionRow]:
        if not txn_refs:
            return []
        parent = aliased(Transaction)
        statement = (
            select(
                Transaction,
                PaymentGateway.name,
                FeeSchedule.version_code,
                User.display_name,
                parent.txn_ref,
                GatewaySettlement.settlement_ref,
            )
            .join(PaymentGateway, Transaction.gateway_id == PaymentGateway.id)
            .join(FeeSchedule, Transaction.fee_schedule_id == FeeSchedule.id)
            .join(User, Transaction.owner_user_id == User.id)
            .outerjoin(parent, Transaction.parent_txn_id == parent.id)
            .outerjoin(GatewaySettlement, Transaction.settlement_id == GatewaySettlement.id)
            .where(Transaction.txn_ref.in_(txn_refs))
            .order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
        )
        if owner_user_id is not None:
            statement = statement.where(Transaction.owner_user_id == owner_user_id)
        rows = self.db.execute(statement).all()
        return [
            (txn, gateway_name, fee_version_code, owner_display_name, parent_txn_ref, settlement_ref)
            for txn, gateway_name, fee_version_code, owner_display_name, parent_txn_ref, settlement_ref in rows
        ]
