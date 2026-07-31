from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import get_current_user, requer_permissao
from api.serializers.financial_schema import (
    BoletoGerarInput,
    BoletoListResponse,
    BoletoResponse,
    ContaPagarCreate,
    ContaPagarListResponse,
    ContaPagarResponse,
    ContaPagarUpdate,
    ContaReceberCreate,
    ContaReceberListResponse,
    ContaReceberResponse,
    ContaReceberUpdate,
    DreCategoriaItem,
    DreResponse,
    FinancialDashboardResponse,
    FluxoCaixaProjecaoItem,
    FluxoCaixaProjecaoResponse,
    InadimplenciaClientesResponse,
    InadimplenciaItem,
    InadimplenciaPorCliente,
    InadimplenciaResponse,
    LancamentoCreate,
    LancamentoListResponse,
    LancamentoResponse,
    PagarBaixaInput,
    PixGerarInput,
    PixListResponse,
    PixResponse,
    ReceberBaixaInput,
    RelatorioContasPagarResponse,
    RelatorioContasReceberResponse,
    RelatorioFluxoCaixaItem,
    RelatorioFluxoCaixaResponse,
)
from core.domain.auth.papeis import Acao, Modulo
from database.models.boleto import BoletoModel
from database.models.conta_pagar import ContaPagarModel
from database.models.conta_receber import ContaReceberModel, ContaStatus, FormaPagamento
from database.models.financeiro_baixa import BaixaModel, BaixaTipo
from database.models.lancamento import LancamentoModel, LancamentoTipo
from database.models.pix_cobranca import PixCobrancaModel, PixStatus
from database.repositories.baixa_repository_impl import BaixaRepositoryImpl
from database.repositories.boleto_repository_impl import BoletoRepositoryImpl
from database.repositories.conta_pagar_repository_impl import ContaPagarRepositoryImpl
from database.repositories.conta_receber_repository_impl import ContaReceberRepositoryImpl
from database.repositories.lancamento_repository_impl import (
    ContaPagarSaldoRepositoryImpl,
    ContaReceberSaldoRepositoryImpl,
    LancamentoRepositoryImpl,
)
from database.repositories.pix_repository_impl import PixCobrancaRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/dashboard", response_model=FinancialDashboardResponse)
async def financial_dashboard(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> FinancialDashboardResponse:
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)

    receber_repo = ContaReceberRepositoryImpl(session)
    pagar_repo = ContaPagarRepositoryImpl(session)
    receber_saldo = ContaReceberSaldoRepositoryImpl(session)
    pagar_saldo = ContaPagarSaldoRepositoryImpl(session)
    lanc_repo = LancamentoRepositoryImpl(session)

    total_receber = await receber_repo.sum_open()
    total_pagar = await pagar_repo.sum_open()
    vencidas_receber = await receber_saldo.total_receber_vencido(hoje)
    vencidas_pagar = await pagar_saldo.total_pagar_vencido(hoje)

    recebido_mes, pago_mes = await lanc_repo.sum_by_periodo(inicio_mes, hoje)
    saldo_atual = await lanc_repo.saldo_ate_data(hoje)

    return FinancialDashboardResponse(
        total_a_receber=total_receber,
        total_a_pagar=total_pagar,
        saldo_previsto=total_receber - total_pagar,
        contas_receber_vencidas=vencidas_receber,
        contas_pagar_vencidas=vencidas_pagar,
        total_recebido_mes=recebido_mes,
        total_pago_mes=pago_mes,
        saldo_disponivel=saldo_atual,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CONTAS A RECEBER
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/receber", response_model=ContaReceberListResponse)
async def list_contas_receber(
    cliente_id: UUID | None = None,
    status: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> ContaReceberListResponse:
    repo = ContaReceberRepositoryImpl(session)

    if cliente_id:
        items = await repo.find_by_cliente(cliente_id)
    elif status:
        items = await repo.find_by_status(status)
    else:
        items = await repo.find_all(skip=skip, limit=limit)

    total = await repo.count() if not (cliente_id or status) else len(items)
    return ContaReceberListResponse(
        items=[_conta_receber_to_response(c) for c in items],
        total=total,
    )


@router.get("/receber/{conta_id}", response_model=ContaReceberResponse)
async def get_conta_receber(
    conta_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> ContaReceberResponse:
    repo = ContaReceberRepositoryImpl(session)
    conta = await repo.find_by_id(conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a receber não encontrada")
    return _conta_receber_to_response(conta)


@router.post("/receber", response_model=ContaReceberResponse, status_code=201)
async def create_conta_receber(
    body: ContaReceberCreate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.CRIAR)),
) -> ContaReceberResponse:
    repo = ContaReceberRepositoryImpl(session)

    conta = ContaReceberModel(
        cliente_id=body.cliente_id,
        pedido_id=body.pedido_id,
        parcela=body.parcela,
        numero_documento=body.numero_documento or "",
        data_emissao=body.data_emissao,
        data_vencimento=body.data_vencimento,
        valor_original=float(body.valor_original),
        status=ContaStatus.ABERTO,
    )
    await repo.save(conta)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return _conta_receber_to_response(conta)


@router.put("/receber/{conta_id}", response_model=ContaReceberResponse)
async def update_conta_receber(
    conta_id: UUID,
    body: ContaReceberUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.ATUALIZAR)),
) -> ContaReceberResponse:
    repo = ContaReceberRepositoryImpl(session)
    conta = await repo.find_by_id(conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a receber não encontrada")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "valor_original":
                value = float(value)
            setattr(conta, field, value)

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return _conta_receber_to_response(conta)


@router.delete("/receber/{conta_id}", status_code=204)
async def delete_conta_receber(
    conta_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.DELETAR)),
) -> None:
    repo = ContaReceberRepositoryImpl(session)
    conta = await repo.find_by_id(conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a receber não encontrada")

    conta.status = ContaStatus.CANCELADO
    uow = AsyncUnitOfWork(session)
    await uow.commit()


@router.post("/receber/{conta_id}/receber", response_model=ContaReceberResponse)
async def registrar_recebimento(
    conta_id: UUID,
    body: ReceberBaixaInput,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.ATUALIZAR)),
) -> ContaReceberResponse:
    repo = ContaReceberRepositoryImpl(session)
    baixa_repo = BaixaRepositoryImpl(session)
    lanc_repo = LancamentoRepositoryImpl(session)

    conta = await repo.find_by_id(conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a receber não encontrada")
    if conta.status == ContaStatus.PAGO:
        raise HTTPException(status_code=400, detail="Conta já está paga")
    if conta.status == ContaStatus.CANCELADO:
        raise HTTPException(status_code=400, detail="Conta cancelada não pode receber pagamento")

    valor_pago = float(body.valor_pago)
    desconto = float(body.desconto)
    juros = float(body.juros)
    multa = float(body.multa)

    if body.forma_pagamento:
        conta.forma_pagamento = FormaPagamento(body.forma_pagamento)
    conta.valor_pago = float(conta.valor_pago or 0) + valor_pago
    conta.desconto = float(conta.desconto or 0) + desconto
    conta.juros = float(conta.juros or 0) + juros
    conta.multa = float(conta.multa or 0) + multa
    conta.data_pagamento = body.data_pagamento

    saldo = (
        float(conta.valor_original) - conta.valor_pago - conta.desconto + conta.juros + conta.multa
    )
    conta.status = ContaStatus.PAGO if saldo <= 0 else ContaStatus.PARCIAL

    baixa = BaixaModel(
        tipo=BaixaTipo.RECEBIMENTO,
        data_baixa=body.data_pagamento,
        valor=valor_pago,
        forma_pagamento=conta.forma_pagamento,
        observacao=body.observacao,
        conta_receber_id=conta_id,
    )
    await baixa_repo.save(baixa)

    lanc = LancamentoModel(
        data=body.data_pagamento,
        tipo=LancamentoTipo.ENTRADA,
        valor=valor_pago,
        categoria="recebimento",
        descricao=f"Recebimento conta #{conta.numero_documento}",
        conciliado=True,
        data_conciliacao=body.data_pagamento,
        conta_receber_id=conta_id,
    )
    await lanc_repo.save(lanc)

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return _conta_receber_to_response(conta)


# ═══════════════════════════════════════════════════════════════════════════════
# CONTAS A PAGAR
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/pagar", response_model=ContaPagarListResponse)
async def list_contas_pagar(
    fornecedor_id: UUID | None = None,
    status: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> ContaPagarListResponse:
    repo = ContaPagarRepositoryImpl(session)

    if fornecedor_id:
        items = await repo.find_by_fornecedor(fornecedor_id)
    elif status:
        items = await repo.find_by_status(status)
    else:
        items = await repo.find_all(skip=skip, limit=limit)

    total = await repo.count() if not (fornecedor_id or status) else len(items)
    return ContaPagarListResponse(
        items=[_conta_pagar_to_response(c) for c in items],
        total=total,
    )


@router.get("/pagar/{conta_id}", response_model=ContaPagarResponse)
async def get_conta_pagar(
    conta_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> ContaPagarResponse:
    repo = ContaPagarRepositoryImpl(session)
    conta = await repo.find_by_id(conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a pagar não encontrada")
    return _conta_pagar_to_response(conta)


@router.post("/pagar", response_model=ContaPagarResponse, status_code=201)
async def create_conta_pagar(
    body: ContaPagarCreate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.CRIAR)),
) -> ContaPagarResponse:
    repo = ContaPagarRepositoryImpl(session)

    conta = ContaPagarModel(
        fornecedor_id=body.fornecedor_id,
        pedido_compra_id=body.pedido_compra_id,
        parcela=body.parcela,
        numero_documento=body.numero_documento or "",
        data_emissao=body.data_emissao,
        data_vencimento=body.data_vencimento,
        valor_original=float(body.valor_original),
        categoria=body.categoria,
        status=ContaStatus.ABERTO,
    )
    await repo.save(conta)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return _conta_pagar_to_response(conta)


@router.put("/pagar/{conta_id}", response_model=ContaPagarResponse)
async def update_conta_pagar(
    conta_id: UUID,
    body: ContaPagarUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.ATUALIZAR)),
) -> ContaPagarResponse:
    repo = ContaPagarRepositoryImpl(session)
    conta = await repo.find_by_id(conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a pagar não encontrada")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "valor_original":
                value = float(value)
            setattr(conta, field, value)

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return _conta_pagar_to_response(conta)


@router.delete("/pagar/{conta_id}", status_code=204)
async def delete_conta_pagar(
    conta_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.DELETAR)),
) -> None:
    repo = ContaPagarRepositoryImpl(session)
    conta = await repo.find_by_id(conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a pagar não encontrada")

    conta.status = ContaStatus.CANCELADO
    uow = AsyncUnitOfWork(session)
    await uow.commit()


@router.post("/pagar/{conta_id}/pagar", response_model=ContaPagarResponse)
async def registrar_pagamento(
    conta_id: UUID,
    body: PagarBaixaInput,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.ATUALIZAR)),
) -> ContaPagarResponse:
    repo = ContaPagarRepositoryImpl(session)
    baixa_repo = BaixaRepositoryImpl(session)
    lanc_repo = LancamentoRepositoryImpl(session)

    conta = await repo.find_by_id(conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a pagar não encontrada")
    if conta.status == ContaStatus.PAGO:
        raise HTTPException(status_code=400, detail="Conta já está paga")
    if conta.status == ContaStatus.CANCELADO:
        raise HTTPException(status_code=400, detail="Conta cancelada não pode ser paga")

    valor_pago = float(body.valor_pago)
    desconto = float(body.desconto)
    juros = float(body.juros)
    multa = float(body.multa)

    conta.valor_pago = float(conta.valor_pago or 0) + valor_pago
    conta.desconto = float(conta.desconto or 0) + desconto
    conta.juros = float(conta.juros or 0) + juros
    conta.multa = float(conta.multa or 0) + multa
    conta.data_pagamento = body.data_pagamento

    saldo = (
        float(conta.valor_original) - conta.valor_pago - conta.desconto + conta.juros + conta.multa
    )
    conta.status = ContaStatus.PAGO if saldo <= 0 else ContaStatus.PARCIAL

    baixa = BaixaModel(
        tipo=BaixaTipo.PAGAMENTO,
        data_baixa=body.data_pagamento,
        valor=valor_pago,
        observacao=body.observacao,
        conta_pagar_id=conta_id,
    )
    await baixa_repo.save(baixa)

    lanc = LancamentoModel(
        data=body.data_pagamento,
        tipo=LancamentoTipo.SAIDA,
        valor=valor_pago,
        categoria="pagamento",
        descricao=f"Pagamento conta #{conta.numero_documento}",
        conciliado=True,
        data_conciliacao=body.data_pagamento,
        conta_pagar_id=conta_id,
    )
    await lanc_repo.save(lanc)

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return _conta_pagar_to_response(conta)


# ═══════════════════════════════════════════════════════════════════════════════
# FLUXO DE CAIXA
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/fluxo-caixa", response_model=LancamentoListResponse)
async def list_lancamentos(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> LancamentoListResponse:
    repo = LancamentoRepositoryImpl(session)
    hoje = date.today()
    inicio = data_inicio or hoje.replace(day=1)
    fim = data_fim or hoje

    items = await repo.find_by_periodo(inicio, fim, skip=skip, limit=limit)
    entradas, saidas = await repo.sum_by_periodo(inicio, fim)
    saldo_periodo = entradas - saidas

    return LancamentoListResponse(
        items=[LancamentoResponse.model_validate(la) for la in items],
        total=len(items),
        saldo_periodo=saldo_periodo,
    )


@router.post("/fluxo-caixa", response_model=LancamentoResponse, status_code=201)
async def create_lancamento(
    body: LancamentoCreate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.CRIAR)),
) -> LancamentoResponse:
    repo = LancamentoRepositoryImpl(session)

    lanc = LancamentoModel(
        data=body.data,
        tipo=LancamentoTipo(body.tipo),
        valor=float(body.valor),
        categoria=body.categoria,
        descricao=body.descricao,
        conciliado=body.conciliado,
        data_conciliacao=body.data if body.conciliado else None,
    )
    await repo.save(lanc)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return LancamentoResponse.model_validate(lanc)


@router.get("/fluxo-caixa/projecao", response_model=FluxoCaixaProjecaoResponse)
async def fluxo_caixa_projecao(
    dias: int = Query(90, ge=30, le=360),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> FluxoCaixaProjecaoResponse:
    hoje = date.today()
    lanc_repo = LancamentoRepositoryImpl(session)
    receber_saldo = ContaReceberSaldoRepositoryImpl(session)
    pagar_saldo = ContaPagarSaldoRepositoryImpl(session)

    saldo_atual = await lanc_repo.saldo_ate_data(hoje)

    intervalos = [
        (hoje + timedelta(days=30 * i), hoje + timedelta(days=30 * (i + 1) - 1))
        for i in range(max(1, dias // 30))
    ]

    items = []
    for data_inicio, data_fim in intervalos:
        entradas = await receber_saldo.entradas_previstas_periodo(data_inicio, data_fim)
        saidas = await pagar_saldo.saidas_previstas_periodo(data_inicio, data_fim)
        items.append(FluxoCaixaProjecaoItem(
            periodo=f"{data_inicio:%m/%Y}",
            data_inicio=data_inicio,
            data_fim=data_fim,
            entradas_previstas=entradas,
            saidas_previstas=saidas,
            saldo_previsto=entradas - saidas,
        ))

    return FluxoCaixaProjecaoResponse(items=items, saldo_atual=saldo_atual)


@router.post("/fluxo-caixa/conciliar/{lancamento_id}", response_model=LancamentoResponse)
async def conciliar_lancamento(
    lancamento_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.ATUALIZAR)),
) -> LancamentoResponse:
    repo = LancamentoRepositoryImpl(session)
    lanc = await repo.conciliar(lancamento_id, date.today())
    if not lanc:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return LancamentoResponse.model_validate(lanc)


# ═══════════════════════════════════════════════════════════════════════════════
# BOLETOS
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/boletos", response_model=BoletoListResponse)
async def list_boletos(
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> BoletoListResponse:
    repo = BoletoRepositoryImpl(session)
    if status:
        items = [b for b in await repo.find_all(skip=skip, limit=limit) if b.status.value == status]
    else:
        items = await repo.find_all(skip=skip, limit=limit)
    total = await repo.count() if not status else len(items)
    return BoletoListResponse(
        items=[BoletoResponse.model_validate(b) for b in items],
        total=total,
    )


@router.get("/boletos/{boleto_id}", response_model=BoletoResponse)
async def get_boleto(
    boleto_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> BoletoResponse:
    repo = BoletoRepositoryImpl(session)
    boleto = await repo.find_by_id(boleto_id)
    if not boleto:
        raise HTTPException(status_code=404, detail="Boleto não encontrado")
    return BoletoResponse.model_validate(boleto)


@router.post("/receber/{conta_id}/boleto", response_model=BoletoResponse, status_code=201)
async def gerar_boleto(
    conta_id: UUID,
    body: BoletoGerarInput,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.CRIAR)),
) -> BoletoResponse:
    conta_repo = ContaReceberRepositoryImpl(session)
    boleto_repo = BoletoRepositoryImpl(session)

    conta = await conta_repo.find_by_id(conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a receber não encontrada")

    from uuid import uuid4

    nosso_numero = f"{conta_id.hex[:10]}{uuid4().hex[:10]}".upper()

    from database.models.boleto import BoletoStatus

    boleto = BoletoModel(
        nosso_numero=nosso_numero,
        data_emissao=date.today(),
        data_vencimento=body.data_vencimento,
        valor_nominal=float(body.valor) if body.valor else conta.valor_original,
        status=BoletoStatus.GERADO,
        conta_receber_id=conta_id,
    )
    await boleto_repo.save(boleto)

    conta.nosso_numero = nosso_numero

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return BoletoResponse.model_validate(boleto)


@router.post("/boletos/{boleto_id}/cancelar", response_model=BoletoResponse)
async def cancelar_boleto(
    boleto_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.ATUALIZAR)),
) -> BoletoResponse:
    repo = BoletoRepositoryImpl(session)
    boleto = await repo.find_by_id(boleto_id)
    if not boleto:
        raise HTTPException(status_code=404, detail="Boleto não encontrado")

    from database.models.boleto import BoletoStatus
    boleto.status = BoletoStatus.CANCELADO

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return BoletoResponse.model_validate(boleto)


# ═══════════════════════════════════════════════════════════════════════════════
# PIX
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/pix", response_model=PixListResponse)
async def list_pix(
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> PixListResponse:
    repo = PixCobrancaRepositoryImpl(session)
    if status:
        items = [p for p in await repo.find_all(skip=skip, limit=limit) if p.status.value == status]
    else:
        items = await repo.find_all(skip=skip, limit=limit)
    total = await repo.count() if not status else len(items)
    return PixListResponse(
        items=[PixResponse.model_validate(p) for p in items],
        total=total,
    )


@router.get("/pix/{pix_id}", response_model=PixResponse)
async def get_pix(
    pix_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> PixResponse:
    repo = PixCobrancaRepositoryImpl(session)
    pix = await repo.find_by_id(pix_id)
    if not pix:
        raise HTTPException(status_code=404, detail="Cobrança PIX não encontrada")
    return PixResponse.model_validate(pix)


@router.post("/receber/{conta_id}/pix", response_model=PixResponse, status_code=201)
async def gerar_pix(
    conta_id: UUID,
    body: PixGerarInput,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.CRIAR)),
) -> PixResponse:
    conta_repo = ContaReceberRepositoryImpl(session)
    pix_repo = PixCobrancaRepositoryImpl(session)

    conta = await conta_repo.find_by_id(conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a receber não encontrada")

    from uuid import uuid4

    txid = f"TX{conta_id.hex[:12]}{uuid4().hex[:12]}".upper()

    from database.models.pix_cobranca import PixStatus

    pix = PixCobrancaModel(
        txid=txid,
        valor=float(body.valor) if body.valor else conta.valor_original,
        status=PixStatus.ATIVO,
        conta_receber_id=conta_id,
    )
    await pix_repo.save(pix)

    conta.pix_charge_id = txid

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return PixResponse.model_validate(pix)


@router.post("/pix/{pix_id}/confirmar", response_model=PixResponse)
async def confirmar_pix(
    pix_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.ATUALIZAR)),
) -> PixResponse:
    pix_repo = PixCobrancaRepositoryImpl(session)
    conta_repo = ContaReceberRepositoryImpl(session)

    pix = await pix_repo.find_by_id(pix_id)
    if not pix:
        raise HTTPException(status_code=404, detail="Cobrança PIX não encontrada")

    pix.status = PixStatus.CONCLUIDO
    pix.data_pagamento = datetime.now(timezone.utc)

    conta = await conta_repo.find_by_id(pix.conta_receber_id)
    if conta and conta.status != ContaStatus.PAGO:
        conta.valor_pago += pix.valor
        conta.data_pagamento = date.today()
        saldo = conta.valor_original - conta.valor_pago - conta.desconto + conta.juros + conta.multa
        conta.status = ContaStatus.PAGO if saldo <= 0 else ContaStatus.PARCIAL

        lanc_repo = LancamentoRepositoryImpl(session)
        await lanc_repo.save(LancamentoModel(
            data=date.today(),
            tipo=LancamentoTipo.ENTRADA,
            valor=pix.valor,
            categoria="recebimento_pix",
            descricao=f"PIX #{pix.txid}",
            conciliado=True,
            data_conciliacao=date.today(),
            conta_receber_id=pix.conta_receber_id,
        ))

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return PixResponse.model_validate(pix)


# ═══════════════════════════════════════════════════════════════════════════════
# INADIMPLÊNCIA
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/inadimplencia", response_model=InadimplenciaResponse)
async def list_inadimplencia(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> InadimplenciaResponse:
    hoje = date.today()
    repo = ContaReceberSaldoRepositoryImpl(session)
    contas = await repo.find_vencidos_com_cliente(hoje)

    items = []
    for c in contas:
        saldo = c.valor_original - c.valor_pago - c.desconto + c.juros + c.multa
        dias = (hoje - c.data_vencimento).days
        if dias <= 30:
            faixa = "1-30"
        elif dias <= 60:
            faixa = "31-60"
        elif dias <= 90:
            faixa = "61-90"
        else:
            faixa = "90+"

        items.append(InadimplenciaItem(
            conta_id=c.id,
            cliente_id=c.cliente_id,
            cliente_nome=c.cliente.nome_razao_social if c.cliente else "N/A",
            documento=c.numero_documento,
            data_vencimento=c.data_vencimento,
            dias_atraso=dias,
            faixa=faixa,
            valor_original=Decimal(str(c.valor_original)),
            saldo=Decimal(str(saldo)),
        ))

    total = float(sum(i.saldo for i in items))
    return InadimplenciaResponse(
        items=items,
        total_geral=total,
        quantidade_total=len(items),
    )


@router.get("/inadimplencia/clientes", response_model=InadimplenciaClientesResponse)
async def inadimplencia_por_cliente(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FINANCEIRO, Acao.LER)),
) -> InadimplenciaClientesResponse:
    hoje = date.today()
    repo = ContaReceberSaldoRepositoryImpl(session)
    contas = await repo.find_vencidos_com_cliente(hoje)

    agrupado: dict[UUID, dict[str, Any]] = {}
    for c in contas:
        saldo = c.valor_original - c.valor_pago - c.desconto + c.juros + c.multa
        cid = c.cliente_id
        if cid not in agrupado:
            agrupado[cid] = {
                "cliente_id": cid,
                "cliente_nome": c.cliente.nome_razao_social if c.cliente else "N/A",
                "total_vencido": 0.0,
                "quantidade": 0,
                "dias_maior_atraso": 0,
            }
        agrupado[cid]["total_vencido"] += saldo
        agrupado[cid]["quantidade"] += 1
        dias = (hoje - c.data_vencimento).days
        if dias > agrupado[cid]["dias_maior_atraso"]:
            agrupado[cid]["dias_maior_atraso"] = dias

    items = [InadimplenciaPorCliente(**v) for v in agrupado.values()]
    items.sort(key=lambda x: x.total_vencido, reverse=True)
    return InadimplenciaClientesResponse(items=items)


# ═══════════════════════════════════════════════════════════════════════════════
# RELATÓRIOS
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/relatorios/fluxo-caixa", response_model=RelatorioFluxoCaixaResponse)
async def relatorio_fluxo_caixa(
    data_inicio: date,
    data_fim: date,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.RELATORIOS, Acao.LER)),
) -> RelatorioFluxoCaixaResponse:
    lanc_repo = LancamentoRepositoryImpl(session)
    lancamentos = await lanc_repo.find_by_periodo(data_inicio, data_fim, limit=9999)

    from collections import defaultdict

    por_dia: dict[date, dict[str, float]] = defaultdict(lambda: {"entradas": 0.0, "saidas": 0.0})
    for lanc in lancamentos:
        if lanc.tipo == LancamentoTipo.ENTRADA:
            por_dia[lanc.data]["entradas"] += lanc.valor
        else:
            por_dia[lanc.data]["saidas"] += lanc.valor

    saldo_acumulado = await lanc_repo.saldo_ate_data(data_inicio - timedelta(days=1))
    items = []
    dia = data_inicio
    while dia <= data_fim:
        dados = por_dia.get(dia, {"entradas": 0.0, "saidas": 0.0})
        saldo_dia = dados["entradas"] - dados["saidas"]
        saldo_acumulado += saldo_dia
        items.append(RelatorioFluxoCaixaItem(
            data=dia,
            entradas=dados["entradas"],
            saidas=dados["saidas"],
            saldo_dia=saldo_dia,
            saldo_acumulado=saldo_acumulado,
        ))
        dia += timedelta(days=1)

    total_entradas = sum(i.entradas for i in items)
    total_saidas = sum(i.saidas for i in items)
    return RelatorioFluxoCaixaResponse(
        items=items,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        saldo_final=saldo_acumulado,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get("/relatorios/contas-receber", response_model=RelatorioContasReceberResponse)
async def relatorio_contas_receber(
    data_inicio: date,
    data_fim: date,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.RELATORIOS, Acao.LER)),
) -> RelatorioContasReceberResponse:
    repo = ContaReceberRepositoryImpl(session)
    receber_saldo = ContaReceberSaldoRepositoryImpl(session)

    items = await repo.find_by_periodo(data_inicio, data_fim)
    total_previsto = await receber_saldo.entradas_previstas_periodo(data_inicio, data_fim)
    total_recebido = await receber_saldo.total_recebido_periodo(data_inicio, data_fim)
    total_vencido = await receber_saldo.total_receber_vencido(data_fim)

    return RelatorioContasReceberResponse(
        items=[_conta_receber_to_response(c) for c in items],
        total_previsto=total_previsto,
        total_recebido=total_recebido,
        total_vencido=total_vencido,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get("/relatorios/contas-pagar", response_model=RelatorioContasPagarResponse)
async def relatorio_contas_pagar(
    data_inicio: date,
    data_fim: date,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.RELATORIOS, Acao.LER)),
) -> RelatorioContasPagarResponse:
    repo = ContaPagarRepositoryImpl(session)
    pagar_saldo = ContaPagarSaldoRepositoryImpl(session)

    items = await repo.find_by_periodo(data_inicio, data_fim)
    total_previsto = await pagar_saldo.saidas_previstas_periodo(data_inicio, data_fim)
    total_pago = await pagar_saldo.total_pago_periodo(data_inicio, data_fim)
    total_vencido = await pagar_saldo.total_pagar_vencido(data_fim)

    return RelatorioContasPagarResponse(
        items=[_conta_pagar_to_response(c) for c in items],
        total_previsto=total_previsto,
        total_pago=total_pago,
        total_vencido=total_vencido,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get("/relatorios/inadimplencia", response_model=InadimplenciaResponse)
async def relatorio_inadimplencia(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.RELATORIOS, Acao.LER)),
) -> InadimplenciaResponse:
    return await list_inadimplencia(session=session, _=_)


@router.get("/relatorios/dre", response_model=DreResponse)
async def relatorio_dre(
    data_inicio: date,
    data_fim: date,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.RELATORIOS, Acao.LER)),
) -> DreResponse:
    lanc_repo = LancamentoRepositoryImpl(session)
    categorias = await lanc_repo.sum_by_categoria_periodo(data_inicio, data_fim)

    from collections import defaultdict

    agg: dict[str, dict[str, float]] = defaultdict(lambda: {"receitas": 0.0, "despesas": 0.0})
    for row in categorias:
        cat = row["categoria"]
        if row["tipo"] == "entrada":
            agg[cat]["receitas"] += row["total"]
        else:
            agg[cat]["despesas"] += row["total"]

    items = [
        DreCategoriaItem(
            categoria=cat,
            receitas=v["receitas"],
            despesas=v["despesas"],
            saldo=v["receitas"] - v["despesas"],
        )
        for cat, v in sorted(agg.items())
    ]

    total_receitas = sum(i.receitas for i in items)
    total_despesas = sum(i.despesas for i in items)

    return DreResponse(
        items=items,
        total_receitas=total_receitas,
        total_despesas=total_despesas,
        resultado=total_receitas - total_despesas,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _saldo(
    valor_original: float, valor_pago: float,
    desconto: float, juros: float, multa: float,
) -> float:
    return (
        float(valor_original) - float(valor_pago) - float(desconto) + float(juros) + float(multa)
    )


def _conta_receber_to_response(c: ContaReceberModel) -> ContaReceberResponse:
    from decimal import Decimal
    vp = c.valor_pago or 0
    desc = c.desconto or 0
    jur = c.juros or 0
    mult = c.multa or 0
    return ContaReceberResponse(
        id=c.id,
        parcela=c.parcela or 1,
        numero_documento=c.numero_documento or "",
        data_emissao=c.data_emissao,
        data_vencimento=c.data_vencimento,
        data_pagamento=c.data_pagamento,
        valor_original=Decimal(str(c.valor_original)),
        valor_pago=Decimal(str(vp)),
        desconto=Decimal(str(desc)),
        juros=Decimal(str(jur)),
        multa=Decimal(str(mult)),
        saldo=Decimal(str(_saldo(c.valor_original, vp, desc, jur, mult))),
        status=c.status.value if hasattr(c.status, 'value') else str(c.status),
        forma_pagamento=(
            c.forma_pagamento.value
            if c.forma_pagamento and hasattr(c.forma_pagamento, 'value')
            else str(c.forma_pagamento) if c.forma_pagamento else None
        ),
        nosso_numero=c.nosso_numero,
        pix_charge_id=c.pix_charge_id,
        cliente_id=c.cliente_id,
        pedido_id=c.pedido_id,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def _conta_pagar_to_response(c: ContaPagarModel) -> ContaPagarResponse:
    from decimal import Decimal
    vp = c.valor_pago or 0
    desc = c.desconto or 0
    jur = c.juros or 0
    mult = c.multa or 0
    return ContaPagarResponse(
        id=c.id,
        parcela=c.parcela or 1,
        numero_documento=c.numero_documento or "",
        data_emissao=c.data_emissao,
        data_vencimento=c.data_vencimento,
        data_pagamento=c.data_pagamento,
        valor_original=Decimal(str(c.valor_original)),
        valor_pago=Decimal(str(vp)),
        desconto=Decimal(str(desc)),
        juros=Decimal(str(jur)),
        multa=Decimal(str(mult)),
        saldo=Decimal(str(_saldo(c.valor_original, vp, desc, jur, mult))),
        status=c.status.value if hasattr(c.status, 'value') else str(c.status),
        categoria=c.categoria,
        fornecedor_id=c.fornecedor_id,
        pedido_compra_id=c.pedido_compra_id,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )
