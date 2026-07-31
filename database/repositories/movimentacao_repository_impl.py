from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.movimentacao import MovimentacaoModel, MovimentacaoTipo
from database.repositories.base_repository import BaseRepository


class MovimentacaoRepositoryImpl(BaseRepository[MovimentacaoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MovimentacaoModel)

    async def find_by_produto(self, produto_id: UUID, limit: int = 50) -> list[MovimentacaoModel]:
        stmt = (
            select(MovimentacaoModel)
            .where(MovimentacaoModel.produto_id == produto_id)
            .order_by(MovimentacaoModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_tipo(
        self, tipo: MovimentacaoTipo, skip: int = 0, limit: int = 100
    ) -> list[MovimentacaoModel]:
        stmt = (
            select(MovimentacaoModel)
            .where(MovimentacaoModel.tipo == tipo)
            .order_by(MovimentacaoModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_tipo(self, tipo: MovimentacaoTipo) -> int:
        stmt = (
            select(func.count())
            .select_from(MovimentacaoModel)
            .where(MovimentacaoModel.tipo == tipo)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def find_all_filtered(
        self,
        tipo: MovimentacaoTipo | None = None,
        produto_id: UUID | None = None,
        deposito_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MovimentacaoModel]:
        stmt = select(MovimentacaoModel)
        if tipo:
            stmt = stmt.where(MovimentacaoModel.tipo == tipo)
        if produto_id:
            stmt = stmt.where(MovimentacaoModel.produto_id == produto_id)
        if deposito_id:
            stmt = stmt.where(
                (MovimentacaoModel.deposito_id_origem == deposito_id)
                | (MovimentacaoModel.deposito_id_destino == deposito_id)
            )
        stmt = stmt.order_by(MovimentacaoModel.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        tipo: MovimentacaoTipo | None = None,
        produto_id: UUID | None = None,
        deposito_id: UUID | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(MovimentacaoModel)
        if tipo:
            stmt = stmt.where(MovimentacaoModel.tipo == tipo)
        if produto_id:
            stmt = stmt.where(MovimentacaoModel.produto_id == produto_id)
        if deposito_id:
            stmt = stmt.where(
                (MovimentacaoModel.deposito_id_origem == deposito_id)
                | (MovimentacaoModel.deposito_id_destino == deposito_id)
            )
        result = await self._session.execute(stmt)
        return result.scalar_one()
