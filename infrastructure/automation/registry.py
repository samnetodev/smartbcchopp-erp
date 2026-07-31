from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from infrastructure.automation.base import BaseJob

logger = logging.getLogger(__name__)

_job_registry: dict[str, type[BaseJob]] = {}


def register_job(job_cls: type[BaseJob]) -> type[BaseJob]:
    """Decorator para registrar um job de automação."""
    instance = job_cls()
    jid = instance.job_id()
    if jid in _job_registry:
        logger.warning("Job '%s' já registrado — sobrescrevendo", jid)
    _job_registry[jid] = job_cls
    logger.debug("Job registrado: %s (%s)", jid, instance.description())
    return job_cls


def get_all_jobs() -> dict[str, type[BaseJob]]:
    """Retorna o dicionário de jobs registrados."""
    return dict(_job_registry)


def get_job(job_id: str) -> type[BaseJob] | None:
    """Retorna a classe de um job específico."""
    return _job_registry.get(job_id)


def list_job_info() -> list[dict[str, Any]]:
    """Retorna metadados de todos os jobs registrados."""
    return [
        {
            "job_id": jid,
            "description": cls().description(),
            "trigger": str(cls().trigger()),
        }
        for jid, cls in _job_registry.items()
    ]
