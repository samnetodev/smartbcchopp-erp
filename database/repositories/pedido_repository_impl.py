from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.pedido import PedidoModel
from database.repositories.base_repository import BaseRepository


class PedidoRepositoryImpl(BaseRepository[PedidoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PedidoModel)

    async def find_by_id_with_items(self, id: UUID) -> PedidoModel | None:
        stmt = (
            select(PedidoModel).options(selectinload(PedidoModel.itens)).where(PedidoModel.id == id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_numero(self, numero: str) -> PedidoModel | None:
        stmt = select(PedidoModel).where(PedidoModel.numero == numero)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_cliente(
        self, cliente_id: UUID, skip: int = 0, limit: int = 50
    ) -> list[PedidoModel]:
        stmt = (
            select(PedidoModel)
            .where(PedidoModel.cliente_id == cliente_id)
            .offset(skip)
            .limit(limit)
            .order_by(PedidoModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> list[PedidoModel]:
        stmt = (
            select(PedidoModel)
            .where(PedidoModel.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(PedidoModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def next_numero(self) -> str:
        from datetime import datetime

        ano = datetime.now().year
        stmt = (
            select(func.count()).select_from(PedidoModel).where(PedidoModel.numero.like(f"P{ano}%"))
        )
        result = await self._session.execute(stmt)
        count = result.scalar_one() + 1
        return f"P{ano}{count:05d}"

    async def count_by_status(self, status: str) -> int:
        stmt = select(func.count()).select_from(PedidoModel).where(PedidoModel.status == status)
        result = await self._session.execute(stmt)
        return result.scalar_one()
