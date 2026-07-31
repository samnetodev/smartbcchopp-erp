from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.veiculo_troca_oleo import TrocaOleoModel
from database.repositories.base_repository import BaseRepository


class TrocaOleoRepositoryImpl(BaseRepository[TrocaOleoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TrocaOleoModel)

    async def find_by_veiculo(
        self, veiculo_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[TrocaOleoModel]:
        stmt = (
            select(TrocaOleoModel)
            .where(TrocaOleoModel.veiculo_id == veiculo_id)
            .order_by(TrocaOleoModel.data.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_veiculo(self, veiculo_id: UUID) -> int:
        stmt = (
            select(func.count(TrocaOleoModel.id))
            .where(TrocaOleoModel.veiculo_id == veiculo_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def total_gasto_por_veiculo_periodo(
        self, veiculo_id: UUID, data_inicio: date, data_fim: date
    ) -> float:
        stmt = (
            select(func.coalesce(func.sum(TrocaOleoModel.valor_total), 0))
            .where(
                TrocaOleoModel.veiculo_id == veiculo_id,
                TrocaOleoModel.data >= data_inicio,
                TrocaOleoModel.data <= data_fim,
            )
        )
        result = await self._session.execute(stmt)
        return float(result.scalar() or 0)
