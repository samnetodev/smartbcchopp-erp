from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import requer_permissao
from api.serializers.auditoria_schema import AuditoriaEventoResponse, AuditoriaListResponse
from core.domain.auth.papeis import Acao, Modulo
from database.repositories.auditoria_repository_impl import AuditoriaRepositoryImpl

router = APIRouter()


@router.get("/", response_model=AuditoriaListResponse)
async def list_auditoria(
    entidade_tipo: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.USUARIOS, Acao.LER)),
) -> AuditoriaListResponse:
    repo = AuditoriaRepositoryImpl(session)
    items = await repo.find_all(entidade_tipo=entidade_tipo, skip=skip, limit=limit)
    total = await repo.count(entidade_tipo)
    return AuditoriaListResponse(
        items=[AuditoriaEventoResponse.model_validate(i) for i in items],
        total=total,
    )
