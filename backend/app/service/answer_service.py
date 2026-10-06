from datetime import date
from zoneinfo import ZoneInfo

from app.dto.user_dto import CurrentUser
from app.service.document_service import DocumentService
from app.service.openrouter_service import OpenRouterService
from app.service.transaction_service import TransactionService

HK = ZoneInfo("Asia/Hong_Kong")


class AnswerService:
    def __init__(
        self,
        document_service: DocumentService,
        transaction_service: TransactionService,
        openrouter_service: OpenRouterService,
    ) -> None:
        self.document_service = document_service
        self.transaction_service = transaction_service
        self.openrouter_service = openrouter_service

    def answer(self, question: str, effective_at: date | None, current_user: CurrentUser) -> str:
        transactions = self.transaction_service.get_transaction_from_question(
            question,
            current_user.id,
            current_user.role,
        )
        dates = self._search_dates(effective_at, transactions)
        chunks = self.document_service.search_similar_chunks(question, dates)
        return self.openrouter_service.answer_from_chunks_and_transactions(
            question,
            chunks,
            transactions,
        )

    def _search_dates(self, effective_at: date | None, transactions) -> list[date]:
        if not transactions:
            return [effective_at or date.today()]

        dates: list[date] = []
        for txn in transactions:
            hk_date = txn.occurred_at.astimezone(HK).date()
            if hk_date not in dates:
                dates.append(hk_date)
        return dates
