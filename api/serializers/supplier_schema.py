from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SupplierBase(BaseModel):
    nome_razao_social: str = Field(..., max_length=200)
    cpf_cnpj: str = Field(..., min_length=11, max_length=14)
    categoria: str = Field(pattern="^(chope|carvao|transporte|insumos|servicos|outros)$")


class SupplierCreate(SupplierBase):
    tipo_pessoa: str = Field("PJ", pattern="^(PF|PJ)$")
    nome_fantasia: str | None = None
    email: str | None = None
    telefone: str | None = None
    contato_nome: str | None = None
    inscricao_estadual: str | None = None


class SupplierUpdate(BaseModel):
    nome_razao_social: str | None = None
    email: str | None = None
    telefone: str | None = None
    contato_nome: str | None = None
    status: str | None = Field(None, pattern="^(ativo|inativo|bloqueado)$")


class SupplierResponse(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tipo_pessoa: str
    nome_fantasia: str | None = None
    email: str | None = None
    telefone: str | None = None
    contato_nome: str | None = None
    status: str = "ativo"
    created_at: datetime
    updated_at: datetime


class SupplierListResponse(BaseModel):
    items: list[SupplierResponse]
    total: int
