from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import get_current_user, requer_permissao
from api.serializers.chopeira_schema import (
    ChopeiraCreate,
    ChopeiraListResponse,
    ChopeiraMaintenanceDueItem,
    ChopeiraMaintenanceDueList,
    ChopeiraResponse,
    ChopeiraUpdate,
    HistoricoListResponse,
    HistoricoResponse,
    InstallChopeiraInput,
    ManutencaoCreate,
    ManutencaoListResponse,
    ManutencaoResponse,
    ManutencaoUpdate,
    StatusCount,
)
from core.domain.auth.papeis import Acao, Modulo
from database.models.chopeira import ChopeiraModel, ChopeiraStatus, ChopeiraTipo
from database.models.chopeira_historico import ChopeiraHistoricoModel, HistoricoEvento
from database.models.chopeira_manutencao import (
    ChopeiraManutencaoModel,
    ManutencaoStatus,
    ManutencaoTipo,
)
from database.models.cliente import ClienteModel
from database.repositories.chopeira_historico_repository_impl import (
    ChopeiraHistoricoRepositoryImpl,
)
from database.repositories.chopeira_manutencao_repository_impl import (
    ChopeiraManutencaoRepositoryImpl,
)
from database.repositories.chopeira_repository_impl import ChopeiraRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


# ─── CRUD Chopeira ────────────────────────────────────────────────────────────


@router.get("/", response_model=ChopeiraListResponse)
async def list_chopeiras(
    status: str | None = None,
    search: str | None = None,
    cliente_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.LER)),
) -> ChopeiraListResponse:
    repo = ChopeiraRepositoryImpl(session)

    if cliente_id:
        items = await repo.find_by_cliente(cliente_id)
    elif search:
        items = await repo.search(search, skip=skip, limit=limit)
    else:
        items = await repo.find_all_active(skip=skip, limit=limit)

    total = len(items)
    return ChopeiraListResponse(
        items=[ChopeiraResponse.model_validate(c) for c in items],
        total=total,
    )


@router.post("/", response_model=ChopeiraResponse, status_code=201)
async def create_chopeira(
    body: ChopeiraCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.CRIAR)),
) -> ChopeiraResponse:
    repo = ChopeiraRepositoryImpl(session)
    existing = await repo.find_by_codigo(body.codigo_identificacao)
    if existing:
        raise HTTPException(status_code=409, detail="Código de identificação já existe")

    chopeira = ChopeiraModel(
        codigo_identificacao=body.codigo_identificacao,
        numero_serie=body.numero_serie,
        marca=body.marca,
        modelo=body.modelo,
        tipo=ChopeiraTipo(body.tipo) if body.tipo else ChopeiraTipo.CHOPEIRA,
        capacidade_l=float(body.capacidade_l) if body.capacidade_l else None,
        local_instalacao=body.local_instalacao,
        latitude=float(body.latitude) if body.latitude else None,
        longitude=float(body.longitude) if body.longitude else None,
        observacao=body.observacao,
        status=ChopeiraStatus.DISPONIVEL,
        ativo=True,
    )
    chopeira = await repo.save(chopeira)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return ChopeiraResponse.model_validate(chopeira)


@router.get("/{chopeira_id}", response_model=ChopeiraResponse)
async def get_chopeira(
    chopeira_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.LER)),
) -> ChopeiraResponse:
    repo = ChopeiraRepositoryImpl(session)
    chopeira = await repo.find_by_id(chopeira_id)
    if not chopeira or not chopeira.ativo:
        raise HTTPException(status_code=404, detail="Chopeira não encontrada")
    return ChopeiraResponse.model_validate(chopeira)


@router.put("/{chopeira_id}", response_model=ChopeiraResponse)
async def update_chopeira(
    chopeira_id: UUID,
    body: ChopeiraUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.ATUALIZAR)),
) -> ChopeiraResponse:
    repo = ChopeiraRepositoryImpl(session)
    chopeira = await repo.find_by_id(chopeira_id)
    if not chopeira or not chopeira.ativo:
        raise HTTPException(status_code=404, detail="Chopeira não encontrada")

    update_data = body.model_dump(exclude_unset=True)
    if "tipo" in update_data:
        update_data["tipo"] = ChopeiraTipo(body.tipo)
    for field, value in update_data.items():
        setattr(chopeira, field, value)

    await repo.save(chopeira)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return ChopeiraResponse.model_validate(chopeira)


@router.delete("/{chopeira_id}", status_code=204)
async def delete_chopeira(
    chopeira_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.DELETAR)),
) -> None:
    repo = ChopeiraRepositoryImpl(session)
    chopeira = await repo.find_by_id(chopeira_id)
    if not chopeira or not chopeira.ativo:
        raise HTTPException(status_code=404, detail="Chopeira não encontrada")
    await repo.soft_delete(chopeira)
    uow = AsyncUnitOfWork(session)
    await uow.commit()


# ─── Instalação / Desinstalação ────────────────────────────────────────────────


@router.post("/{chopeira_id}/install", response_model=ChopeiraResponse)
async def install_chopeira(
    chopeira_id: UUID,
    body: InstallChopeiraInput,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.ATUALIZAR)),
) -> ChopeiraResponse:
    repo = ChopeiraRepositoryImpl(session)
    chopeira = await repo.find_by_id(chopeira_id)
    if not chopeira or not chopeira.ativo:
        raise HTTPException(status_code=404, detail="Chopeira não encontrada")

    cliente = await session.get(ClienteModel, body.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    chopeira.cliente_id = body.cliente_id
    chopeira.status = ChopeiraStatus.INSTALADA
    chopeira.data_instalacao = body.data_instalacao or date.today()
    chopeira.local_instalacao = body.local_instalacao
    chopeira.latitude = float(body.latitude) if body.latitude else None
    chopeira.longitude = float(body.longitude) if body.longitude else None
    chopeira.observacao = body.observacao or chopeira.observacao

    await repo.save(chopeira)

    historico_repo = ChopeiraHistoricoRepositoryImpl(session)
    historico = ChopeiraHistoricoModel(
        evento=HistoricoEvento.INSTALACAO,
        data_evento=date.today(),
        descricao=f"Instalação no cliente {cliente.nome_razao_social or body.cliente_id}",
        chopeira_id=chopeira_id,
        cliente_id=body.cliente_id,
        usuario_id=UUID(current_user["sub"]) if "sub" in current_user else None,
    )
    await historico_repo.save(historico)

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return ChopeiraResponse.model_validate(chopeira)


@router.post("/{chopeira_id}/uninstall", response_model=ChopeiraResponse)
async def uninstall_chopeira(
    chopeira_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.ATUALIZAR)),
) -> ChopeiraResponse:
    repo = ChopeiraRepositoryImpl(session)
    chopeira = await repo.find_by_id(chopeira_id)
    if not chopeira or not chopeira.ativo:
        raise HTTPException(status_code=404, detail="Chopeira não encontrada")

    cliente_id = chopeira.cliente_id
    chopeira.cliente_id = None
    chopeira.status = ChopeiraStatus.DISPONIVEL
    chopeira.data_instalacao = None
    chopeira.local_instalacao = None

    await repo.save(chopeira)

    historico_repo = ChopeiraHistoricoRepositoryImpl(session)
    historico = ChopeiraHistoricoModel(
        evento=HistoricoEvento.DESINSTALACAO,
        data_evento=date.today(),
        chopeira_id=chopeira_id,
        cliente_id=cliente_id,
        usuario_id=UUID(current_user["sub"]) if "sub" in current_user else None,
    )
    await historico_repo.save(historico)

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return ChopeiraResponse.model_validate(chopeira)


# ─── Histórico ────────────────────────────────────────────────────────────────


@router.get("/{chopeira_id}/history", response_model=HistoricoListResponse)
async def list_chopeira_history(
    chopeira_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.LER)),
) -> HistoricoListResponse:
    repo = ChopeiraHistoricoRepositoryImpl(session)
    items = await repo.find_by_chopeira(chopeira_id, skip=skip, limit=limit)
    total = await repo.count_by_chopeira(chopeira_id)
    return HistoricoListResponse(
        items=[HistoricoResponse.model_validate(h) for h in items],
        total=total,
    )


# ─── Manutenção ───────────────────────────────────────────────────────────────


@router.get("/{chopeira_id}/maintenance", response_model=ManutencaoListResponse)
async def list_maintenance(
    chopeira_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.LER)),
) -> ManutencaoListResponse:
    repo = ChopeiraManutencaoRepositoryImpl(session)
    items = await repo.find_by_chopeira(chopeira_id, skip=skip, limit=limit)
    total = await repo.count_by_chopeira(chopeira_id)
    return ManutencaoListResponse(
        items=[ManutencaoResponse.model_validate(m) for m in items],
        total=total,
    )


@router.post("/{chopeira_id}/maintenance", response_model=ManutencaoResponse, status_code=201)
async def create_maintenance(
    chopeira_id: UUID,
    body: ManutencaoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.CRIAR)),
) -> ManutencaoResponse:
    repo = ChopeiraManutencaoRepositoryImpl(session)

    manutencao = ChopeiraManutencaoModel(
        tipo=ManutencaoTipo(body.tipo),
        status=ManutencaoStatus.AGENDADA,
        data_solicitacao=body.data_solicitacao,
        data_inicio=body.data_inicio,
        data_fim=body.data_fim,
        descricao_problema=body.descricao_problema,
        descricao_servico=body.descricao_servico,
        tecnico_responsavel=body.tecnico_responsavel,
        custo_pecas=float(body.custo_pecas) if body.custo_pecas else 0,
        custo_servico=float(body.custo_servico) if body.custo_servico else 0,
        chopeira_id=chopeira_id,
    )
    manutencao = await repo.save(manutencao)

    chopeira_repo = ChopeiraRepositoryImpl(session)
    chopeira = await chopeira_repo.find_by_id(chopeira_id)
    if chopeira:
        chopeira.status = ChopeiraStatus.MANUTENCAO
        chopeira.data_ultima_manutencao = body.data_solicitacao

    historico_repo = ChopeiraHistoricoRepositoryImpl(session)
    historico = ChopeiraHistoricoModel(
        evento=HistoricoEvento.MANUTENCAO,
        data_evento=body.data_solicitacao,
        descricao=f"Manutenção {body.tipo} agendada: {body.descricao_problema or 'sem descrição'}",
        chopeira_id=chopeira_id,
        usuario_id=UUID(current_user["sub"]) if "sub" in current_user else None,
    )
    await historico_repo.save(historico)

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return ManutencaoResponse.model_validate(manutencao)


@router.put("/maintenance/{manutencao_id}", response_model=ManutencaoResponse)
async def update_maintenance(
    manutencao_id: UUID,
    body: ManutencaoUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.ATUALIZAR)),
) -> ManutencaoResponse:
    repo = ChopeiraManutencaoRepositoryImpl(session)
    manutencao = await repo.find_by_id(manutencao_id)
    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")

    update_data = body.model_dump(exclude_unset=True)
    if "tipo" in update_data:
        update_data["tipo"] = ManutencaoTipo(body.tipo)
    if "status" in update_data:
        update_data["status"] = ManutencaoStatus(body.status)
    for field, value in update_data.items():
        setattr(manutencao, field, value)

    await repo.save(manutencao)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return ManutencaoResponse.model_validate(manutencao)


@router.post("/maintenance/{manutencao_id}/complete", response_model=ManutencaoResponse)
async def complete_maintenance(
    manutencao_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.ATUALIZAR)),
) -> ManutencaoResponse:
    repo = ChopeiraManutencaoRepositoryImpl(session)
    manutencao = await repo.find_by_id(manutencao_id)
    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")

    manutencao.status = ManutencaoStatus.CONCLUIDA
    manutencao.data_fim = date.today()
    await repo.save(manutencao)

    chopeira_repo = ChopeiraRepositoryImpl(session)
    chopeira = await chopeira_repo.find_by_id(manutencao.chopeira_id)
    if chopeira:
        if chopeira.cliente_id:
            chopeira.status = ChopeiraStatus.INSTALADA
        else:
            chopeira.status = ChopeiraStatus.DISPONIVEL
        chopeira.data_ultima_manutencao = date.today()

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return ManutencaoResponse.model_validate(manutencao)


# ─── Alertas ──────────────────────────────────────────────────────────────────


@router.get("/{chopeira_id}/alerts")
async def list_chopeira_alerts(
    chopeira_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.LER)),
) -> list[dict[str, Any]]:
    from database.models.alerta import AlertaModel

    repo = ChopeiraRepositoryImpl(session)
    chopeira = await repo.find_by_id(chopeira_id)
    if not chopeira or not chopeira.ativo:
        raise HTTPException(status_code=404, detail="Chopeira não encontrada")

    stmt = (
        AlertaModel.__table__.select()
        .where(
            AlertaModel.entidade_tipo == "chopeira",
            AlertaModel.entidade_id == chopeira_id,
        )
        .order_by(AlertaModel.created_at.desc())
    )
    result = await session.execute(stmt)
    rows = result.mappings().all()
    return [dict(row) for row in rows]


# ─── Disponibilidade / Status ─────────────────────────────────────────────────


@router.get("/status-counts", response_model=list[StatusCount])
async def chopeira_status_counts(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.LER)),
) -> list[StatusCount]:
    repo = ChopeiraRepositoryImpl(session)
    counts = await repo.count_by_status()
    return [
        StatusCount(status=k, total=v)
        for k, v in sorted(counts.items())
    ]


@router.get("/available", response_model=ChopeiraListResponse)
async def list_available_chopeiras(
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.LER)),
) -> ChopeiraListResponse:
    repo = ChopeiraRepositoryImpl(session)
    items = await repo.find_by_status(ChopeiraStatus.DISPONIVEL)
    return ChopeiraListResponse(
        items=[ChopeiraResponse.model_validate(c) for c in items],
        total=len(items),
    )


@router.get("/reports/maintenance-due", response_model=ChopeiraMaintenanceDueList)
async def maintenance_due_report(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CHOPEIRAS, Acao.LER)),
) -> ChopeiraMaintenanceDueList:
    repo = ChopeiraRepositoryImpl(session)
    items = await repo.find_maintenance_due(limit_days=days)
    today = date.today()
    result = []
    for c in items:
        if c.data_proxima_manutencao is None:
            continue
        cliente_nome = c.cliente.nome if c.cliente else None
        dias = (c.data_proxima_manutencao - today).days
        result.append(
            ChopeiraMaintenanceDueItem(
                id=c.id,
                codigo_identificacao=c.codigo_identificacao,
                marca=c.marca,
                modelo=c.modelo,
                data_proxima_manutencao=c.data_proxima_manutencao,
                cliente_nome=cliente_nome,
                dias_para_vencer=dias,
            )
        )
    return ChopeiraMaintenanceDueList(items=result)
