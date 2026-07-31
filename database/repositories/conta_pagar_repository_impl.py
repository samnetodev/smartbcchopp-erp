from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.conta_pagar import ContaPagarModel
from database.models.conta_receber import ContaStatus
from database.repositories.base_repository import BaseRepository


class ContaPagarRepositoryImpl(BaseRepository[ContaPagarModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ContaPagarModel)

    async def find_by_fornecedor(self, fornecedor_id: UUID) -> list[ContaPagarModel]:
        stmt = (
            select(ContaPagarModel)
            .where(ContaPagarModel.fornecedor_id == fornecedor_id)
            .order_by(ContaPagarModel.data_vencimento)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_status(self, status: str) -> list[ContaPagarModel]:
        stmt = (
            select(ContaPagarModel)
            .where(ContaPagarModel.status == status)
            .order_by(ContaPagarModel.data_vencimento)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_periodo(
        self, data_inicio: date, data_fim: date, skip: int = 0, limit: int = 500
    ) -> list[ContaPagarModel]:
        stmt = (
            select(ContaPagarModel)
            .where(ContaPagarModel.data_vencimento.between(data_inicio, data_fim))
            .order_by(ContaPagarModel.data_vencimento)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def sum_open(self) -> float:
        saldo = (
            ContaPagarModel.valor_original
            - ContaPagarModel.valor_pago
            - ContaPagarModel.desconto
            + ContaPagarModel.juros
            + ContaPagarModel.multa
        )
        stmt = select(func.sum(saldo)).where(
            ContaPagarModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL])
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)

    async def sum_overdue(self) -> float:
        hoje = date.today()
        saldo = (
            ContaPagarModel.valor_original
            - ContaPagarModel.valor_pago
            - ContaPagarModel.desconto
            + ContaPagarModel.juros
            + ContaPagarModel.multa
        )
        stmt = select(func.sum(saldo)).where(
            ContaPagarModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]),
            ContaPagarModel.data_vencimento < hoje,
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)
