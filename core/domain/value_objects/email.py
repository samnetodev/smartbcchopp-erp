import re
from dataclasses import dataclass

from core.shared.base_value_object import BaseValueObject


@dataclass(frozen=True)
class Email(BaseValueObject):
    endereco: str

    _PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __post_init__(self) -> None:
        if not self._PATTERN.match(self.endereco):
            raise ValueError(f"Email inválido: {self.endereco}")
