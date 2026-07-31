from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from core.shared.base_value_object import BaseValueObject


@dataclass(frozen=True)
class Money(BaseValueObject):
    amount: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "amount",
            self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        )

    def __add__(self, other: Money) -> Money:
        return Money(self.amount + other.amount)

    def __sub__(self, other: Money) -> Money:
        return Money(self.amount - other.amount)

    def __mul__(self, factor: Decimal) -> Money:
        return Money(self.amount * factor)

    def __gt__(self, other: Money) -> bool:
        return self.amount > other.amount

    def __lt__(self, other: Money) -> bool:
        return self.amount < other.amount
