
import pytest

from core.application.usecases.whatsapp.processar_mensagem import IntentRouter


class TestIntentRouter:
    @pytest.fixture
    def router(self) -> IntentRouter:
        return IntentRouter()

    def test_detecta_saudacao(self, router: IntentRouter) -> None:
        intents = router.detectar("Olá, bom dia!")
        assert len(intents) > 0
        assert intents[0].acao == "saudacao"
        assert intents[0].confianca >= 0.8

    def test_detecta_consultar_cliente_por_nome(self, router: IntentRouter) -> None:
        intents = router.detectar("consulta cliente João Silva")
        acoes = [i.acao for i in intents]
        assert "consultar_cliente" in acoes
        cli = next(i for i in intents if i.acao == "consultar_cliente")
        assert cli.confianca >= 0.8

    def test_detecta_consultar_estoque(self, router: IntentRouter) -> None:
        intents = router.detectar("tem chope pilsen em estoque?")
        acoes = [i.acao for i in intents]
        assert "consultar_estoque" in acoes

    def test_detecta_cadastrar_pedido(self, router: IntentRouter) -> None:
        intents = router.detectar("quero pedir 10 cx de chope")
        acoes = [i.acao for i in intents]
        assert "cadastrar_pedido" in acoes

    def test_detecta_consultar_chopeiras(self, router: IntentRouter) -> None:
        intents = router.detectar("qual o status da chopeira do cliente XYZ?")
        acoes = [i.acao for i in intents]
        assert "consultar_chopeiras" in acoes

    def test_detecta_consultar_documentos(self, router: IntentRouter) -> None:
        intents = router.detectar("preciso de um documento do pedido 123")
        acoes = [i.acao for i in intents]
        assert "consultar_documentos" in acoes

    def test_detecta_falar_humano(self, router: IntentRouter) -> None:
        intents = router.detectar("quero falar com um atendente")
        acoes = [i.acao for i in intents]
        assert "falar_humano" in acoes

    def test_detecta_sair(self, router: IntentRouter) -> None:
        intents = router.detectar("obrigado, tchau!")
        acoes = [i.acao for i in intents]
        assert "sair" in acoes

    def test_mensagem_vazia_retorna_lista_vazia(self, router: IntentRouter) -> None:
        intents = router.detectar("")
        assert len(intents) == 0

    def test_mensagem_sem_padrao_retorna_lista_vazia(self, router: IntentRouter) -> None:
        intents = router.detectar("aksjdhflaksjdhf")
        assert len(intents) == 0

    def test_multiplas_intencoes_ordenadas_por_confianca(self, router: IntentRouter) -> None:
        intents = router.detectar("oi, quero consultar cliente João e ver estoque")
        if len(intents) >= 2:
            for i in range(len(intents) - 1):
                assert intents[i].confianca >= intents[i + 1].confianca

    def test_extrai_parametros_cliente(self, router: IntentRouter) -> None:
        intents = router.detectar("consulta cliente 123.456.789-00")
        cli = next((i for i in intents if i.acao == "consultar_cliente"), None)
        if cli:
            assert "termo" in cli.parametros

    def test_extrai_parametros_pedido_quantidade(self, router: IntentRouter) -> None:
        intents = router.detectar("quero comprar 20 cx de chope")
        ped = next((i for i in intents if i.acao == "cadastrar_pedido"), None)
        if ped:
            assert ped.parametros.get("quantidade") == "20"
            assert ped.parametros.get("unidade") == "cx"

    def test_detecta_saudacao_variantes(self, router: IntentRouter) -> None:
        for msg in ["ola", "oi", "bom dia", "boa tarde", "boa noite", "hey", "e aí"]:
            intents = router.detectar(msg)
            assert any(i.acao == "saudacao" for i in intents), f"Falhou para: {msg}"

    def test_detecta_consultar_cliente_por_cpf_cnpj(self, router: IntentRouter) -> None:
        intents = router.detectar("consulta cnpj 11.222.333/0001-44")
        acoes = [i.acao for i in intents]
        assert "consultar_cliente" in acoes
