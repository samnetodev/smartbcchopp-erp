from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.base import Base

M = TypeVar("M", bound=Base)


class BaseRepository(Generic[M]):  # noqa: UP046
    def __init__(self, session: AsyncSession, model: type[M]) -> None:
        self._session = session
        self._model = model

    async def find_by_id(self, id: UUID) -> M | None:
        return await self._session.get(self._model, id)

    async def find_all(self, skip: int = 0, limit: int = 100) -> list[M]:
        stmt = select(self._model).offset(skip).limit(limit).order_by(self._model.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self._model)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def save(self, instance: M) -> M:
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def delete(self, id: UUID) -> bool:
        stmt = delete(self._model).where(self._model.id == id).returning(self._model.id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
