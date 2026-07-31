from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.veiculo_km_registro import KmRegistroModel
from database.repositories.base_repository import BaseRepository


class KmRegistroRepositoryImpl(BaseRepository[KmRegistroModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, KmRegistroModel)

    async def find_by_veiculo(
        self, veiculo_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[KmRegistroModel]:
        stmt = (
            select(KmRegistroModel)
            .where(KmRegistroModel.veiculo_id == veiculo_id)
            .order_by(KmRegistroModel.data.desc(), KmRegistroModel.km.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_veiculo(self, veiculo_id: UUID) -> int:
        stmt = (
            select(func.count(KmRegistroModel.id))
            .where(KmRegistroModel.veiculo_id == veiculo_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_ultimo_km(self, veiculo_id: UUID) -> int | None:
        stmt = (
            select(KmRegistroModel.km)
            .where(KmRegistroModel.veiculo_id == veiculo_id)
            .order_by(KmRegistroModel.km.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return row
