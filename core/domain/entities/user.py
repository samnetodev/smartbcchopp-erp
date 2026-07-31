from typing import Any

from core.shared.base_entity import BaseEntity


class User(BaseEntity):
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        funcionario_id: str | None = None,
        ativo: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.funcionario_id = funcionario_id
        self.ativo = ativo
