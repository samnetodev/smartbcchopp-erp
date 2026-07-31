from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VehicleBase(BaseModel):
    placa: str = Field(..., max_length=7)
    marca: str = Field(..., max_length=50)
    modelo: str = Field(..., max_length=50)
    tipo: str = Field(pattern="^(caminhao|van|carro|utilitario)$")
    proprietario: str = Field(pattern="^(proprio|terceiro)$")


class VehicleCreate(VehicleBase):
    renavam: str | None = None
    chassi: str | None = None
    ano_fabricacao: int | None = None
    ano_modelo: int | None = None
    cor: str | None = None
    categoria: str | None = Field(None, pattern="^(leve|medio|pesado)$")
    capacidade_carga_kg: Decimal | None = None
    tipo_carroceria: str | None = Field(None, pattern="^(bau|graneleiro|tanque|sider|aberta)$")
    km_atual: int = 0


class VehicleUpdate(BaseModel):
    placa: str | None = None
    status: str | None = Field(None, pattern="^(disponivel|em_rota|manutencao|inativo)$")
    km_atual: int | None = None
    cor: str | None = None


class VehicleResponse(VehicleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    renavam: str | None = None
    chassi: str | None = None
    ano_fabricacao: int | None = None
    ano_modelo: int | None = None
    cor: str | None = None
    categoria: str | None = None
    capacidade_carga_kg: Decimal | None = None
    km_atual: int = 0
    status: str = "disponivel"
    created_at: datetime
    updated_at: datetime


class VehicleListResponse(BaseModel):
    items: list[VehicleResponse]
    total: int
    skip: int
    limit: int
