import json
import re
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.shared.result import Failure, Success
from database.models.cliente import ClienteModel
from database.models.whatsapp_conversa import (
    WhatsappConversaModel,
    WhatsappConversaStatus,
    WhatsappMensagemModel,
)
from database.repositories.whatsapp_repository_impl import WhatsappConversaRepositoryImpl
from infrastructure.messaging.integrations.whatsapp_client import FakeWhatsAppClient


@dataclass
class WhatsAppContext:
    telefone: str
    nome_contato: str | None = None
    session: AsyncSession | None = None


@dataclass
class Intent:
    """Intenção identificada + dados extraídos."""

    acao: str
    entidade: str | None = None
    parametros: dict[str, Any] = field(default_factory=dict)
    confianca: float = 0.0


class IntentRouter:
    """Detecta intenção em mensagens WhatsApp usando regras + agentes.

    Mapeia mensagens para ações usando keywords dos agentes em
    ``agents/registry/rules.json``.
    """

    # Padrões de intenção por domínio
    CLIENTE_REGEX = r"(cadastro|dados)\s*(do|da)\s*(cliente|empresa)"
    _REGEX_REMOVER_CLIENTE = (
        r"(cliente|empresa|me fala do|info do|dados do|"
        r"dados da|consulta|busca|localiza)\s*"
    )
    _REGEX_REMOVER_ESTOQUE = (
        r"(consulta|tem|vê|verifica|checa|estoque de |"
        r"produto |em estoque|disponível|saldo)\s*"
    )
    _REGEX_REMOVER_PEDIDO = (
        r"(quero|preciso|vou|pedir|comprar|criar|"
        r"registrar|pedido de |novo)\s*"
    )

    PADROES: dict[str, list[tuple[str, float]]] = {
        "consultar_cliente": [
            (r"(consulta|busca|localiza|dados do)\s*(cliente|customer)", 0.9),
            (r"(quem é|me fala do|info do)\s*(cliente|empresa)", 0.9),
            (r"cliente.*telefone|telefone.*cliente", 0.8),
            (r"saldo.*cliente|cliente.*saldo|limite.*cliente", 0.8),
            (r"cpf|cnpj.*consulta", 0.9),
            (r"(consulta|busca).*(cpf|cnpj)", 0.9),
            (CLIENTE_REGEX, 0.8),
        ],
        "cadastrar_pedido": [
            (r"(quero|preciso|vou|gostaria de)\s*(pedir|comprar|encomendar)", 0.9),
            (r"(fazer|criar|abrir|registrar|cadastrar)\s*(um|o)?\s*pedido", 0.9),
            (r"pedido\s*(de|para)\s*\d+", 0.8),
            (r"comprar\s+\d+.*(cx|un|kg|l|pacote)", 0.8),
            (r"(encomenda|compra|pedido).*novo", 0.8),
            (r"quero.*(cx|unidade|peça|fardo)", 0.7),
        ],
        "consultar_estoque": [
            (r"(consulta|tem|vê|verifica|checa)\s*(estoque|produto)", 0.9),
            (r"estoque de |produto |tem .* (em estoque|disponível)", 0.8),
            (r"(quantidade|saldo).*(produto|estoque)", 0.8),
            (r"(tem|possui|disponível) .* (estoque|depósito)", 0.7),
            (r"(código|sku|ean)\s*\d+", 0.7),
        ],
        "consultar_chopeiras": [
            (r"(consulta|status|situação)\s*(da|das?)\s*chopeira", 0.9),
            (r"chopeira.*(cliente|local|instalação)", 0.8),
            (r"(manutenção|defeito|quebrou|problema).*chopeira", 0.9),
            (r"chopeira[s]?\s*(instalada|disponível|status)", 0.8),
            (r"equipamento.*chope|torre.*cerveja", 0.7),
        ],
        "consultar_documentos": [
            (r"(consulta|busca|localiza|pega)\s*(doc|documento|arquivo)", 0.9),
            (r"(enviar|manda|precisa)\s*(doc|documento|arquivo|anexo)", 0.8),
            (r"documento.*(cliente|pedido|compra|fornecedor)", 0.8),
            (r"(nota|nf|nfe|xml|danfe)", 0.8),
            (r"anexo.*pedido|pedido.*anexo", 0.7),
        ],
        "falar_humano": [
            (r"(fal[ae]r|quero)\s*(com|falar com)\s*(humano|atendente|suporte)", 0.9),
            (r"(atendente|humano|pessoa)", 0.8),
            (r"transferir|transferência.*atendente", 0.9),
        ],
        "sair": [
            (r"(tchau|obrigado|valeu|flw|fui|bye|até logo|sair)", 0.7),
        ],
        "saudacao": [
            (r"^(ola|olá|oi|oie|bom dia|boa tarde|boa noite|hey|e aí)", 0.8),
            (r"(começar|iniciar|menu|opções|opcao)", 0.6),
        ],
    }

    def __init__(self) -> None:
        self._cache = json.dumps

    def detectar(self, texto: str) -> list[Intent]:
        texto_clean = texto.strip().lower()
        intents: list[Intent] = []

        for acao, padroes in self.PADROES.items():
            melhor_conf = 0.0
            params: dict[str, Any] = {}

            for regex, peso in padroes:
                match = re.search(regex, texto_clean)
                if match:
                    if peso > melhor_conf:
                        melhor_conf = peso
                        grupos = match.groups()
                        if acao == "consultar_cliente" and grupos:
                            params["termo"] = re.sub(
                                self._REGEX_REMOVER_CLIENTE, "", texto_clean,
                            ).strip()
                        elif acao == "consultar_estoque" and grupos:
                            params["produto"] = re.sub(
                                self._REGEX_REMOVER_ESTOQUE, "", texto_clean,
                            ).strip()
                        elif acao in ("cadastrar_pedido",):
                            qty_match = re.search(
                                r"(\d+)\s*(cx|un|kg|l|pacote|fardo)", texto_clean,
                            )
                            if qty_match:
                                params["quantidade"] = qty_match.group(1)
                                params["unidade"] = qty_match.group(2)
                            prod = re.sub(
                                self._REGEX_REMOVER_PEDIDO, "", texto_clean,
                            ).strip()
                            if prod:
                                params["produto"] = prod

            if melhor_conf > 0:
                intents.append(Intent(acao=acao, parametros=params, confianca=melhor_conf))

        return sorted(intents, key=lambda i: i.confianca, reverse=True)


class ProcessarMensagemWhatsAppUseCase:
    """Fluxo principal de recebimento e resposta de mensagens WhatsApp."""

    def __init__(
        self,
        session: AsyncSession,
        whatsapp_client: FakeWhatsAppClient | None = None,
    ) -> None:
        self._session = session
        self._repo = WhatsappConversaRepositoryImpl(session)
        self._router = IntentRouter()
        self._whatsapp = whatsapp_client

    async def executar(
        self,
        telefone: str,
        mensagem: str,
        nome_contato: str | None = None,
    ) -> Success[dict[str, Any]] | Failure[str]:
        try:
            # 1. Obter ou criar conversa
            conversa = await self._repo.find_by_telefone(telefone)
            if not conversa:
                conversa = WhatsappConversaModel(
                    telefone=telefone,
                    nome_contato=nome_contato,
                    status=WhatsappConversaStatus.ATIVA,
                )
                await self._repo.save(conversa)
                await self._session.flush()

            # 2. Salvar mensagem recebida
            msg_model = WhatsappMensagemModel(
                remetente=telefone,
                conteudo=mensagem,
                tipo="texto",
                direcao="entrada",
                conversa_id=conversa.id,
            )
            await self._repo.salvar_mensagem(msg_model)

            # 3. Atualizar metadados da conversa
            await self._repo.atualizar_ultima_mensagem(conversa.id, mensagem)

            # 4. Detectar intenção
            intents = self._router.detectar(mensagem)
            if not intents:
                resposta = self._resposta_fallback(conversa)
            else:
                intent = intents[0]
                await self._repo.atualizar_agente(conversa.id, intent.acao)
                resposta = await self._executar_intencao(intent, conversa, mensagem)

            # 5. Salvar resposta como mensagem de saída
            resposta_msg = WhatsappMensagemModel(
                remetente=telefone,
                conteudo=resposta,
                tipo="texto",
                direcao="saida",
                conversa_id=conversa.id,
            )
            await self._repo.salvar_mensagem(resposta_msg)
            await self._repo.atualizar_ultima_mensagem(conversa.id, resposta)

            # 6. Enviar via WhatsApp
            if self._whatsapp:
                await self._whatsapp.send_text(to=telefone, text=resposta)

            from database.unit_of_work import AsyncUnitOfWork

            uow = AsyncUnitOfWork(self._session)
            await uow.commit()

            return Success({
                "conversa_id": conversa.id,
                "resposta": resposta,
                "mensagem_id": msg_model.id,
            })
        except Exception as e:
            await self._session.rollback()
            return Failure(str(e))

    async def _executar_intencao(
        self, intent: Intent, conversa: WhatsappConversaModel, mensagem_original: str
    ) -> str:
        acao = intent.acao

        if acao == "saudacao":
            return (
                "Olá! 👋 Bem-vindo ao SmartBcChopp!\n\n"
                "Eu sou o assistente virtual. Como posso ajudar?\n\n"
                "📋 *Consultar cliente*\n"
                "📦 *Consultar estoque*\n"
                "🛒 *Cadastrar pedido*\n"
                "🍺 *Status de chopeiras*\n"
                "📄 *Consultar documentos*\n\n"
                "É só me falar o que precisa!"
            )

        if acao == "consultar_cliente":
            return await self._consultar_cliente(intent, conversa)

        if acao == "consultar_estoque":
            return await self._consultar_estoque(intent)

        if acao == "consultar_chopeiras":
            return await self._consultar_chopeiras(intent)

        if acao == "consultar_documentos":
            return await self._consultar_documentos(intent, conversa)

        if acao == "cadastrar_pedido":
            return await self._iniciar_cadastro_pedido(intent, conversa, mensagem_original)

        if acao == "falar_humano":
            return (
                "Vou transferir seu atendimento para um de nossos consultores. "
                "Em breve alguém entrará em contato pelo WhatsApp. "
                "Se preferir, ligue para (XX) XXXX-XXXX."
            )

        if acao == "sair":
            return (
                "Obrigado pelo contato! 😊\n"
                "Estou à disposição sempre que precisar. "
                "Basta me enviar uma mensagem!"
            )

        return self._resposta_fallback(conversa)

    async def _consultar_cliente(
        self, intent: Intent, conversa: WhatsappConversaModel
    ) -> str:
        termo = intent.parametros.get("termo", "")
        if not termo:
            if conversa.cliente_id:
                from database.repositories.cliente_repository_impl import ClienteRepositoryImpl

                repo = ClienteRepositoryImpl(self._session)
                cliente = await repo.find_by_id(conversa.cliente_id)
                if cliente:
                    return self._formatar_cliente(cliente)
            return (
                "Para consultar um cliente, me informe o nome, CPF/CNPJ ou telefone.\n"
                "Ex: *consulta cliente João* ou *cpf 123.456.789-00*"
            )

        from database.repositories.cliente_repository_impl import ClienteRepositoryImpl

        repo = ClienteRepositoryImpl(self._session)
        resultados = await repo.search(termo, limit=5)

        if not resultados:
            return (
                f"Não encontrei nenhum cliente com *{termo}*."
                " Verifique o termo e tente novamente."
            )

        if len(resultados) == 1:
            await self._repo.vincular_cliente(conversa.id, resultados[0].id)
            return self._formatar_cliente(resultados[0])

        linhas = []
        for i, c in enumerate(resultados, 1):
            tel = c.celular or c.telefone or "-"
            linhas.append(f"{i}. *{c.nome_razao_social}* — {c.cpf_cnpj} — {tel}")
        return "Encontrei vários clientes. Qual deles?\n\n" + "\n".join(linhas)

    async def _consultar_estoque(self, intent: Intent) -> str:
        produto = intent.parametros.get("produto", "")
        if not produto:
            return (
                "Para consultar o estoque, me informe o nome ou código do produto.\n"
                "Ex: *estoque do chope pilsen* ou *produto 1234*"
            )

        from sqlalchemy import select

        from database.models.estoque import EstoqueModel
        from database.models.produto import ProdutoModel

        stmt = (
            select(ProdutoModel, EstoqueModel)
            .join(EstoqueModel, EstoqueModel.produto_id == ProdutoModel.id)
            .where(
                ProdutoModel.nome.ilike(f"%{produto}%")
                | ProdutoModel.codigo.ilike(f"%{produto}%")
            )
            .limit(10)
        )
        result = await self._session.execute(stmt)
        rows = result.all()

        if not rows:
            return f"Não encontrei nenhum produto com *{produto}*."

        linhas = []
        for prod, est in rows:
            baixo = est.quantidade_atual <= (est.estoque_minimo or 0)
            status = "⚠️ Estoque baixo!" if baixo else "✅ OK"
            linhas.append(
                f"*{prod.codigo}* — {prod.nome}\n"
                f"  Saldo: {float(est.quantidade_atual):.2f} {prod.unidade_medida or 'un'} {status}"
            )
        return "\n".join(linhas)

    async def _consultar_chopeiras(self, intent: Intent) -> str:
        from sqlalchemy import select

        from database.models.chopeira import ChopeiraModel
        from database.models.cliente import ClienteModel

        termo = intent.parametros.get("termo", "")
        if termo:
            stmt = (
                select(ChopeiraModel)
                .join(ClienteModel, ClienteModel.id == ChopeiraModel.cliente_id)
                .where(
                    ClienteModel.nome_razao_social.ilike(f"%{termo}%")
                    | ChopeiraModel.codigo_identificacao.ilike(f"%{termo}%")
                    | ChopeiraModel.local_instalacao.ilike(f"%{termo}%")
                )
                .limit(10)
            )
        else:
            stmt = select(ChopeiraModel).limit(10)

        result = await self._session.execute(stmt)
        chopeiras = list(result.scalars().all())

        if not chopeiras:
            return "Nenhuma chopeira encontrada."

        linhas = []
        for c in chopeiras:
            status = {
                "disponivel": "✅ Disponível",
                "instalada": "🍺 Instalada",
                "manutencao": "🔧 Em manutenção",
                "baixada": "❌ Baixada",
            }.get(c.status.value if hasattr(c.status, "value") else str(c.status), c.status)
            local = f" em {c.local_instalacao}" if c.local_instalacao else ""
            tipo_str = c.tipo.value if hasattr(c.tipo, "value") else c.tipo
            linhas.append(
                f"*{c.codigo_identificacao}* — {c.marca} {c.modelo}\n"
                f"  Tipo: {tipo_str} | Status: {status}{local}"
            )
        return "\n".join(linhas)

    async def _consultar_documentos(
        self, intent: Intent, conversa: WhatsappConversaModel
    ) -> str:
        from sqlalchemy import select

        from database.models.documento import DocumentoModel

        stmt = select(DocumentoModel).limit(10)
        result = await self._session.execute(stmt)
        docs = list(result.scalars().all())

        if not docs:
            return "Nenhum documento encontrado."

        linhas = []
        for d in docs:
            entidade = d.entidade_tipo or "-"
            linhas.append(
                f"📄 *{d.nome_original}*\n"
                f"  Tipo: {d.tipo_documento} | Entidade: {entidade}"
            )
        return "\n".join(linhas)

    async def _iniciar_cadastro_pedido(
        self, intent: Intent, conversa: WhatsappConversaModel, mensagem: str
    ) -> str:
        if not conversa.cliente_id:
            return (
                "Para cadastrar um pedido, primeiro preciso saber qual cliente. "
                "Me informe o nome, CPF/CNPJ ou telefone do cliente.\n"
                "Ex: *cliente João Silva*"
            )

        params = intent.parametros
        produto_nome = params.get("produto")
        quantidade = params.get("quantidade")

        if not produto_nome:
            return (
                "Qual produto você deseja pedir?\n"
                "Ex: *10 cx de Chope Pilsen 50L*"
            )

        if not quantidade:
            return (
                f"OK! *{produto_nome}*. Quantas unidades você deseja?\n"
                "Ex: *10 cx*"
            )

        return (
            f"📋 *Resumo do pedido:*\n"
            f"Cliente: vinculado à conversa\n"
            f"Produto: {produto_nome}\n"
            f"Quantidade: {quantidade}\n\n"
            f"Para confirmar, responda *confirmar*.\n"
            f"Para alterar, me diga o que mudar."
        )

    def _resposta_fallback(self, conversa: WhatsappConversaModel) -> str:
        return (
            "🤖 Não entendi sua solicitação.\n\n"
            "Você pode me perguntar:\n"
            "• *Consultar cliente* — dados de um cliente\n"
            "• *Consultar estoque* — saldo de produtos\n"
            "• *Cadastrar pedido* — novo pedido\n"
            "• *Status chopeiras* — situação dos equipamentos\n"
            "• *Consultar documentos* — documentos anexados\n\n"
            "Ou digite *menu* para ver as opções."
        )

    @staticmethod
    def _formatar_cliente(cliente: ClienteModel) -> str:
        tipo = "PF" if cliente.tipo_pessoa == "PF" else "PJ"
        doc = cliente.cpf_cnpj or "-"
        nome = cliente.nome_razao_social
        fantasia = f" ({cliente.nome_fantasia})" if cliente.nome_fantasia else ""
        raw_status = (
            cliente.status.value
            if hasattr(cliente.status, "value")
            else str(cliente.status)
        )
        status = {
            "ativo": "✅ Ativo",
            "inativo": "❌ Inativo",
            "bloqueado": "🔒 Bloqueado",
        }.get(raw_status, raw_status)

        return (
            f"*{nome}*{fantasia}\n"
            f"📇 {tipo}: {doc}\n"
            f"📞 {cliente.celular or cliente.telefone or '-'}\n"
            f"📧 {cliente.email or '-'}\n"
            f"💰 Limite: R$ {float(cliente.limite_credito or 0):.2f}\n"
            f"💳 Disponível: R$ {float(cliente.saldo_disponivel or 0):.2f}\n"
            f"📊 Status: {status}"
        )
