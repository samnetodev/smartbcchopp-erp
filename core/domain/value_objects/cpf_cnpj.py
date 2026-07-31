from dataclasses import dataclass

from core.shared.base_value_object import BaseValueObject


@dataclass(frozen=True)
class CpfCnpj(BaseValueObject):
    valor: str

    def __post_init__(self) -> None:
        digits = "".join(filter(str.isdigit, self.valor))
        if len(digits) not in (11, 14):
            raise ValueError(f"CPF/CNPJ inválido: {self.valor}")
        object.__setattr__(self, "valor", digits)

    @property
    def is_cpf(self) -> bool:
        return len(self.valor) == 11

    @property
    def is_cnpj(self) -> bool:
        return len(self.valor) == 14

    def formatted(self) -> str:
        if self.is_cpf:
            return f"{self.valor[:3]}.{self.valor[3:6]}.{self.valor[6:9]}-{self.valor[9:]}"
        return (
            f"{self.valor[:2]}.{self.valor[2:5]}.{self.valor[5:8]}/"
            f"{self.valor[8:12]}-{self.valor[12:]}"
        )
