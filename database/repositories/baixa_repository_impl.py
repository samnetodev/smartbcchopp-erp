from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.financeiro_baixa import BaixaModel, BaixaTipo
from database.repositories.base_repository import BaseRepository


class BaixaRepositoryImpl(BaseRepository[BaixaModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, BaixaModel)

    async def find_by_periodo(
        self, data_inicio: date, data_fim: date, skip: int = 0, limit: int = 500
    ) -> list[BaixaModel]:
        stmt = (
            select(BaixaModel)
            .where(BaixaModel.data_baixa.between(data_inicio, data_fim))
            .order_by(BaixaModel.data_baixa.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def sum_by_periodo(self, data_inicio: date, data_fim: date) -> tuple[float, float]:
        stmt = select(
            func.sum(BaixaModel.valor).filter(BaixaModel.tipo == BaixaTipo.RECEBIMENTO),
            func.sum(BaixaModel.valor).filter(BaixaModel.tipo == BaixaTipo.PAGAMENTO),
        ).where(BaixaModel.data_baixa.between(data_inicio, data_fim))
        result = await self._session.execute(stmt)
        row = result.one()
        return float(row[0] or 0), float(row[1] or 0)

    async def find_by_conta_receber(self, conta_receber_id: UUID) -> list[BaixaModel]:
        stmt = (
            select(BaixaModel)
            .where(BaixaModel.conta_receber_id == conta_receber_id)
            .order_by(BaixaModel.data_baixa.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_conta_pagar(self, conta_pagar_id: UUID) -> list[BaixaModel]:
        stmt = (
            select(BaixaModel)
            .where(BaixaModel.conta_pagar_id == conta_pagar_id)
            .order_by(BaixaModel.data_baixa.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
