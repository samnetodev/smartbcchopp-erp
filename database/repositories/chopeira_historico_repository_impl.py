from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.chopeira_historico import ChopeiraHistoricoModel, HistoricoEvento
from database.repositories.base_repository import BaseRepository


class ChopeiraHistoricoRepositoryImpl(BaseRepository[ChopeiraHistoricoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ChopeiraHistoricoModel)

    async def find_by_chopeira(
        self, chopeira_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[ChopeiraHistoricoModel]:
        stmt = (
            select(ChopeiraHistoricoModel)
            .where(ChopeiraHistoricoModel.chopeira_id == chopeira_id)
            .order_by(ChopeiraHistoricoModel.data_evento.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_chopeira(self, chopeira_id: UUID) -> int:
        stmt = (
            select(func.count(ChopeiraHistoricoModel.id))
            .where(ChopeiraHistoricoModel.chopeira_id == chopeira_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def find_by_evento(
        self, chopeira_id: UUID, evento: HistoricoEvento
    ) -> list[ChopeiraHistoricoModel]:
        stmt = (
            select(ChopeiraHistoricoModel)
            .where(
                ChopeiraHistoricoModel.chopeira_id == chopeira_id,
                ChopeiraHistoricoModel.evento == evento,
            )
            .order_by(ChopeiraHistoricoModel.data_evento.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
