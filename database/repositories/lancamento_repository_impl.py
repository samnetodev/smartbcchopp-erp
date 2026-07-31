from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.conta_pagar import ContaPagarModel
from database.models.conta_receber import ContaReceberModel, ContaStatus
from database.models.lancamento import LancamentoModel, LancamentoTipo
from database.repositories.base_repository import BaseRepository


class LancamentoRepositoryImpl(BaseRepository[LancamentoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, LancamentoModel)

    async def find_by_periodo(
        self, data_inicio: date, data_fim: date, skip: int = 0, limit: int = 500
    ) -> list[LancamentoModel]:
        stmt = (
            select(LancamentoModel)
            .where(LancamentoModel.data.between(data_inicio, data_fim))
            .order_by(LancamentoModel.data)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def sum_by_periodo(self, data_inicio: date, data_fim: date) -> tuple[float, float]:
        stmt = select(
            func.sum(LancamentoModel.valor).filter(LancamentoModel.tipo == LancamentoTipo.ENTRADA),
            func.sum(LancamentoModel.valor).filter(LancamentoModel.tipo == LancamentoTipo.SAIDA),
        ).where(LancamentoModel.data.between(data_inicio, data_fim))
        result = await self._session.execute(stmt)
        row = result.one()
        return float(row[0] or 0), float(row[1] or 0)

    async def saldo_ate_data(self, data: date) -> float:
        entradas = select(func.sum(LancamentoModel.valor)).where(
            LancamentoModel.data <= data, LancamentoModel.tipo == LancamentoTipo.ENTRADA
        )
        saidas = select(func.sum(LancamentoModel.valor)).where(
            LancamentoModel.data <= data, LancamentoModel.tipo == LancamentoTipo.SAIDA
        )
        e = await self._session.execute(entradas)
        s = await self._session.execute(saidas)
        return float(e.scalar_one() or 0) - float(s.scalar_one() or 0)

    async def sum_by_categoria_periodo(
        self, data_inicio: date, data_fim: date
    ) -> list[dict[str, Any]]:
        stmt = (
            select(
                LancamentoModel.categoria,
                LancamentoModel.tipo,
                func.sum(LancamentoModel.valor).label("total"),
            )
            .where(LancamentoModel.data.between(data_inicio, data_fim))
            .group_by(LancamentoModel.categoria, LancamentoModel.tipo)
            .order_by(LancamentoModel.categoria)
        )
        result = await self._session.execute(stmt)
        return [
            {"categoria": row.categoria, "tipo": row.tipo.value, "total": float(row.total)}
            for row in result.all()
        ]

    async def conciliar(
        self, lancamento_id: UUID, data_conciliacao: date,
    ) -> LancamentoModel | None:
        lanc = await self.find_by_id(lancamento_id)
        if lanc:
            lanc.conciliado = True
            lanc.data_conciliacao = data_conciliacao
        return lanc


class ContaReceberSaldoRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def entradas_previstas_periodo(
        self, data_inicio: date, data_fim: date
    ) -> float:
        saldo = (
            ContaReceberModel.valor_original
            - ContaReceberModel.valor_pago
            - ContaReceberModel.desconto
            + ContaReceberModel.juros
            + ContaReceberModel.multa
        )
        stmt = select(func.sum(saldo)).where(
            ContaReceberModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]),
            ContaReceberModel.data_vencimento.between(data_inicio, data_fim),
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)

    async def total_recebido_periodo(self, data_inicio: date, data_fim: date) -> float:
        stmt = select(func.sum(ContaReceberModel.valor_pago)).where(
            ContaReceberModel.status == ContaStatus.PAGO,
            ContaReceberModel.data_pagamento.between(data_inicio, data_fim),
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)

    async def total_receber_vencido(self, data_ref: date) -> float:
        saldo = (
            ContaReceberModel.valor_original
            - ContaReceberModel.valor_pago
            - ContaReceberModel.desconto
            + ContaReceberModel.juros
            + ContaReceberModel.multa
        )
        stmt = select(func.sum(saldo)).where(
            ContaReceberModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]),
            ContaReceberModel.data_vencimento < data_ref,
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)

    async def find_vencidos_com_cliente(
        self, data_ref: date
    ) -> list[ContaReceberModel]:
        from sqlalchemy.orm import selectinload

        stmt = (
            select(ContaReceberModel)
            .options(selectinload(ContaReceberModel.cliente))
            .where(
                ContaReceberModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]),
                ContaReceberModel.data_vencimento < data_ref,
            )
            .order_by(ContaReceberModel.data_vencimento)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class ContaPagarSaldoRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def saidas_previstas_periodo(
        self, data_inicio: date, data_fim: date
    ) -> float:
        saldo = (
            ContaPagarModel.valor_original
            - ContaPagarModel.valor_pago
            - ContaPagarModel.desconto
            + ContaPagarModel.juros
            + ContaPagarModel.multa
        )
        stmt = select(func.sum(saldo)).where(
            ContaPagarModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]),
            ContaPagarModel.data_vencimento.between(data_inicio, data_fim),
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)

    async def total_pago_periodo(self, data_inicio: date, data_fim: date) -> float:
        stmt = select(func.sum(ContaPagarModel.valor_pago)).where(
            ContaPagarModel.status == ContaStatus.PAGO,
            ContaPagarModel.data_pagamento.between(data_inicio, data_fim),
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)

    async def total_pagar_vencido(self, data_ref: date) -> float:
        saldo = (
            ContaPagarModel.valor_original
            - ContaPagarModel.valor_pago
            - ContaPagarModel.desconto
            + ContaPagarModel.juros
            + ContaPagarModel.multa
        )
        stmt = select(func.sum(saldo)).where(
            ContaPagarModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]),
            ContaPagarModel.data_vencimento < data_ref,
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)
