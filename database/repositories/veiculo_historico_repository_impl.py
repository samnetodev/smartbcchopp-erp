from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.veiculo_historico import VeiculoHistoricoModel
from database.repositories.base_repository import BaseRepository


class VeiculoHistoricoRepositoryImpl(BaseRepository[VeiculoHistoricoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, VeiculoHistoricoModel)

    async def find_by_veiculo(
        self, veiculo_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[VeiculoHistoricoModel]:
        stmt = (
            select(VeiculoHistoricoModel)
            .where(VeiculoHistoricoModel.veiculo_id == veiculo_id)
            .order_by(VeiculoHistoricoModel.data_evento.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_veiculo(self, veiculo_id: UUID) -> int:
        stmt = (
            select(func.count(VeiculoHistoricoModel.id))
            .where(VeiculoHistoricoModel.veiculo_id == veiculo_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
