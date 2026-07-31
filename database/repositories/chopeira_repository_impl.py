from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.chopeira import ChopeiraModel, ChopeiraStatus
from database.repositories.base_repository import BaseRepository


class ChopeiraRepositoryImpl(BaseRepository[ChopeiraModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ChopeiraModel)

    async def find_by_status(self, status: ChopeiraStatus) -> list[ChopeiraModel]:
        stmt = select(ChopeiraModel).where(
            ChopeiraModel.status == status, ChopeiraModel.ativo.is_(True)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_cliente(self, cliente_id: UUID) -> list[ChopeiraModel]:
        stmt = select(ChopeiraModel).where(
            ChopeiraModel.cliente_id == cliente_id, ChopeiraModel.ativo.is_(True)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_codigo(self, codigo: str) -> ChopeiraModel | None:
        stmt = select(ChopeiraModel).where(ChopeiraModel.codigo_identificacao == codigo)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_status(self) -> dict[str, int]:
        from sqlalchemy import func

        stmt = (
            select(ChopeiraModel.status, func.count(ChopeiraModel.id))
            .where(ChopeiraModel.ativo.is_(True))
            .group_by(ChopeiraModel.status)
        )
        result = await self._session.execute(stmt)
        return {row[0].value: row[1] for row in result.all()}

    async def find_maintenance_due(self, limit_days: int = 30) -> list[ChopeiraModel]:
        from datetime import date, timedelta

        today = date.today()
        deadline = today + timedelta(days=limit_days)
        stmt = (
            select(ChopeiraModel)
            .where(
                ChopeiraModel.ativo.is_(True),
                ChopeiraModel.data_proxima_manutencao.isnot(None),
                ChopeiraModel.data_proxima_manutencao <= deadline,
            )
            .options(selectinload(ChopeiraModel.cliente))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_all_active(self, skip: int = 0, limit: int = 100) -> list[ChopeiraModel]:
        stmt = (
            select(ChopeiraModel)
            .where(ChopeiraModel.ativo.is_(True))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> list[ChopeiraModel]:
        stmt = (
            select(ChopeiraModel)
            .where(
                ChopeiraModel.ativo.is_(True),
                ChopeiraModel.codigo_identificacao.ilike(f"%{query}%"),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def soft_delete(self, chopeira: ChopeiraModel) -> None:
        chopeira.ativo = False
        chopeira.status = ChopeiraStatus.BAIXADA
        await self._session.merge(chopeira)
