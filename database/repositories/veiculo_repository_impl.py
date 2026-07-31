
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.veiculo import VeiculoModel
from database.repositories.base_repository import BaseRepository


class VeiculoRepositoryImpl(BaseRepository[VeiculoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, VeiculoModel)

    async def find_by_placa(self, placa: str) -> VeiculoModel | None:
        stmt = select(VeiculoModel).where(VeiculoModel.placa == placa)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_status(self, status: str) -> list[VeiculoModel]:
        stmt = (
            select(VeiculoModel)
            .where(VeiculoModel.status == status, VeiculoModel.ativo.is_(True))
            .order_by(VeiculoModel.modelo)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_all_active(self, skip: int = 0, limit: int = 100) -> list[VeiculoModel]:
        stmt = (
            select(VeiculoModel)
            .where(VeiculoModel.ativo.is_(True))
            .offset(skip)
            .limit(limit)
            .order_by(VeiculoModel.placa)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> list[VeiculoModel]:
        pattern = f"%{query}%"
        stmt = (
            select(VeiculoModel)
            .where(
                VeiculoModel.ativo.is_(True),
                VeiculoModel.placa.ilike(pattern),
            )
            .offset(skip)
            .limit(limit)
            .order_by(VeiculoModel.placa)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_active(self) -> int:
        from sqlalchemy import func

        stmt = select(func.count(VeiculoModel.id)).where(VeiculoModel.ativo.is_(True))
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def soft_delete(self, veiculo: VeiculoModel) -> None:
        from database.models.veiculo import VeiculoStatus

        veiculo.ativo = False
        veiculo.status = VeiculoStatus.INATIVO
        await self._session.merge(veiculo)

    async def find_with_custos_periodo(
        self, data_inicio: date, data_fim: date, skip: int = 0, limit: int = 100
    ) -> list[VeiculoModel]:
        stmt = (
            select(VeiculoModel)
            .where(VeiculoModel.ativo.is_(True))
            .options(
                selectinload(VeiculoModel.abastecimentos),
                selectinload(VeiculoModel.manutencoes),
                selectinload(VeiculoModel.multas),
                selectinload(VeiculoModel.seguros),
                selectinload(VeiculoModel.trocas_oleo),
            )
            .offset(skip)
            .limit(limit)
            .order_by(VeiculoModel.placa)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
