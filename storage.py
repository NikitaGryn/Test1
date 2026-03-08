from datetime import datetime
from typing import List

from models import Transaction, TransactionsData
from helpers import decode_message_from_transaction


class InMemoryStorage:
    def __init__(self) -> None:
        self.transactions: List[Transaction] = []

    def add_transaction(self, tx: Transaction) -> None:
        self.transactions.append(tx)

    def list_outgoing_for_system_a(
        self, start: datetime, end: datetime, limit: int, offset: int
    ) -> TransactionsData:
        # Только транзакции в SYSTEM_A за период, с пагинацией
        filtered: List[Transaction] = []
        for tx in self.transactions:
            try:
                msg = decode_message_from_transaction(tx)
            except Exception:
                continue
            if msg.ReceiverBranch != "SYSTEM_A":
                continue
            if not (start <= tx.TransactionTime <= end):
                continue
            filtered.append(tx)
        filtered.sort(key=lambda t: t.TransactionTime)
        total = len(filtered)
        paged = filtered[offset : offset + limit] if limit > 0 else filtered[offset:]
        return TransactionsData(Transactions=paged, Count=total)


storage = InMemoryStorage()
