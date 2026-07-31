from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cliente import ClienteModel
from database.repositories.base_repository import BaseRepository


class ClienteRepositoryImpl(BaseRepository[ClienteModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ClienteModel)

    async def find_by_cpf_cnpj(self, cpf_cnpj: str) -> ClienteModel | None:
        stmt = select(ClienteModel).where(ClienteModel.cpf_cnpj == cpf_cnpj)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(self, term: str, skip: int = 0, limit: int = 20) -> list[ClienteModel]:
        stmt = (
            select(ClienteModel)
            .where(
                or_(
                    ClienteModel.nome_razao_social.ilike(f"%{term}%"),
                    ClienteModel.nome_fantasia.ilike(f"%{term}%"),
                    ClienteModel.cpf_cnpj.ilike(f"%{term}%"),
                )
            )
            .where(ClienteModel.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .order_by(ClienteModel.nome_razao_social)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_all_active(self, skip: int = 0, limit: int = 100) -> list[ClienteModel]:
        stmt = (
            select(ClienteModel)
            .where(ClienteModel.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .order_by(ClienteModel.nome_razao_social)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_active(self) -> int:
        from sqlalchemy import func

        stmt = (
            select(func.count()).select_from(ClienteModel).where(ClienteModel.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
