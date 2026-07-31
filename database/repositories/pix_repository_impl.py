from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.pix_cobranca import PixCobrancaModel, PixStatus
from database.repositories.base_repository import BaseRepository


class PixCobrancaRepositoryImpl(BaseRepository[PixCobrancaModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PixCobrancaModel)

    async def find_by_conta_receber(self, conta_receber_id: UUID) -> list[PixCobrancaModel]:
        stmt = (
            select(PixCobrancaModel)
            .where(PixCobrancaModel.conta_receber_id == conta_receber_id)
            .order_by(PixCobrancaModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_txid(self, txid: str) -> PixCobrancaModel | None:
        stmt = select(PixCobrancaModel).where(PixCobrancaModel.txid == txid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_status(self, status: str) -> int:
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(PixCobrancaModel)
            .where(PixCobrancaModel.status == status)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def confirmar_pagamento(
        self, pix_id: UUID, data_pagamento: datetime, end_to_end_id: str
    ) -> PixCobrancaModel | None:
        pix = await self.find_by_id(pix_id)
        if pix:
            pix.status = PixStatus.CONCLUIDO
            pix.data_pagamento = data_pagamento
            pix.end_to_end_id = end_to_end_id
        return pix
