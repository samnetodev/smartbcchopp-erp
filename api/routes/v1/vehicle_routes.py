from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import requer_permissao
from api.serializers.vehicle_schema import (
    VehicleCreate,
    VehicleListResponse,
    VehicleResponse,
    VehicleUpdate,
)
from core.domain.auth.papeis import Acao, Modulo
from database.models.veiculo import VeiculoModel, VeiculoProprietario, VeiculoTipo
from database.repositories.veiculo_repository_impl import VeiculoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


@router.get("/", response_model=VehicleListResponse)
async def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: str | None = None,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> VehicleListResponse:
    repo = VeiculoRepositoryImpl(session)

    if status:
        items = await repo.find_by_status(status)
        total = len(items)
    else:
        items = await repo.find_all(skip=skip, limit=limit)
        total = await repo.count()

    return VehicleListResponse(
        items=[VehicleResponse.model_validate(v) for v in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.LER)),
) -> VehicleResponse:
    repo = VeiculoRepositoryImpl(session)
    vehicle = await repo.find_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return VehicleResponse.model_validate(vehicle)


@router.post("/", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    body: VehicleCreate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.CRIAR)),
) -> VehicleResponse:
    repo = VeiculoRepositoryImpl(session)

    vehicle = VeiculoModel(
        placa=body.placa,
        marca=body.marca,
        modelo=body.modelo,
        ano_fabricacao=body.ano_fabricacao,
        capacidade_carga_kg=(
            float(body.capacidade_carga_kg) if body.capacidade_carga_kg is not None else None
        ),
        tipo=VeiculoTipo(body.tipo),
        renavam=body.renavam,
        proprietario=VeiculoProprietario(body.proprietario),
    )

    await repo.save(vehicle)
    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return VehicleResponse.model_validate(vehicle)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    body: VehicleUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.ATUALIZAR)),
) -> VehicleResponse:
    repo = VeiculoRepositoryImpl(session)
    vehicle = await repo.find_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "capacidade_carga_kg":
                value = float(value)
            setattr(vehicle, field, value)

    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return VehicleResponse.model_validate(vehicle)


@router.delete("/{vehicle_id}", status_code=204)
async def delete_vehicle(
    vehicle_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.VEICULOS, Acao.DELETAR)),
) -> None:
    repo = VeiculoRepositoryImpl(session)
    vehicle = await repo.find_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    vehicle.ativo = False
    uow = AsyncUnitOfWork(session)
    await uow.commit()
