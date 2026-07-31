from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.boleto import BoletoModel, BoletoStatus
from database.repositories.base_repository import BaseRepository


class BoletoRepositoryImpl(BaseRepository[BoletoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, BoletoModel)

    async def find_by_conta_receber(self, conta_receber_id: UUID) -> list[BoletoModel]:
        stmt = (
            select(BoletoModel)
            .where(BoletoModel.conta_receber_id == conta_receber_id)
            .order_by(BoletoModel.data_emissao.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_nosso_numero(self, nosso_numero: str) -> BoletoModel | None:
        stmt = select(BoletoModel).where(BoletoModel.nosso_numero == nosso_numero)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_status(self, status: str) -> int:
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(BoletoModel)
            .where(BoletoModel.status == status)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def registrar_pagamento(
        self, boleto_id: UUID, data_pagamento: date, valor_pago: float
    ) -> BoletoModel | None:
        boleto = await self.find_by_id(boleto_id)
        if boleto:
            boleto.status = BoletoStatus.PAGO
            boleto.data_pagamento = data_pagamento
            boleto.valor_pago = valor_pago
        return boleto
