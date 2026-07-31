from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.alerta import AlertaModel
from database.repositories.base_repository import BaseRepository


class AlertaRepositoryImpl(BaseRepository[AlertaModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AlertaModel)

    async def find_nao_lidos(self, skip: int = 0, limit: int = 50) -> list[AlertaModel]:
        stmt = (
            select(AlertaModel)
            .where(AlertaModel.lido.is_(False))
            .order_by(AlertaModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_nao_lidos(self) -> int:
        stmt = (
            select(func.count())
            .select_from(AlertaModel)
            .where(AlertaModel.lido.is_(False))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def find_by_tipo(self, tipo: str, skip: int = 0, limit: int = 50) -> list[AlertaModel]:
        stmt = (
            select(AlertaModel)
            .where(AlertaModel.tipo == tipo)
            .order_by(AlertaModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
