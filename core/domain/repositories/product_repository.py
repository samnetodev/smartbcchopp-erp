from abc import ABC, abstractmethod
from uuid import UUID

from core.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    async def save(self, product: Product) -> None: ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Product | None: ...

    @abstractmethod
    async def find_by_codigo(self, codigo: str) -> Product | None: ...

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> list[Product]: ...

    @abstractmethod
    async def delete(self, id: UUID) -> None: ...
