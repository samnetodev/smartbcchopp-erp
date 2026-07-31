from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.veiculo_seguro import SeguroModel
from database.repositories.base_repository import BaseRepository


class SeguroRepositoryImpl(BaseRepository[SeguroModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SeguroModel)

    async def find_by_veiculo(
        self, veiculo_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[SeguroModel]:
        stmt = (
            select(SeguroModel)
            .where(SeguroModel.veiculo_id == veiculo_id, SeguroModel.ativo.is_(True))
            .order_by(SeguroModel.data_fim_vigencia.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_veiculo(self, veiculo_id: UUID) -> int:
        stmt = (
            select(func.count(SeguroModel.id))
            .where(SeguroModel.veiculo_id == veiculo_id, SeguroModel.ativo.is_(True))
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def find_ativos_vencendo(self, dias: int = 30) -> list[SeguroModel]:
        from datetime import date, timedelta

        today = date.today()
        deadline = today + timedelta(days=dias)
        stmt = (
            select(SeguroModel)
            .where(
                SeguroModel.ativo.is_(True),
                SeguroModel.status == "ativo",
                SeguroModel.data_fim_vigencia <= deadline,
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
