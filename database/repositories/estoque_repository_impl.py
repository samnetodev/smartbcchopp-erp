from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.estoque import EstoqueModel
from database.models.produto import ProdutoModel
from database.repositories.base_repository import BaseRepository


class EstoqueRepositoryImpl(BaseRepository[EstoqueModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, EstoqueModel)

    async def find_by_produto_deposito(
        self, produto_id: UUID, deposito_id: UUID, lote_id: UUID | None = None
    ) -> list[EstoqueModel]:
        stmt = (
            select(EstoqueModel)
            .where(EstoqueModel.produto_id == produto_id)
            .where(EstoqueModel.deposito_id == deposito_id)
        )
        if lote_id:
            stmt = stmt.where(EstoqueModel.lote_id == lote_id)
        else:
            stmt = stmt.where(EstoqueModel.lote_id.is_(None))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_one_by_produto_deposito(
        self, produto_id: UUID, deposito_id: UUID, lote_id: UUID | None = None
    ) -> EstoqueModel | None:
        rows = await self.find_by_produto_deposito(produto_id, deposito_id, lote_id)
        return rows[0] if rows else None

    async def saldo_total_produto(self, produto_id: UUID) -> float:
        stmt = select(func.sum(EstoqueModel.quantidade_atual)).where(
            EstoqueModel.produto_id == produto_id
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)

    async def find_by_deposito(self, deposito_id: UUID) -> list[EstoqueModel]:
        stmt = (
            select(EstoqueModel)
            .where(EstoqueModel.deposito_id == deposito_id)
            .order_by(EstoqueModel.updated_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_produto(self, produto_id: UUID) -> list[EstoqueModel]:
        stmt = (
            select(EstoqueModel)
            .where(EstoqueModel.produto_id == produto_id)
            .order_by(EstoqueModel.deposito_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_estoque_critico(self, deposito_id: UUID | None = None) -> list[EstoqueModel]:
        stmt = (
            select(EstoqueModel)
            .join(ProdutoModel)
            .where(EstoqueModel.quantidade_atual <= ProdutoModel.estoque_minimo)
            .order_by(EstoqueModel.quantidade_atual.asc())
        )
        if deposito_id:
            stmt = stmt.where(EstoqueModel.deposito_id == deposito_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def valor_total_estoque(self) -> float:
        from sqlalchemy import literal_column

        stmt = select(
            func.sum(EstoqueModel.quantidade_atual * literal_column("produto.preco_custo"))
        ).join(ProdutoModel)
        result = await self._session.execute(stmt)
        return float(result.scalar_one() or 0)

    async def count_by_deposito(self, deposito_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(EstoqueModel)
            .where(EstoqueModel.deposito_id == deposito_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
