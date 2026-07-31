from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.veiculo_pneu import PneuModel, PneuStatus
from database.repositories.base_repository import BaseRepository


class PneuRepositoryImpl(BaseRepository[PneuModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PneuModel)

    async def find_by_veiculo(
        self, veiculo_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[PneuModel]:
        stmt = (
            select(PneuModel)
            .where(PneuModel.veiculo_id == veiculo_id)
            .order_by(PneuModel.posicao)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_veiculo(self, veiculo_id: UUID) -> int:
        stmt = (
            select(func.count(PneuModel.id))
            .where(PneuModel.veiculo_id == veiculo_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def find_ativos_by_veiculo(self, veiculo_id: UUID) -> list[PneuModel]:
        stmt = (
            select(PneuModel)
            .where(
                PneuModel.veiculo_id == veiculo_id,
                PneuModel.status == PneuStatus.ATIVO,
            )
            .order_by(PneuModel.posicao)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
