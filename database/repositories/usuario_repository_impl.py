from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.usuario import UsuarioModel
from database.repositories.base_repository import BaseRepository


class UsuarioRepositoryImpl(BaseRepository[UsuarioModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UsuarioModel)

    async def find_by_username(self, username: str) -> UsuarioModel | None:
        stmt = select(UsuarioModel).where(UsuarioModel.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> UsuarioModel | None:
        stmt = select(UsuarioModel).where(UsuarioModel.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, id: UUID | str) -> UsuarioModel | None:
        if isinstance(id, str):
            id = UUID(id)
        return await self._session.get(UsuarioModel, id)

    async def save(self, usuario: UsuarioModel) -> UsuarioModel:
        self._session.add(usuario)
        await self._session.flush()
        return usuario
