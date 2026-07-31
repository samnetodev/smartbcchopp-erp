from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.chopeira_manutencao import (
    ChopeiraManutencaoModel,
    ManutencaoStatus,
)
from database.repositories.base_repository import BaseRepository


class ChopeiraManutencaoRepositoryImpl(BaseRepository[ChopeiraManutencaoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ChopeiraManutencaoModel)

    async def find_by_chopeira(
        self, chopeira_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[ChopeiraManutencaoModel]:
        stmt = (
            select(ChopeiraManutencaoModel)
            .where(ChopeiraManutencaoModel.chopeira_id == chopeira_id)
            .order_by(ChopeiraManutencaoModel.data_solicitacao.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_chopeira(self, chopeira_id: UUID) -> int:
        stmt = (
            select(func.count(ChopeiraManutencaoModel.id))
            .where(ChopeiraManutencaoModel.chopeira_id == chopeira_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def find_by_status(
        self, status: ManutencaoStatus, skip: int = 0, limit: int = 100
    ) -> list[ChopeiraManutencaoModel]:
        stmt = (
            select(ChopeiraManutencaoModel)
            .where(ChopeiraManutencaoModel.status == status)
            .order_by(ChopeiraManutencaoModel.data_solicitacao.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
