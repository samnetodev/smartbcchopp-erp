from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditoriaEventoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID | None
    entidade_tipo: str
    entidade_id: UUID
    acao: str
    dados_anteriores: dict[str, Any] | None
    dados_novos: dict[str, Any] | None
    ip_origem: str | None
    user_agent: str | None
    created_at: datetime


class AuditoriaListResponse(BaseModel):
    items: list[AuditoriaEventoResponse]
    total: int
