from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.fornecedor import FornecedorModel
from database.repositories.base_repository import BaseRepository


class FornecedorRepositoryImpl(BaseRepository[FornecedorModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FornecedorModel)

    async def find_by_cpf_cnpj(self, cpf_cnpj: str) -> FornecedorModel | None:
        stmt = select(FornecedorModel).where(FornecedorModel.cpf_cnpj == cpf_cnpj)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_categoria(self, categoria: str) -> list[FornecedorModel]:
        stmt = (
            select(FornecedorModel)
            .where(FornecedorModel.categoria == categoria)
            .order_by(FornecedorModel.nome_razao_social)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
