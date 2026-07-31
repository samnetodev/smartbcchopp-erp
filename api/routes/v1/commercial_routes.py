from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import requer_permissao
from api.serializers.commercial_schema import (
    ClienteInativoResponse,
    ClienteRankingItem,
    DashboardComercialResponse,
    FaturamentoItem,
    IndicadoresResponse,
    MetaCreate,
    MetaListResponse,
    MetaResponse,
    MetaUpdate,
)
from core.domain.auth.papeis import Acao, Modulo
from database.models.comercial import MetaModel
from database.repositories.comercial_repository_impl import (
    ComercialRepositoryImpl,
    MetaRepositoryImpl,
)
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


def _meta_to_response(m: MetaModel) -> MetaResponse:
    return MetaResponse(
        id=m.id,
        descricao=m.descricao,
        periodo_inicio=m.periodo_inicio,
        periodo_fim=m.periodo_fim,
        valor_meta=Decimal(str(m.valor_meta)),
        valor_realizado=Decimal(str(m.valor_realizado or 0)),
        comissao_percentual=Decimal(str(m.comissao_percentual or 0)),
        status=m.status.value if hasattr(m.status, "value") else str(m.status),
        vendedor_id=m.vendedor_id,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/dashboard", response_model=DashboardComercialResponse)
async def commercial_dashboard(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.LER)),
) -> DashboardComercialResponse:
    repo = ComercialRepositoryImpl(session)
    data = await repo.dashboard(data_inicio, data_fim)
    return DashboardComercialResponse(
        indicadores=IndicadoresResponse(**data["indicadores"]),
        faturamento_periodo=[FaturamentoItem(**f) for f in data["faturamento_periodo"]],
        ranking_clientes=[ClienteRankingItem(**r) for r in data["ranking_clientes"]],
        ticket_medio=data["ticket_medio"],
        total_clientes_ativos=data["total_clientes_ativos"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Clientes Inativos
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/clientes-inativos", response_model=list[ClienteInativoResponse])
async def list_clientes_inativos(
    meses_sem_compra: int = Query(3, ge=1, le=24),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.LER)),
) -> list[ClienteInativoResponse]:
    repo = ComercialRepositoryImpl(session)
    clientes = await repo.find_clientes_inativos(meses_sem_compra=meses_sem_compra)
    return [ClienteInativoResponse.model_validate(c) for c in clientes]


# ═══════════════════════════════════════════════════════════════════════════════
# Ranking
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/ranking", response_model=list[ClienteRankingItem])
async def ranking_clientes(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.LER)),
) -> list[ClienteRankingItem]:
    repo = ComercialRepositoryImpl(session)
    rows = await repo.find_ranking_clientes(data_inicio, data_fim, limit=limit)
    return [ClienteRankingItem(**r) for r in rows]


# ═══════════════════════════════════════════════════════════════════════════════
# Ticket Médio
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/ticket-medio")
async def ticket_medio(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.LER)),
) -> dict[str, Any]:
    repo = ComercialRepositoryImpl(session)
    valor = await repo.calcular_ticket_medio(data_inicio, data_fim)
    return {
        "ticket_medio": float(valor),
        "data_inicio": data_inicio.isoformat(),
        "data_fim": data_fim.isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Faturamento
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/faturamento", response_model=list[FaturamentoItem])
async def faturamento(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    agrupamento: str = Query("mes", pattern="^(dia|mes|ano)$"),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.LER)),
) -> list[FaturamentoItem]:
    repo = ComercialRepositoryImpl(session)
    rows = await repo.calcular_faturamento(data_inicio, data_fim, agrupamento=agrupamento)
    return [FaturamentoItem(**r) for r in rows]


# ═══════════════════════════════════════════════════════════════════════════════
# Indicadores
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/indicadores", response_model=IndicadoresResponse)
async def indicadores(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.LER)),
) -> IndicadoresResponse:
    repo = ComercialRepositoryImpl(session)
    data = await repo.calcular_indicadores(data_inicio, data_fim)
    return IndicadoresResponse(**data)


# ═══════════════════════════════════════════════════════════════════════════════
# Relatórios
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/relatorios/vendas")
async def relatorio_vendas(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.RELATORIOS, Acao.LER)),
) -> dict[str, Any]:
    repo = ComercialRepositoryImpl(session)
    indicadores = await repo.calcular_indicadores(data_inicio, data_fim)
    faturamento = await repo.calcular_faturamento(data_inicio, data_fim)
    ranking = await repo.find_ranking_clientes(data_inicio, data_fim, limit=10)
    return {
        "periodo": {"inicio": data_inicio.isoformat(), "fim": data_fim.isoformat()},
        "indicadores": indicadores,
        "faturamento": faturamento,
        "ranking_clientes": ranking,
    }


@router.get("/relatorios/clientes")
async def relatorio_clientes(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.RELATORIOS, Acao.LER)),
) -> dict[str, Any]:
    repo = ComercialRepositoryImpl(session)
    clientes = await repo.find_clientes_inativos(meses_sem_compra=3)
    total_ativos = len(clientes)
    return {
        "total_clientes_inativos": total_ativos,
        "clientes_inativos": [ClienteInativoResponse.model_validate(c) for c in clientes],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Metas (CRUD)
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/metas", response_model=MetaListResponse)
async def list_metas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    vendedor_id: UUID | None = None,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.LER)),
) -> MetaListResponse:
    repo = MetaRepositoryImpl(session)
    if vendedor_id:
        items = await repo.find_by_vendedor(vendedor_id, skip=skip, limit=limit)
    else:
        items = await repo.find_all(skip=skip, limit=limit)
    total = await repo.count()
    return MetaListResponse(
        items=[_meta_to_response(m) for m in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/metas/{meta_id}", response_model=MetaResponse)
async def get_meta(
    meta_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.LER)),
) -> MetaResponse:
    repo = MetaRepositoryImpl(session)
    meta = await repo.find_by_id(meta_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    return _meta_to_response(meta)


@router.post("/metas", response_model=MetaResponse, status_code=201)
async def create_meta(
    body: MetaCreate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.CRIAR)),
) -> MetaResponse:
    repo = MetaRepositoryImpl(session)
    meta = MetaModel(
        descricao=body.descricao,
        periodo_inicio=body.periodo_inicio,
        periodo_fim=body.periodo_fim,
        valor_meta=float(body.valor_meta),
        comissao_percentual=float(body.comissao_percentual),
        vendedor_id=body.vendedor_id,
    )
    await repo.save(meta)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return _meta_to_response(meta)


@router.put("/metas/{meta_id}", response_model=MetaResponse)
async def update_meta(
    meta_id: UUID,
    body: MetaUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.ATUALIZAR)),
) -> MetaResponse:
    repo = MetaRepositoryImpl(session)
    meta = await repo.find_by_id(meta_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field in ("valor_meta", "valor_realizado", "comissao_percentual"):
                value = float(value)
            setattr(meta, field, value)

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return _meta_to_response(meta)


@router.delete("/metas/{meta_id}", status_code=204)
async def delete_meta(
    meta_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.COMERCIAL, Acao.DELETAR)),
) -> None:
    repo = MetaRepositoryImpl(session)
    deleted = await repo.delete(meta_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    uow = AsyncUnitOfWork(session)
    await uow.commit()
