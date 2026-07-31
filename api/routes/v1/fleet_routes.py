from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select as sa_select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import get_current_user, requer_permissao
from api.serializers.fleet_schema import (
    CustoReportItem,
    CustoReportResponse,
    DocumentoVencendoItem,
    DocumentoVencendoList,
    DriverCreate,
    DriverListResponse,
    DriverResponse,
    DriverUpdate,
    HistoricoListResponse,
    HistoricoResponse,
    KmRegistroCreate,
    KmRegistroListResponse,
    KmRegistroResponse,
    PneuCreate,
    PneuListResponse,
    PneuResponse,
    PneuUpdate,
    SeguroCreate,
    SeguroListResponse,
    SeguroResponse,
    SeguroUpdate,
    TrocaOleoCreate,
    TrocaOleoListResponse,
    TrocaOleoResponse,
    VehicleCreate,
    VehicleKmUpdate,
    VehicleListResponse,
    VehicleResponse,
    VehicleUpdate,
)
from core.domain.auth.papeis import Acao, Modulo
from database.models.funcionario import FuncionarioModel
from database.models.motorista import CategoriaCNH, MotoristaModel, MotoristaStatus
from database.models.veiculo import VeiculoModel, VeiculoProprietario, VeiculoStatus, VeiculoTipo
from database.models.veiculo_historico import VeiculoHistoricoEvento, VeiculoHistoricoModel
from database.models.veiculo_km_registro import KmRegistroModel
from database.models.veiculo_pneu import PneuMarca, PneuModel, PneuPosicao
from database.models.veiculo_seguro import SeguroModel, SeguroSeguradora
from database.models.veiculo_troca_oleo import TrocaOleoModel
from database.repositories.km_registro_repository_impl import KmRegistroRepositoryImpl
from database.repositories.motorista_repository_impl import MotoristaRepositoryImpl
from database.repositories.pneu_repository_impl import PneuRepositoryImpl
from database.repositories.seguro_repository_impl import SeguroRepositoryImpl
from database.repositories.troca_oleo_repository_impl import TrocaOleoRepositoryImpl
from database.repositories.veiculo_historico_repository_impl import VeiculoHistoricoRepositoryImpl
from database.repositories.veiculo_repository_impl import VeiculoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# VEÍCULOS
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/vehicles", response_model=VehicleListResponse)
async def list_vehicles(
    status: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> VehicleListResponse:
    repo = VeiculoRepositoryImpl(session)
    if search:
        items = await repo.search(search, skip=skip, limit=limit)
    elif status:
        items = await repo.find_by_status(status)
    else:
        items = await repo.find_all_active(skip=skip, limit=limit)
    total = len(items) if (search or status) else await repo.count_active()
    return VehicleListResponse(
        items=[VehicleResponse.model_validate(v) for v in items], total=total,
    )


@router.post("/vehicles", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    body: VehicleCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.CRIAR)),
) -> VehicleResponse:
    repo = VeiculoRepositoryImpl(session)
    existing = await repo.find_by_placa(body.placa)
    if existing:
        raise HTTPException(status_code=409, detail="Placa já cadastrada")

    def fmt(v: Decimal | None) -> float | None:
        return float(v) if v else None

    veiculo = VeiculoModel(
        placa=body.placa.upper(), renavam=body.renavam, chassi=body.chassi,
        marca=body.marca, modelo=body.modelo,
        ano_fabricacao=body.ano_fabricacao, ano_modelo=body.ano_modelo,
        cor=body.cor, tipo=VeiculoTipo(body.tipo),
        categoria=body.categoria,
        capacidade_carga_kg=fmt(body.capacidade_carga_kg),
        capacidade_volume_m3=fmt(body.capacidade_volume_m3),
        tipo_carroceria=body.tipo_carroceria,
        consumo_medio_km_l=fmt(body.consumo_medio_km_l),
        tanque_capacidade_l=fmt(body.tanque_capacidade_l),
        km_atual=body.km_atual, km_proxima_troca_oleo=body.km_proxima_troca_oleo,
        proprietario=VeiculoProprietario(body.proprietario),
        terceiro_nome=body.terceiro_nome, terceiro_cpf_cnpj=body.terceiro_cpf_cnpj,
        data_aquisicao=body.data_aquisicao,
        data_vencimento_seguro=body.data_vencimento_seguro,
        status=VeiculoStatus.DISPONIVEL, ativo=True,
    )
    veiculo = await repo.save(veiculo)

    historico_repo = VeiculoHistoricoRepositoryImpl(session)
    historico = VeiculoHistoricoModel(
        evento=VeiculoHistoricoEvento.CRIACAO, data_evento=date.today(),
        descricao=f"Veículo {body.placa} cadastrado",
        veiculo_id=veiculo.id,
        usuario_id=UUID(current_user["sub"]) if "sub" in current_user else None,
    )
    await historico_repo.save(historico)

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return VehicleResponse.model_validate(veiculo)


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> VehicleResponse:
    repo = VeiculoRepositoryImpl(session)
    vehicle = await repo.find_by_id(vehicle_id)
    if not vehicle or not vehicle.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return VehicleResponse.model_validate(vehicle)


@router.put("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    body: VehicleUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.ATUALIZAR)),
) -> VehicleResponse:
    repo = VeiculoRepositoryImpl(session)
    vehicle = await repo.find_by_id(vehicle_id)
    if not vehicle or not vehicle.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    float_fields = {"capacidade_carga_kg", "capacidade_volume_m3",
                    "consumo_medio_km_l", "tanque_capacidade_l"}
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field in float_fields:
                value = float(value)
            setattr(vehicle, field, value)

    await repo.save(vehicle)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return VehicleResponse.model_validate(vehicle)


@router.delete("/vehicles/{vehicle_id}", status_code=204)
async def delete_vehicle(
    vehicle_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.DELETAR)),
) -> None:
    repo = VeiculoRepositoryImpl(session)
    vehicle = await repo.find_by_id(vehicle_id)
    if not vehicle or not vehicle.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    await repo.soft_delete(vehicle)
    uow = AsyncUnitOfWork(session)
    await uow.commit()


@router.put("/vehicles/{vehicle_id}/km", response_model=VehicleResponse)
async def update_vehicle_km(
    vehicle_id: UUID,
    body: VehicleKmUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.ATUALIZAR)),
) -> VehicleResponse:
    repo = VeiculoRepositoryImpl(session)
    vehicle = await repo.find_by_id(vehicle_id)
    if not vehicle or not vehicle.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    if body.km <= vehicle.km_atual:
        raise HTTPException(status_code=400, detail="Novo KM deve ser maior que o atual")

    vehicle.km_atual = body.km

    km_repo = KmRegistroRepositoryImpl(session)
    await km_repo.save(KmRegistroModel(
        data=body.data or date.today(), km=body.km,
        tipo="leitura_manual", origem="atualizacao_manual",
        observacao=body.observacao, veiculo_id=vehicle_id,
    ))

    historico_repo = VeiculoHistoricoRepositoryImpl(session)
    await historico_repo.save(VeiculoHistoricoModel(
        evento=VeiculoHistoricoEvento.KM_ATUALIZADO, data_evento=date.today(),
        descricao=f"KM atualizado para {body.km}",
        veiculo_id=vehicle_id,
        usuario_id=UUID(current_user["sub"]) if "sub" in current_user else None,
    ))

    await repo.save(vehicle)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return VehicleResponse.model_validate(vehicle)


# ═══════════════════════════════════════════════════════════════════════════════
# VEÍCULO → QUILOMETRAGEM
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/vehicles/{vehicle_id}/kilometers", response_model=KmRegistroListResponse)
async def list_vehicle_kilometers(
    vehicle_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> KmRegistroListResponse:
    repo = KmRegistroRepositoryImpl(session)
    items = await repo.find_by_veiculo(vehicle_id, skip=skip, limit=limit)
    total = await repo.count_by_veiculo(vehicle_id)
    return KmRegistroListResponse(
        items=[KmRegistroResponse.model_validate(k) for k in items], total=total,
    )


@router.post(
    "/vehicles/{vehicle_id}/kilometers",
    response_model=KmRegistroResponse, status_code=201,
)
async def create_vehicle_kilometer(
    vehicle_id: UUID,
    body: KmRegistroCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.CRIAR)),
) -> KmRegistroResponse:
    veiculo_repo = VeiculoRepositoryImpl(session)
    vehicle = await veiculo_repo.find_by_id(vehicle_id)
    if not vehicle or not vehicle.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    repo = KmRegistroRepositoryImpl(session)
    registro = KmRegistroModel(
        data=body.data, km=body.km, tipo=body.tipo,
        origem=body.origem, observacao=body.observacao,
        veiculo_id=vehicle_id,
    )
    await repo.save(registro)
    if body.km > vehicle.km_atual:
        vehicle.km_atual = body.km

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return KmRegistroResponse.model_validate(registro)


# ═══════════════════════════════════════════════════════════════════════════════
# VEÍCULO → TROCA DE ÓLEO
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/vehicles/{vehicle_id}/oil-changes", response_model=TrocaOleoListResponse)
async def list_oil_changes(
    vehicle_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> TrocaOleoListResponse:
    repo = TrocaOleoRepositoryImpl(session)
    items = await repo.find_by_veiculo(vehicle_id, skip=skip, limit=limit)
    total = await repo.count_by_veiculo(vehicle_id)
    return TrocaOleoListResponse(
        items=[TrocaOleoResponse.model_validate(t) for t in items], total=total,
    )


@router.post(
    "/vehicles/{vehicle_id}/oil-changes",
    response_model=TrocaOleoResponse, status_code=201,
)
async def create_oil_change(
    vehicle_id: UUID,
    body: TrocaOleoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.CRIAR)),
) -> TrocaOleoResponse:
    veiculo_repo = VeiculoRepositoryImpl(session)
    vehicle = await veiculo_repo.find_by_id(vehicle_id)
    if not vehicle or not vehicle.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    repo = TrocaOleoRepositoryImpl(session)
    troca = TrocaOleoModel(
        data=body.data, km_atual=body.km_atual, tipo_oleo=body.tipo_oleo,
        quantidade_l=float(body.quantidade_l),
        valor_oleo=float(body.valor_oleo), valor_filtro=float(body.valor_filtro),
        valor_servico=float(body.valor_servico), valor_total=float(body.valor_total),
        oficina_nome=body.oficina_nome, km_proxima_troca=body.km_proxima_troca,
        observacao=body.observacao, veiculo_id=vehicle_id,
    )
    troca = await repo.save(troca)

    if body.km_proxima_troca:
        vehicle.km_proxima_troca_oleo = body.km_proxima_troca
    if body.km_atual > vehicle.km_atual:
        vehicle.km_atual = body.km_atual

    historico_repo = VeiculoHistoricoRepositoryImpl(session)
    desc = f"Troca de óleo: {body.tipo_oleo} ({body.quantidade_l}L)"
    await historico_repo.save(VeiculoHistoricoModel(
        evento=VeiculoHistoricoEvento.TROCA_OLEO, data_evento=body.data,
        descricao=desc, veiculo_id=vehicle_id,
        usuario_id=UUID(current_user["sub"]) if "sub" in current_user else None,
    ))

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return TrocaOleoResponse.model_validate(troca)


# ═══════════════════════════════════════════════════════════════════════════════
# VEÍCULO → PNEUS
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/vehicles/{vehicle_id}/tires", response_model=PneuListResponse)
async def list_tires(
    vehicle_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> PneuListResponse:
    repo = PneuRepositoryImpl(session)
    items = await repo.find_by_veiculo(vehicle_id, skip=skip, limit=limit)
    total = await repo.count_by_veiculo(vehicle_id)
    return PneuListResponse(
        items=[PneuResponse.model_validate(p) for p in items], total=total,
    )


@router.post(
    "/vehicles/{vehicle_id}/tires",
    response_model=PneuResponse, status_code=201,
)
async def create_tire(
    vehicle_id: UUID,
    body: PneuCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.CRIAR)),
) -> PneuResponse:
    veiculo_repo = VeiculoRepositoryImpl(session)
    vehicle = await veiculo_repo.find_by_id(vehicle_id)
    if not vehicle or not vehicle.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    repo = PneuRepositoryImpl(session)
    pneu = PneuModel(
        posicao=PneuPosicao(body.posicao), marca=PneuMarca(body.marca),
        modelo=body.modelo, medida=body.medida, numero_fogo=body.numero_fogo,
        km_instalacao=body.km_instalacao, data_instalacao=body.data_instalacao,
        vida_util_km=body.vida_util_km,
        valor_unitario=float(body.valor_unitario) if body.valor_unitario else None,
        observacao=body.observacao, veiculo_id=vehicle_id,
    )
    pneu = await repo.save(pneu)

    historico_repo = VeiculoHistoricoRepositoryImpl(session)
    desc = f"Pneu instalado: {body.marca} {body.modelo} ({body.medida})"
    await historico_repo.save(VeiculoHistoricoModel(
        evento=VeiculoHistoricoEvento.TROCA_PNEU, data_evento=body.data_instalacao,
        descricao=desc, veiculo_id=vehicle_id,
        usuario_id=UUID(current_user["sub"]) if "sub" in current_user else None,
    ))

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return PneuResponse.model_validate(pneu)


@router.put("/vehicles/{vehicle_id}/tires/{tire_id}", response_model=PneuResponse)
async def update_tire(
    vehicle_id: UUID,
    tire_id: UUID,
    body: PneuUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.ATUALIZAR)),
) -> PneuResponse:
    repo = PneuRepositoryImpl(session)
    pneu = await repo.find_by_id(tire_id)
    if not pneu or pneu.veiculo_id != vehicle_id:
        raise HTTPException(status_code=404, detail="Pneu não encontrado")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(pneu, field, value)

    await repo.save(pneu)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return PneuResponse.model_validate(pneu)


# ═══════════════════════════════════════════════════════════════════════════════
# VEÍCULO → SEGURO
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/vehicles/{vehicle_id}/insurance", response_model=SeguroListResponse)
async def list_insurance(
    vehicle_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> SeguroListResponse:
    repo = SeguroRepositoryImpl(session)
    items = await repo.find_by_veiculo(vehicle_id, skip=skip, limit=limit)
    total = await repo.count_by_veiculo(vehicle_id)
    return SeguroListResponse(
        items=[SeguroResponse.model_validate(s) for s in items], total=total,
    )


@router.post(
    "/vehicles/{vehicle_id}/insurance",
    response_model=SeguroResponse, status_code=201,
)
async def create_insurance(
    vehicle_id: UUID,
    body: SeguroCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.CRIAR)),
) -> SeguroResponse:
    veiculo_repo = VeiculoRepositoryImpl(session)
    vehicle = await veiculo_repo.find_by_id(vehicle_id)
    if not vehicle or not vehicle.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    repo = SeguroRepositoryImpl(session)
    seguro = SeguroModel(
        apolice=body.apolice, seguradora=SeguroSeguradora(body.seguradora),
        data_inicio_vigencia=body.data_inicio_vigencia,
        data_fim_vigencia=body.data_fim_vigencia,
        data_contratacao=body.data_contratacao,
        premio_total=float(body.premio_total),
        premio_parcela=float(body.premio_parcela) if body.premio_parcela else None,
        numero_parcelas=body.numero_parcelas,
        coberturas=body.coberturas,
        valor_cobertura_terceiros=(
            float(body.valor_cobertura_terceiros) if body.valor_cobertura_terceiros else None
        ),
        valor_franquia=float(body.valor_franquia) if body.valor_franquia else None,
        observacao=body.observacao, veiculo_id=vehicle_id,
    )
    seguro = await repo.save(seguro)
    vehicle.data_vencimento_seguro = body.data_fim_vigencia

    historico_repo = VeiculoHistoricoRepositoryImpl(session)
    desc = f"Seguro {body.apolice} - vigência até {body.data_fim_vigencia}"
    await historico_repo.save(VeiculoHistoricoModel(
        evento=VeiculoHistoricoEvento.SEGURO, data_evento=date.today(),
        descricao=desc, veiculo_id=vehicle_id,
        usuario_id=UUID(current_user["sub"]) if "sub" in current_user else None,
    ))

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return SeguroResponse.model_validate(seguro)


@router.put("/vehicles/{vehicle_id}/insurance/{seguro_id}", response_model=SeguroResponse)
async def update_insurance(
    vehicle_id: UUID,
    seguro_id: UUID,
    body: SeguroUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.ATUALIZAR)),
) -> SeguroResponse:
    repo = SeguroRepositoryImpl(session)
    seguro = await repo.find_by_id(seguro_id)
    if not seguro or seguro.veiculo_id != vehicle_id:
        raise HTTPException(status_code=404, detail="Seguro não encontrado")

    float_fields = {"premio_total", "premio_parcela",
                    "valor_cobertura_terceiros", "valor_franquia"}
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field in float_fields:
                value = float(value)
            setattr(seguro, field, value)

    await repo.save(seguro)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return SeguroResponse.model_validate(seguro)


# ═══════════════════════════════════════════════════════════════════════════════
# VEÍCULO → HISTÓRICO
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/vehicles/{vehicle_id}/history", response_model=HistoricoListResponse)
async def list_vehicle_history(
    vehicle_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> HistoricoListResponse:
    repo = VeiculoHistoricoRepositoryImpl(session)
    items = await repo.find_by_veiculo(vehicle_id, skip=skip, limit=limit)
    total = await repo.count_by_veiculo(vehicle_id)
    return HistoricoListResponse(
        items=[HistoricoResponse.model_validate(h) for h in items], total=total,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MOTORISTAS
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/drivers", response_model=DriverListResponse)
async def list_drivers(
    status: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> DriverListResponse:
    repo = MotoristaRepositoryImpl(session)
    if search:
        items = await repo.search(search, skip=skip, limit=limit)
    elif status:
        items = await repo.find_by_status(status)
    else:
        items = await repo.find_all_active(skip=skip, limit=limit)
    total = len(items) if (search or status) else await repo.count_active()
    return DriverListResponse(
        items=[DriverResponse.model_validate(d) for d in items], total=total,
    )


@router.post("/drivers", response_model=DriverResponse, status_code=201)
async def create_driver(
    body: DriverCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.CRIAR)),
) -> DriverResponse:
    repo = MotoristaRepositoryImpl(session)
    existing = await repo.find_by_cnh(body.numero_cnh)
    if existing:
        raise HTTPException(status_code=409, detail="CNH já cadastrada")

    motorista = MotoristaModel(
        numero_cnh=body.numero_cnh, categoria_cnh=CategoriaCNH(body.categoria_cnh),
        data_validade_cnh=body.data_validade_cnh,
        data_primeira_cnh=body.data_primeira_cnh,
        orgao_emissor_cnh=body.orgao_emissor_cnh,
        cnh_observacao=body.cnh_observacao,
        data_ultimo_exame_medico=body.data_ultimo_exame_medico,
        data_validade_exame_medico=body.data_validade_exame_medico,
        certificacoes=body.certificacoes, telefone=body.telefone, email=body.email,
        status=MotoristaStatus.DISPONIVEL, ativo=True,
        funcionario_id=body.funcionario_id,
    )
    motorista = await repo.save(motorista)

    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return DriverResponse.model_validate(motorista)


@router.get("/drivers/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> DriverResponse:
    repo = MotoristaRepositoryImpl(session)
    driver = await repo.find_by_id(driver_id)
    if not driver or not driver.ativo:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")
    return DriverResponse.model_validate(driver)


@router.put("/drivers/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: UUID,
    body: DriverUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.ATUALIZAR)),
) -> DriverResponse:
    repo = MotoristaRepositoryImpl(session)
    driver = await repo.find_by_id(driver_id)
    if not driver or not driver.ativo:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    update_data = body.model_dump(exclude_unset=True)
    if "categoria_cnh" in update_data and update_data["categoria_cnh"] is not None:
        update_data["categoria_cnh"] = CategoriaCNH(update_data["categoria_cnh"])
    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = MotoristaStatus(update_data["status"])
    for field, value in update_data.items():
        if value is not None:
            setattr(driver, field, value)

    await repo.save(driver)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return DriverResponse.model_validate(driver)


@router.delete("/drivers/{driver_id}", status_code=204)
async def delete_driver(
    driver_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.DELETAR)),
) -> None:
    repo = MotoristaRepositoryImpl(session)
    driver = await repo.find_by_id(driver_id)
    if not driver or not driver.ativo:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")
    await repo.soft_delete(driver)
    uow = AsyncUnitOfWork(session)
    await uow.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# RELATÓRIOS
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/reports/costs", response_model=CustoReportResponse)
async def fleet_cost_report(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.RELATORIOS, Acao.LER)),
) -> CustoReportResponse:
    repo = VeiculoRepositoryImpl(session)
    vehicles = await repo.find_with_custos_periodo(data_inicio, data_fim)

    items = []
    total_geral = 0.0
    for v in vehicles:
        total_comb = sum(
            float(a.valor_total) for a in (v.abastecimentos or [])
            if data_inicio <= a.data.date() <= data_fim
        )
        total_manut = sum(
            float(m.valor_total) for m in (v.manutencoes or [])
            if (m.data_inicio and data_inicio <= m.data_inicio <= data_fim)
            or (m.data_fim and data_inicio <= m.data_fim <= data_fim)
        )
        total_multas = sum(
            float(m.valor_original) for m in (v.multas or [])
            if data_inicio <= m.data_infracao <= data_fim
        )
        total_seg = sum(
            float(s.premio_total) for s in (v.seguros or [])
            if data_inicio <= s.data_inicio_vigencia <= data_fim
        )
        total_oleo = sum(
            float(t.valor_total) for t in (v.trocas_oleo or [])
            if data_inicio <= t.data <= data_fim
        )
        total = total_comb + total_manut + total_multas + total_seg + total_oleo
        total_geral += total
        items.append(CustoReportItem(
            veiculo_id=v.id, placa=v.placa,
            total_combustivel=Decimal(str(round(total_comb, 2))),
            total_manutencao=Decimal(str(round(total_manut, 2))),
            total_multas=Decimal(str(round(total_multas, 2))),
            total_seguros=Decimal(str(round(total_seg, 2))),
            total_troca_oleo=Decimal(str(round(total_oleo, 2))),
            total_geral=Decimal(str(round(total, 2))),
        ))

    return CustoReportResponse(
        items=items, total_geral=Decimal(str(round(total_geral, 2))),
        data_inicio=data_inicio, data_fim=data_fim,
    )


@router.get("/reports/expiring-documents", response_model=DocumentoVencendoList)
async def expiring_documents_report(
    dias: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.RELATORIOS, Acao.LER)),
) -> DocumentoVencendoList:
    today = date.today()
    deadline = today + timedelta(days=dias)
    items: list[DocumentoVencendoItem] = []

    seguro_repo = SeguroRepositoryImpl(session)
    seguros = await seguro_repo.find_ativos_vencendo(dias)
    for s in seguros:
        items.append(DocumentoVencendoItem(
            tipo="seguro",
            descricao=f"Seguro {s.apolice} - {s.seguradora.value}",
            veiculo_id=s.veiculo_id, placa="",
            data_vencimento=s.data_fim_vigencia,
            dias_para_vencer=(s.data_fim_vigencia - today).days,
            status=s.status.value,
        ))

    stmt = sa_select(MotoristaModel).where(
        MotoristaModel.ativo.is_(True),
        MotoristaModel.data_validade_cnh <= deadline,
    )
    result = await session.execute(stmt)
    motoristas = list(result.scalars().all())
    for m in motoristas:
        func = await session.get(FuncionarioModel, m.funcionario_id)
        items.append(DocumentoVencendoItem(
            tipo="cnh",
            descricao=f"CNH {m.numero_cnh} - {func.nome if func else ''}",
            motorista_id=m.id, motorista_nome=func.nome if func else None,
            data_vencimento=m.data_validade_cnh,
            dias_para_vencer=(m.data_validade_cnh - today).days,
            status=m.status.value,
        ))

    items.sort(key=lambda x: x.dias_para_vencer)

    veiculo_repo = VeiculoRepositoryImpl(session)
    for item in items:
        if item.veiculo_id and not item.placa:
            v = await veiculo_repo.find_by_id(item.veiculo_id)
            if v:
                item.placa = v.placa

    return DocumentoVencendoList(items=items)
