from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.auditoria import AuditoriaModel


class AuditoriaRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_all(
        self,
        entidade_tipo: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditoriaModel]:
        stmt = select(AuditoriaModel)
        if entidade_tipo:
            stmt = stmt.where(AuditoriaModel.entidade_tipo == entidade_tipo)
        stmt = stmt.order_by(AuditoriaModel.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, entidade_tipo: str | None = None) -> int:
        stmt = select(func.count()).select_from(AuditoriaModel)
        if entidade_tipo:
            stmt = stmt.where(AuditoriaModel.entidade_tipo == entidade_tipo)
        result = await self._session.execute(stmt)
        return result.scalar_one()
