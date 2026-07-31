from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    tipo_pessoa: str = Field(pattern="^(PF|PJ)$")
    nome_razao_social: str = Field(..., max_length=200)
    cpf_cnpj: str = Field(..., min_length=11, max_length=14)
    email: str | None = None
    telefone: str | None = Field(None, max_length=20)
    celular: str | None = Field(None, max_length=20)


class CustomerCreate(CustomerBase):
    nome_fantasia: str | None = Field(None, max_length=200)
    rg_ie: str | None = None
    endereco_id: UUID | None = None
    limite_credito: Decimal = Decimal("0")


class CustomerUpdate(BaseModel):
    nome_razao_social: str | None = Field(None, max_length=200)
    nome_fantasia: str | None = None
    email: str | None = None
    telefone: str | None = None
    celular: str | None = None
    rg_ie: str | None = None
    limite_credito: Decimal | None = None
    status: str | None = Field(None, pattern="^(ativo|inativo|bloqueado)$")


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome_fantasia: str | None = None
    rg_ie: str | None = None
    limite_credito: Decimal = Decimal("0")
    saldo_disponivel: Decimal = Decimal("0")
    status: str = "ativo"
    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    skip: int
    limit: int
