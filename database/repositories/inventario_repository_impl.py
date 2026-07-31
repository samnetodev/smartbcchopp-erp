from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.inventario import InventarioModel, InventarioStatus
from database.repositories.base_repository import BaseRepository


class InventarioRepositoryImpl(BaseRepository[InventarioModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, InventarioModel)

    async def find_by_deposito(
        self, deposito_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[InventarioModel]:
        stmt = (
            select(InventarioModel)
            .where(InventarioModel.deposito_id == deposito_id)
            .order_by(InventarioModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_abertos(self) -> list[InventarioModel]:
        stmt = (
            select(InventarioModel)
            .where(InventarioModel.status == InventarioStatus.ABERTO)
            .order_by(InventarioModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
