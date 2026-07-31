from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.motorista import MotoristaModel
from database.repositories.base_repository import BaseRepository


class MotoristaRepositoryImpl(BaseRepository[MotoristaModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MotoristaModel)

    async def find_by_cnh(self, numero_cnh: str) -> MotoristaModel | None:
        stmt = select(MotoristaModel).where(MotoristaModel.numero_cnh == numero_cnh)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_funcionario(self, funcionario_id: UUID) -> MotoristaModel | None:
        stmt = select(MotoristaModel).where(
            MotoristaModel.funcionario_id == funcionario_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_status(self, status: str) -> list[MotoristaModel]:
        stmt = (
            select(MotoristaModel)
            .where(MotoristaModel.status == status, MotoristaModel.ativo.is_(True))
            .order_by(MotoristaModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_all_active(self, skip: int = 0, limit: int = 100) -> list[MotoristaModel]:
        stmt = (
            select(MotoristaModel)
            .where(MotoristaModel.ativo.is_(True))
            .offset(skip)
            .limit(limit)
            .order_by(MotoristaModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> list[MotoristaModel]:
        pattern = f"%{query}%"
        stmt = (
            select(MotoristaModel)
            .where(
                MotoristaModel.ativo.is_(True),
                MotoristaModel.numero_cnh.ilike(pattern),
            )
            .offset(skip)
            .limit(limit)
            .order_by(MotoristaModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_active(self) -> int:
        from sqlalchemy import func

        stmt = select(func.count(MotoristaModel.id)).where(MotoristaModel.ativo.is_(True))
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def soft_delete(self, motorista: MotoristaModel) -> None:
        from database.models.motorista import MotoristaStatus

        motorista.ativo = False
        motorista.status = MotoristaStatus.INATIVO
        await self._session.merge(motorista)
