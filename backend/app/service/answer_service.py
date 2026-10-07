import re
from datetime import date
from zoneinfo import ZoneInfo

from app.dto.transaction_dto import TransactionDto
from app.dto.user_dto import CurrentUser
from app.service.document_service import DocumentService
from app.service.openrouter_service import OpenRouterService
from app.service.transaction_service import TransactionService

HK = ZoneInfo("Asia/Hong_Kong")

ISO_DATE = re.compile(r"(?<![0-9])(\d{4})-(\d{2})-(\d{2})(?![0-9])")
LONG_DATE = re.compile(
    r"(?<![A-Za-z0-9])(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{4})(?![A-Za-z0-9])",
    re.IGNORECASE,
)
MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


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
        dates = self._search_dates(question, effective_at, transactions)
        scopes = list(dict.fromkeys(
            (txn.gateway_name, txn.fee_version_code) for txn in transactions
        ))
        chunks = self.document_service.search_similar_chunks(question, dates, scopes=scopes)
        gateways = self.transaction_service.list_settlement_currencies()
        return self.openrouter_service.answer_from_chunks_and_transactions(
            question,
            chunks,
            transactions,
            gateways,
        )

    def _search_dates(
        self,
        question: str,
        effective_at: date | None,
        transactions: list[TransactionDto],
    ) -> list[date]:
        parsed = dates_in(question)
        if parsed:
            return parsed
        if effective_at is not None:
            return [effective_at]
        if transactions:
            dates: list[date] = []
            for txn in transactions:
                hk_date = txn.occurred_at.astimezone(HK).date()
                if hk_date not in dates:
                    dates.append(hk_date)
            return dates
        return [date.today()]


def dates_in(question: str) -> list[date]:
    found: list[tuple[int, date]] = []
    for match in ISO_DATE.finditer(question):
        year, month, day = (int(part) for part in match.groups())
        try:
            found.append((match.start(), date(year, month, day)))
        except ValueError:
            continue
    for match in LONG_DATE.finditer(question):
        day = int(match.group(1))
        month = MONTHS[match.group(2).lower()]
        year = int(match.group(3))
        try:
            found.append((match.start(), date(year, month, day)))
        except ValueError:
            continue
    found.sort(key=lambda item: item[0])
    dates: list[date] = []
    for _, parsed in found:
        if parsed not in dates:
            dates.append(parsed)
    return dates
