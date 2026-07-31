import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.serializers.whatsapp_schema import (
    ChopeiraResponse,
    ClienteResponse,
    ConversaDetalhadaResponse,
    ConversaResponse,
    DocumentoResponse,
    MensagemEntrada,
    MensagemEnviar,
    MensagemResponse,
    MensagemSaida,
    PedidoCriadoResponse,
    ProdutoEstoqueResponse,
    WebhookReceber,
)
from core.application.usecases.whatsapp.cadastrar_pedido import (
    CadastrarPedidoWhatsAppUseCase,
)
from core.application.usecases.whatsapp.consultar_cliente import (
    ConsultarClienteWhatsAppUseCase,
)
from core.application.usecases.whatsapp.processar_mensagem import (
    ProcessarMensagemWhatsAppUseCase,
)
from core.shared.result import Failure
from database.repositories.cliente_repository_impl import ClienteRepositoryImpl
from database.repositories.whatsapp_repository_impl import (
    WhatsappConversaRepositoryImpl,
)
from database.unit_of_work import AsyncUnitOfWork
from infrastructure.messaging.integrations.whatsapp_client import FakeWhatsAppClient

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Webhook ────────────────────────────────────────────────────────────────────

@router.post("/webhook", response_model=MensagemResponse)
async def webhook_receber(
    body: WebhookReceber,
    session: AsyncSession = Depends(get_session),
) -> MensagemResponse:
    """Recebe mensagens do WhatsApp via webhook."""
    whatsapp = FakeWhatsAppClient()
    use_case = ProcessarMensagemWhatsAppUseCase(session, whatsapp_client=whatsapp)
    result = await use_case.executar(
        telefone=body.telefone,
        mensagem=body.mensagem,
        nome_contato=body.nome_contato,
    )
    if isinstance(result, Failure):
        raise HTTPException(status_code=400, detail=result.error)
    data = result.value
    return MensagemResponse(
        mensagem_id=data["mensagem_id"],
        conversa_id=data["conversa_id"],
        resposta=data["resposta"],
    )


# ── Conversas ──────────────────────────────────────────────────────────────────

@router.get("/conversas", response_model=list[ConversaResponse])
async def listar_conversas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[ConversaResponse]:
    repo = WhatsappConversaRepositoryImpl(session)
    conversas = await repo.find_ativas(skip=skip, limit=limit)
    return [ConversaResponse.model_validate(c) for c in conversas]


@router.get("/conversas/{conversa_id}", response_model=ConversaDetalhadaResponse)
async def detalhar_conversa(
    conversa_id: str,
    session: AsyncSession = Depends(get_session),
) -> ConversaDetalhadaResponse:
    from uuid import UUID

    repo = WhatsappConversaRepositoryImpl(session)
    try:
        cid = UUID(conversa_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de conversa inválido")

    conversa = await repo.find_by_id(cid)
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    mensagens = await repo.listar_mensagens(cid, limit=50)

    resp = ConversaDetalhadaResponse.model_validate(conversa)
    resp.mensagens = []
    for m in mensagens:
        if m.direcao == "entrada":
            resp.mensagens.append(
                MensagemEntrada(
                    id=m.id,
                    telefone=m.remetente,
                    conteudo=m.conteudo,
                    tipo=m.tipo,
                    data_recebida=m.data_recebida,
                    lida=m.lida,
                )
            )
        else:
            resp.mensagens.append(
                MensagemSaida(
                    id=m.id,
                    telefone=m.remetente,
                    conteudo=m.conteudo,
                    data_envio=m.created_at,
                    status="enviada",
                )
            )
    return resp


# ── Envio ativo ────────────────────────────────────────────────────────────────

@router.post("/enviar")
async def enviar_mensagem(
    body: MensagemEnviar,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Envia mensagem ativa para um WhatsApp."""
    repo = WhatsappConversaRepositoryImpl(session)
    whatsapp = FakeWhatsAppClient()

    from database.models.whatsapp_conversa import WhatsappConversaModel, WhatsappConversaStatus
    conversa = await repo.find_by_telefone(body.telefone)
    if not conversa:
        conversa = WhatsappConversaModel(
            telefone=body.telefone,
            status=WhatsappConversaStatus.ATIVA,
        )
        await repo.save(conversa)
        await session.flush()

    # Salvar mensagem de saída
    from database.models.whatsapp_conversa import WhatsappMensagemModel

    msg = WhatsappMensagemModel(
        remetente=conversa.telefone,
        conteudo=body.mensagem,
        tipo="texto",
        direcao="saida",
        conversa_id=conversa.id,
    )
    await repo.salvar_mensagem(msg)

    # Enviar via WhatsApp
    await whatsapp.send_text(to=body.telefone, text=body.mensagem)
    await repo.atualizar_ultima_mensagem(conversa.id, body.mensagem)

    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return {"status": "enviada", "conversa_id": str(conversa.id)}


# ── Consultas auxiliares ──────────────────────────────────────────────────────

@router.post("/consultar-cliente", response_model=ClienteResponse)
async def consultar_cliente(
    telefone: str = Query(..., description="Telefone do WhatsApp"),
    session: AsyncSession = Depends(get_session),
) -> ClienteResponse:
    use_case = ConsultarClienteWhatsAppUseCase(session)
    result = await use_case.por_telefone(telefone)
    if isinstance(result, Failure):
        raise HTTPException(status_code=404, detail="Cliente não encontrado para este telefone")

    cliente = result.value
    return ClienteResponse(
        id=cliente.id,
        nome_razao_social=cliente.nome_razao_social,
        cpf_cnpj=cliente.cpf_cnpj,
        telefone=cliente.telefone,
        celular=cliente.celular,
        email=cliente.email,
        status=cliente.status.value if hasattr(cliente.status, "value") else str(cliente.status),
    )


@router.get("/consultar-cliente/busca", response_model=list[ClienteResponse])
async def buscar_clientes(
    termo: str = Query(..., min_length=2),
    session: AsyncSession = Depends(get_session),
) -> list[ClienteResponse]:
    repo = ClienteRepositoryImpl(session)
    resultados = await repo.search(termo, limit=10)
    return [
        ClienteResponse(
            id=c.id,
            nome_razao_social=c.nome_razao_social,
            cpf_cnpj=c.cpf_cnpj,
            telefone=c.telefone,
            celular=c.celular,
            email=c.email,
            status=c.status.value if hasattr(c.status, "value") else str(c.status),
        )
        for c in resultados
    ]


@router.get("/consultar-estoque", response_model=list[ProdutoEstoqueResponse])
async def consultar_estoque(
    produto: str = Query(..., min_length=2),
    session: AsyncSession = Depends(get_session),
) -> list[ProdutoEstoqueResponse]:
    from sqlalchemy import select

    from database.models.deposito import DepositoModel
    from database.models.estoque import EstoqueModel
    from database.models.produto import ProdutoModel

    stmt = (
        select(ProdutoModel, EstoqueModel, DepositoModel)
        .join(EstoqueModel, EstoqueModel.produto_id == ProdutoModel.id)
        .join(DepositoModel, DepositoModel.id == EstoqueModel.deposito_id)
        .where(
            ProdutoModel.nome.ilike(f"%{produto}%")
            | ProdutoModel.codigo.ilike(f"%{produto}%")
        )
        .limit(20)
    )
    result = await session.execute(stmt)
    rows = result.all()

    return [
        ProdutoEstoqueResponse(
            codigo=p.codigo,
            nome=p.nome,
            quantidade_atual=float(e.quantidade_atual),
            deposito=d.nome,
            estoque_minimo=float(e.estoque_minimo) if e.estoque_minimo else None,
        )
        for p, e, d in rows
    ]


@router.get("/consultar-chopeiras", response_model=list[ChopeiraResponse])
async def consultar_chopeiras(
    termo: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> list[ChopeiraResponse]:
    from sqlalchemy import select

    from database.models.chopeira import ChopeiraModel

    if termo:
        from database.models.cliente import ClienteModel

        stmt = (
            select(ChopeiraModel)
            .join(ClienteModel, ClienteModel.id == ChopeiraModel.cliente_id)
            .where(
                ClienteModel.nome_razao_social.ilike(f"%{termo}%")
                | ChopeiraModel.codigo_identificacao.ilike(f"%{termo}%")
                | ChopeiraModel.local_instalacao.ilike(f"%{termo}%")
            )
            .limit(20)
        )
    else:
        stmt = select(ChopeiraModel).limit(20)

    result = await session.execute(stmt)
    chopeiras = list(result.scalars().all())

    return [
        ChopeiraResponse(
            codigo_identificacao=c.codigo_identificacao,
            marca=c.marca,
            modelo=c.modelo,
            tipo=c.tipo.value if hasattr(c.tipo, "value") else str(c.tipo),
            status=c.status.value if hasattr(c.status, "value") else str(c.status),
            local_instalacao=c.local_instalacao,
        )
        for c in chopeiras
    ]


@router.get("/consultar-documentos", response_model=list[DocumentoResponse])
async def consultar_documentos(
    entidade_tipo: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> list[DocumentoResponse]:
    from sqlalchemy import select

    from database.models.documento import DocumentoModel

    if entidade_tipo:
        stmt = (
            select(DocumentoModel)
            .where(DocumentoModel.entidade_tipo == entidade_tipo)
            .limit(20)
        )
    else:
        stmt = select(DocumentoModel).limit(20)

    result = await session.execute(stmt)
    docs = list(result.scalars().all())

    return [
        DocumentoResponse(
            id=d.id,
            tipo_documento=d.tipo_documento,
            nome_original=d.nome_original,
            entidade_tipo=d.entidade_tipo,
        )
        for d in docs
    ]


@router.post("/cadastrar-pedido", response_model=PedidoCriadoResponse)
async def cadastrar_pedido(
    cliente_id: str = Query(...),
    produto: str = Query(..., min_length=2),
    quantidade: float = Query(..., gt=0),
    session: AsyncSession = Depends(get_session),
) -> PedidoCriadoResponse:
    from uuid import UUID

    use_case = CadastrarPedidoWhatsAppUseCase(session)
    result = await use_case.executar(
        cliente_id=UUID(cliente_id),
        produto_nome=produto,
        quantidade=quantidade,
    )
    if isinstance(result, Failure):
        raise HTTPException(status_code=400, detail=result.error)

    data = result.value
    return PedidoCriadoResponse(
        id=data["id"],
        numero=data["numero"],
        total=data["total"],
        status=data["status"],
    )
