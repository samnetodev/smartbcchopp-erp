from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from core.application.usecases.whatsapp.processar_mensagem import ProcessarMensagemWhatsAppUseCase


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    return session


def _setup_conversa_repo_find(mock_session, conversa=None) -> AsyncMock:
    repo = AsyncMock()
    repo.find_by_telefone = AsyncMock(return_value=conversa)
    repo.save = AsyncMock(return_value=conversa)
    repo.salvar_mensagem = AsyncMock()
    repo.atualizar_ultima_mensagem = AsyncMock()
    repo.atualizar_agente = AsyncMock()
    return repo


class TestProcessarMensagem:
    @patch("core.application.usecases.whatsapp.processar_mensagem.WhatsappConversaRepositoryImpl")
    async def test_mensagem_aleatoria_retorna_fallback(
        self, mock_repo_cls, mock_session
    ) -> None:
        repo = AsyncMock()
        repo.find_by_telefone = AsyncMock(return_value=None)
        repo.save = AsyncMock()
        repo.salvar_mensagem = AsyncMock()
        repo.atualizar_ultima_mensagem = AsyncMock()
        repo.atualizar_agente = AsyncMock()
        mock_repo_cls.return_value = repo

        use_case = ProcessarMensagemWhatsAppUseCase(mock_session)
        result = await use_case.executar(
            telefone="5511999999999",
            mensagem="aksjdhflaksjdhf",
        )

        assert result.value["resposta"] is not None
        assert "Não entendi" in result.value["resposta"] or "entendi" in result.value["resposta"]

    @patch("core.application.usecases.whatsapp.processar_mensagem.WhatsappConversaRepositoryImpl")
    async def test_saudacao_retorna_menu(self, mock_repo_cls, mock_session) -> None:
        repo = AsyncMock()
        repo.find_by_telefone = AsyncMock(return_value=None)
        repo.save = AsyncMock()
        repo.salvar_mensagem = AsyncMock()
        repo.atualizar_ultima_mensagem = AsyncMock()
        repo.atualizar_agente = AsyncMock()
        mock_repo_cls.return_value = repo

        use_case = ProcessarMensagemWhatsAppUseCase(mock_session)
        result = await use_case.executar(
            telefone="5511999999999",
            mensagem="Olá",
        )

        assert result.value["resposta"] is not None
        resp = result.value["resposta"].lower()
        assert "bem-vindo" in resp or "ajudar" in resp

    @patch("core.application.usecases.whatsapp.processar_mensagem.WhatsappConversaRepositoryImpl")
    async def test_erro_no_processamento_retorna_failure(self, mock_repo_cls, mock_session) -> None:
        repo = AsyncMock()
        repo.find_by_telefone = AsyncMock(side_effect=Exception("DB error"))
        mock_repo_cls.return_value = repo

        use_case = ProcessarMensagemWhatsAppUseCase(mock_session)
        result = await use_case.executar(
            mensagem="teste",
            telefone="5511999999999",
        )

        assert result.error is not None

    @patch("core.application.usecases.whatsapp.processar_mensagem.WhatsappConversaRepositoryImpl")
    async def test_conversa_existente_reutilizada(self, mock_repo_cls, mock_session) -> None:
        conversa_id = uuid4()
        conversa = AsyncMock()
        conversa.id = conversa_id
        conversa.telefone = "5511999999999"
        conversa.contexto = {}
        conversa.cliente_id = None

        repo = AsyncMock()
        repo.find_by_telefone = AsyncMock(return_value=conversa)
        repo.salvar_mensagem = AsyncMock()
        repo.atualizar_ultima_mensagem = AsyncMock()
        repo.atualizar_agente = AsyncMock()
        mock_repo_cls.return_value = repo

        use_case = ProcessarMensagemWhatsAppUseCase(mock_session)
        result = await use_case.executar(
            mensagem="Olá",
            telefone="5511999999999",
        )

        assert result.value["conversa_id"] == conversa_id
        repo.find_by_telefone.assert_called_once_with("5511999999999")
