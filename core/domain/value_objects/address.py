from dataclasses import dataclass

from core.shared.base_value_object import BaseValueObject


@dataclass(frozen=True)
class Address(BaseValueObject):
    logradouro: str
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str
    complemento: str | None = None
    latitude: float | None = None
    longitude: float | None = None
