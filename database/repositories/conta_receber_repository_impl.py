from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.conta_receber import ContaReceberModel, ContaStatus
from database.repositories.base_repository import BaseRepository


class ContaReceberRepositoryImpl(BaseRepository[ContaReceberModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ContaReceberModel)

    async def find_by_cliente(self, cliente_id: UUID) -> list[ContaReceberModel]:
        stmt = (
            select(ContaReceberModel)
            .where(ContaReceberModel.cliente_id == cliente_id)
            .order_by(ContaReceberModel.data_vencimento)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_status(self, status: str) -> list[ContaReceberModel]:
        stmt = (
            select(ContaReceberModel)
            .where(ContaReceberModel.status == status)
            .order_by(ContaReceberModel.data_vencimento)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_periodo(
        self, data_inicio: date, data_fim: date, skip: int = 0, limit: int = 500
    ) -> list[ContaReceberModel]:
        stmt = (
            select(ContaReceberModel)
            .where(ContaReceberModel.data_vencimento.between(data_inicio, data_fim))
            .order_by(ContaReceberModel.data_vencimento)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def sum_open(self) -> float:
        saldo = (
            ContaReceberModel.valor_original
            - ContaReceberModel.valor_pago
            - ContaReceberModel.desconto
            + ContaReceberModel.juros
            + ContaReceberModel.multa
        )
        stmt = select(func.sum(saldo)).where(
            ContaReceberModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL])
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)

    async def sum_overdue(self) -> float:
        hoje = date.today()
        saldo = (
            ContaReceberModel.valor_original
            - ContaReceberModel.valor_pago
            - ContaReceberModel.desconto
            + ContaReceberModel.juros
            + ContaReceberModel.multa
        )
        stmt = select(func.sum(saldo)).where(
            ContaReceberModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]),
            ContaReceberModel.data_vencimento < hoje,
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)
