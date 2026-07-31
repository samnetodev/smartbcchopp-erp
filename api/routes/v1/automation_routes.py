from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from database.repositories.alerta_repository_impl import AlertaRepositoryImpl
from infrastructure.automation.registry import list_job_info

router = APIRouter()


@router.get("/jobs", summary="Listar todos os jobs de automação")
async def listar_jobs() -> list[dict[str, Any]]:
    """Retorna metadados de todos os jobs de automação registrados."""
    return list_job_info()


@router.get("/alertas", summary="Listar alertas gerados")
async def listar_alertas(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    """Retorna os alertas mais recentes."""
    repo = AlertaRepositoryImpl(session)
    alertas = await repo.find_all(skip=skip, limit=limit)
    return [
        {
            "id": str(a.id),
            "tipo": a.tipo,
            "nivel": a.nivel.value if hasattr(a.nivel, "value") else str(a.nivel),
            "titulo": a.titulo,
            "mensagem": a.mensagem,
            "lido": a.lido,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alertas
    ]


@router.get("/alertas/nao-lidos", summary="Contar alertas não lidos")
async def contar_alertas_nao_lidos(
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    repo = AlertaRepositoryImpl(session)
    total = await repo.count_nao_lidos()
    return {"total_nao_lidos": total}


@router.patch("/alertas/{alerta_id}/ler", summary="Marcar alerta como lido")
async def marcar_alerta_lido(
    alerta_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    from uuid import UUID

    repo = AlertaRepositoryImpl(session)
    alerta = await repo.find_by_id(UUID(alerta_id))
    if not alerta:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    alerta.lido = True
    from database.unit_of_work import AsyncUnitOfWork
    uow = AsyncUnitOfWork(session)
    await uow.commit()
    return {"status": "ok"}
