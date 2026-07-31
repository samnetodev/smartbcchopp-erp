from typing import Any
from uuid import UUID

from sqlalchemy import desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.whatsapp_conversa import (
    WhatsappConversaModel,
    WhatsappConversaStatus,
    WhatsappMensagemModel,
)
from database.repositories.base_repository import BaseRepository


class WhatsappConversaRepositoryImpl(BaseRepository[WhatsappConversaModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WhatsappConversaModel)

    async def find_by_telefone(self, telefone: str) -> WhatsappConversaModel | None:
        stmt = select(WhatsappConversaModel).where(WhatsappConversaModel.telefone == telefone)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_ativas(self, skip: int = 0, limit: int = 50) -> list[WhatsappConversaModel]:
        stmt = (
            select(WhatsappConversaModel)
            .where(WhatsappConversaModel.status == WhatsappConversaStatus.ATIVA)
            .order_by(desc(WhatsappConversaModel.ultima_data))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self, term: str, skip: int = 0, limit: int = 20
    ) -> list[WhatsappConversaModel]:
        stmt = (
            select(WhatsappConversaModel)
            .where(
                or_(
                    WhatsappConversaModel.telefone.ilike(f"%{term}%"),
                    WhatsappConversaModel.nome_contato.ilike(f"%{term}%"),
                )
            )
            .order_by(desc(WhatsappConversaModel.ultima_data))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def atualizar_contexto(self, conversa_id: UUID, contexto: dict[str, Any]) -> None:
        stmt = (
            update(WhatsappConversaModel)
            .where(WhatsappConversaModel.id == conversa_id)
            .values(contexto=contexto)
        )
        await self._session.execute(stmt)

    async def atualizar_agente(self, conversa_id: UUID, agente: str | None) -> None:
        stmt = (
            update(WhatsappConversaModel)
            .where(WhatsappConversaModel.id == conversa_id)
            .values(agente_ativo=agente)
        )
        await self._session.execute(stmt)

    async def atualizar_ultima_mensagem(
        self, conversa_id: UUID, texto: str, pedido_ctx: dict[str, Any] | None = None
    ) -> None:
        values: dict[str, Any] = {
            "ultima_mensagem": texto,
            "ultima_data": func.now(),
        }
        if pedido_ctx is not None:
            values["pedido_ctx"] = pedido_ctx
        stmt = (
            update(WhatsappConversaModel)
            .where(WhatsappConversaModel.id == conversa_id)
            .values(**values)
        )
        await self._session.execute(stmt)

    async def vincular_cliente(self, conversa_id: UUID, cliente_id: UUID) -> None:
        stmt = (
            update(WhatsappConversaModel)
            .where(WhatsappConversaModel.id == conversa_id)
            .values(cliente_id=cliente_id)
        )
        await self._session.execute(stmt)

    async def count_ativas(self) -> int:
        stmt = (
            select(func.count())
            .select_from(WhatsappConversaModel)
            .where(WhatsappConversaModel.status == WhatsappConversaStatus.ATIVA)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def listar_mensagens(
        self, conversa_id: UUID, limit: int = 50
    ) -> list[WhatsappMensagemModel]:
        stmt = (
            select(WhatsappMensagemModel)
            .where(WhatsappMensagemModel.conversa_id == conversa_id)
            .order_by(desc(WhatsappMensagemModel.data_recebida))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def salvar_mensagem(self, mensagem: WhatsappMensagemModel) -> WhatsappMensagemModel:
        self._session.add(mensagem)
        await self._session.flush()
        return mensagem


class MensagemRepositoryImpl(BaseRepository[WhatsappMensagemModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WhatsappMensagemModel)
