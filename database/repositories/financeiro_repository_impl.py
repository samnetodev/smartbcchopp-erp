from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.conta_pagar import ContaPagarModel
from database.models.conta_receber import ContaReceberModel, ContaStatus
from database.repositories.base_repository import BaseRepository


def _saldo_expression_receber() -> Any:
    return (
        ContaReceberModel.valor_original
        - ContaReceberModel.valor_pago
        - ContaReceberModel.desconto
        + ContaReceberModel.juros
        + ContaReceberModel.multa
    )


def _saldo_expression_pagar() -> Any:
    return (
        ContaPagarModel.valor_original
        - ContaPagarModel.valor_pago
        - ContaPagarModel.desconto
        + ContaPagarModel.juros
        + ContaPagarModel.multa
    )


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

    async def find_abertas_vencidas(self) -> list[ContaReceberModel]:
        hoje = date.today()
        stmt = (
            select(ContaReceberModel)
            .where(ContaReceberModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]))
            .where(ContaReceberModel.data_vencimento < hoje)
            .order_by(ContaReceberModel.data_vencimento)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def total_a_receber(self) -> float:
        saldo = _saldo_expression_receber()
        stmt = select(func.sum(saldo)).where(
            ContaReceberModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL])
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)


class ContaPagarRepositoryImpl(BaseRepository[ContaPagarModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ContaPagarModel)

    async def find_abertas(self) -> list[ContaPagarModel]:
        stmt = (
            select(ContaPagarModel)
            .where(ContaPagarModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]))
            .order_by(ContaPagarModel.data_vencimento)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def total_a_pagar(self) -> float:
        saldo = _saldo_expression_pagar()
        stmt = select(func.sum(saldo)).where(
            ContaPagarModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL])
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)
