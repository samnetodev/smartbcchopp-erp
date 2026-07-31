from typing import Any

from core.shared.base_entity import BaseEntity


class Customer(BaseEntity):
    def __init__(
        self,
        nome_razao_social: str,
        cpf_cnpj: str,
        tipo_pessoa: str,
        email: str | None = None,
        telefone: str | None = None,
        limite_credito: float = 0.0,
        status: str = "ativo",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.nome_razao_social = nome_razao_social
        self.cpf_cnpj = cpf_cnpj
        self.tipo_pessoa = tipo_pessoa
        self.email = email
        self.telefone = telefone
        self.limite_credito = limite_credito
        self.status = status
