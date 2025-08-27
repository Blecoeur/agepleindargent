import csv
import hashlib
from datetime import datetime
from typing import Iterable, Protocol, IO

from schemas import TransactionIn


class BaseParser(Protocol):
    name: str

    def sniff(self, header: list[str]) -> bool:
        ...

    def parse(self, file_obj: IO[bytes]) -> Iterable[TransactionIn]:
        ...


class WorldlineMockParser:
    name = "mock_worldline"

    expected_fields = {
        "selling_point",
        "ept",
        "amount_cents",
        "currency",
        "occurred_at",
        "card_last4",
    }

    def sniff(self, header: list[str]) -> bool:
        return set(header) >= self.expected_fields

    def parse(self, file_obj: IO[bytes]) -> Iterable[TransactionIn]:
        text = file_obj.read().decode("utf-8")
        reader = csv.DictReader(text.splitlines())
        for row in reader:
            normalized = "|".join(
                [
                    row["selling_point"],
                    row["ept"],
                    row["amount_cents"],
                    row["currency"],
                    row["occurred_at"],
                    row["card_last4"],
                ]
            )
            source_row_hash = hashlib.sha256(normalized.encode()).hexdigest()
            yield TransactionIn(
                selling_point_name=row["selling_point"],
                ept_label=row["ept"],
                amount_cents=int(row["amount_cents"]),
                currency=row["currency"],
                occurred_at=datetime.fromisoformat(row["occurred_at"]),
                card_last4=row["card_last4"],
                source_row_hash=source_row_hash,
            )


PARSER_REGISTRY: dict[str, BaseParser] = {"mock_worldline": WorldlineMockParser()}
