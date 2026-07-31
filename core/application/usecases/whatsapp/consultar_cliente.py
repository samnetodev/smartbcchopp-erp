
from sqlalchemy.ext.asyncio import AsyncSession

from core.shared.result import Failure, Success
from database.models.cliente import ClienteModel
from database.repositories.cliente_repository_impl import ClienteRepositoryImpl


class ConsultarClienteWhatsAppUseCase:
    """Consulta dados de cliente a partir de um termo de busca."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cliente_repo = ClienteRepositoryImpl(session)

    async def por_telefone(self, telefone: str) -> Success[ClienteModel] | Failure[str]:
        try:
            from database.repositories.whatsapp_repository_impl import (
                WhatsappConversaRepositoryImpl,
            )

            whatsapp_repo = WhatsappConversaRepositoryImpl(self._session)
            conversa = await whatsapp_repo.find_by_telefone(telefone)
            if conversa and conversa.cliente_id:
                cliente = await self._cliente_repo.find_by_id(conversa.cliente_id)
                if cliente:
                    return Success(cliente)
            return Failure("cliente_nao_encontrado")
        except Exception as e:
            return Failure(str(e))

    async def por_termo(self, termo: str) -> Success[list[ClienteModel]] | Failure[str]:
        try:
            resultados = await self._cliente_repo.search(termo, limit=5)
            if resultados:
                return Success(resultados)
            return Failure("cliente_nao_encontrado")
        except Exception as e:
            return Failure(str(e))
