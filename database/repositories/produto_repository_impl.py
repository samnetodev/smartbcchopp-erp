from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.produto import ProdutoModel
from database.repositories.base_repository import BaseRepository


class ProdutoRepositoryImpl(BaseRepository[ProdutoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProdutoModel)

    async def find_by_codigo(self, codigo: str) -> ProdutoModel | None:
        stmt = select(ProdutoModel).where(ProdutoModel.codigo == codigo)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_codigo_barras(self, codigo_barras: str) -> ProdutoModel | None:
        stmt = select(ProdutoModel).where(ProdutoModel.codigo_barras == codigo_barras)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(self, term: str, skip: int = 0, limit: int = 20) -> list[ProdutoModel]:
        stmt = (
            select(ProdutoModel)
            .where(
                or_(
                    ProdutoModel.nome.ilike(f"%{term}%"),
                    ProdutoModel.codigo.ilike(f"%{term}%"),
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(ProdutoModel.nome)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_categoria(
        self, categoria: str, skip: int = 0, limit: int = 100
    ) -> list[ProdutoModel]:
        stmt = (
            select(ProdutoModel)
            .where(ProdutoModel.categoria == categoria)
            .offset(skip)
            .limit(limit)
            .order_by(ProdutoModel.nome)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
