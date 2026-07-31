from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.automation.registry import get_all_jobs

logger = logging.getLogger(__name__)


class SchedulerService:
    """Wrapper do AsyncIOScheduler que gerencia jobs de automação.

    Cada job recebe uma session factory e roda sua lógica de negócio
    dentro de uma transação isolada.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._scheduler = AsyncIOScheduler()
        self._session_factory = session_factory
        self._started = False

    async def start(self) -> None:
        """Registra todos os jobs e inicia o scheduler."""
        if self._started:
            logger.warning("Scheduler já iniciado")
            return

        jobs = get_all_jobs()
        if not jobs:
            logger.warning("Nenhum job de automação registrado")
            return

        for jid, job_cls in jobs.items():
            job = job_cls()
            self._scheduler.add_job(
                self._run_job,
                trigger=job.trigger(),
                id=jid,
                name=job.description(),
                args=[jid],
                replace_existing=True,
                misfire_grace_time=300,
            )
            logger.info("Job agendado: %s (%s)", jid, job.description())

        self._scheduler.start()
        self._started = True
        logger.info("Scheduler de automação iniciado com %d job(s)", len(jobs))

    async def stop(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
        self._started = False
        logger.info("Scheduler de automação parado")

    async def _run_job(self, job_id: str) -> None:
        """Executa um job dentro de uma sessão isolada."""
        jobs = get_all_jobs()
        job_cls = jobs.get(job_id)
        if not job_cls:
            logger.error("Job '%s' não encontrado no registry", job_id)
            return

        job = job_cls()
        async with self._session_factory() as session:
            try:
                await job.pre_execute(session)
                from database.models.alerta import AlertaModel

                alertas = await job.execute(session)
                for item in alertas:
                    alerta = AlertaModel(
                        tipo=item["tipo"],
                        titulo=item["titulo"],
                        mensagem=item.get("mensagem"),
                        nivel=item.get("nivel", "warning"),
                        entidade_tipo=item.get("entidade_tipo"),
                        entidade_id=item.get("entidade_id"),
                    )
                    session.add(alerta)

                await session.commit()
                await job.post_execute(session, alertas)
            except Exception:
                await session.rollback()
                logger.exception(
                    "Erro na execução do job '%s' (%s)", job_id, job.description()
                )

    @property
    def running(self) -> bool:
        return self._started
