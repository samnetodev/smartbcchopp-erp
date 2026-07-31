from abc import ABC, abstractmethod
from uuid import UUID

from core.domain.entities.customer import Customer


class CustomerRepository(ABC):
    @abstractmethod
    async def save(self, customer: Customer) -> None: ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Customer | None: ...

    @abstractmethod
    async def find_by_cpf_cnpj(self, cpf_cnpj: str) -> Customer | None: ...

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> list[Customer]: ...
