from abc import ABC, abstractmethod
from uuid import UUID

from core.domain.entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None: ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Order | None: ...

    @abstractmethod
    async def find_by_numero(self, numero: str) -> Order | None: ...

    @abstractmethod
    async def find_by_cliente(self, cliente_id: UUID) -> list[Order]: ...

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> list[Order]: ...

    @abstractmethod
    async def next_numero(self) -> str: ...
