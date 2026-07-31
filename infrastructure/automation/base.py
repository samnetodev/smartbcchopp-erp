from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from apscheduler.triggers.base import BaseTrigger
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseJob(ABC):
    """Classe base para todos os jobs de automação."""

    @abstractmethod
    def job_id(self) -> str:
        """Identificador único do job (ex: 'alerta_documento')."""

    @abstractmethod
    def description(self) -> str:
        """Descrição legível do job."""

    @abstractmethod
    def trigger(self) -> BaseTrigger:
        """Triggers do APScheduler (IntervalTrigger, CronTrigger, etc.)."""

    @abstractmethod
    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        """Executa a verificação e cria alertas.

        Retorna lista de dicionários com os alertas criados:
        ``[{"tipo": ..., "titulo": ..., "mensagem": ..., "nivel": ...}, ...]``
        """

    async def pre_execute(self, session: AsyncSession) -> None:
        """Hook executado antes de cada execução (logging, etc.)."""
        logger.info("[AUTOMATION] Executando job '%s' (%s)", self.job_id(), self.description())

    async def post_execute(self, session: AsyncSession, alertas: list[dict[str, Any]]) -> None:
        """Hook pós-execução."""
        if alertas:
            logger.info(
                "[AUTOMATION] Job '%s' criou %d alerta(s)", self.job_id(), len(alertas)
            )
        else:
            logger.debug("[AUTOMATION] Job '%s' — nenhum alerta gerado", self.job_id())
