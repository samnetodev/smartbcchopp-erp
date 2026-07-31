from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_async_session_factory
from database.unit_of_work import AsyncUnitOfWork


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_async_session_factory()
    async with factory() as session:
        yield session


async def get_uow(session: AsyncSession) -> AsyncUnitOfWork:
    return AsyncUnitOfWork(session)


def get_uow_from_session(session: AsyncSession) -> AsyncUnitOfWork:
    return AsyncUnitOfWork(session)
