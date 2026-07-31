from datetime import date
from typing import Any

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.chopeira import ChopeiraModel, ChopeiraStatus
from infrastructure.automation.base import BaseJob
from infrastructure.automation.registry import register_job


@register_job
class ChopeiraParadaJob(BaseJob):
    """Alerta para chopeiras em manutenção prolongada ou sem manutenção recente."""

    DIAS_SEM_MANUTENCAO = 180
    DIAS_MANUTENCAO_PROLONGADA = 15

    def job_id(self) -> str:
        return "chopeira_parada"

    def description(self) -> str:
        return "Alertas de chopeiras paradas / sem manutenção"

    def trigger(self) -> BaseTrigger:
        return CronTrigger(hour=8, minute=30)

    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        hoje = date.today()
        alertas: list[dict[str, Any]] = []

        stmt = select(ChopeiraModel)
        result = await session.execute(stmt)
        chopeiras = list(result.scalars().all())

        for c in chopeiras:
            if c.status == ChopeiraStatus.MANUTENCAO:
                from database.models.chopeira_manutencao import (
                    ChopeiraManutencaoModel,
                    ManutencaoStatus,
                )

                stmt_manut = (
                    select(ChopeiraManutencaoModel)
                    .where(ChopeiraManutencaoModel.chopeira_id == c.id)
                    .where(ChopeiraManutencaoModel.status.in_(
                        [ManutencaoStatus.AGENDADA, ManutencaoStatus.ANDAMENTO]
                    ))
                    .order_by(ChopeiraManutencaoModel.data_inicio.desc())
                    .limit(1)
                )
                result_manut = await session.execute(stmt_manut)
                manut = result_manut.scalar_one_or_none()

                if manut and manut.data_inicio:
                    dias_manut = (hoje - manut.data_inicio).days
                    if dias_manut >= self.DIAS_MANUTENCAO_PROLONGADA:
                        alertas.append({
                            "tipo": "chopeira_manutencao_prolongada",
                            "nivel": "warning",
                            "titulo": f"Manutenção prolongada — {c.codigo_identificacao}",
                            "mensagem": (
                                f"Chopeira {c.codigo_identificacao} ({c.marca} {c.modelo}) "
                                f"está em manutenção há {dias_manut} dias "
                                f"(início: {manut.data_inicio.isoformat()}). "
                                f"Local: {c.local_instalacao or 'N/I'}."
                            ),
                            "entidade_tipo": "chopeira",
                            "entidade_id": c.id,
                        })

            if c.data_proxima_manutencao and c.status != ChopeiraStatus.BAIXADA:
                dias = (c.data_proxima_manutencao - hoje).days
                if dias <= 0:
                    alertas.append({
                        "tipo": "chopeira_manutencao_atrasada",
                        "nivel": "critical",
                        "titulo": f"Manutenção atrasada — {c.codigo_identificacao}",
                        "mensagem": (
                            f"Chopeira {c.codigo_identificacao} está com "
                            f"manutenção preventiva atrasada em {-dias} dia(s). "
                            f"Prevista para: {c.data_proxima_manutencao.isoformat()}."
                        ),
                        "entidade_tipo": "chopeira",
                        "entidade_id": c.id,
                    })
                elif dias <= 15:
                    alertas.append({
                        "tipo": "chopeira_manutencao_proxima",
                        "nivel": "warning",
                        "titulo": f"Manutenção próxima — {c.codigo_identificacao}",
                        "mensagem": (
                            f"Chopeira {c.codigo_identificacao} tem manutenção "
                            f"prevista para {c.data_proxima_manutencao.isoformat()} "
                            f"(em {dias} dia(s))."
                        ),
                        "entidade_tipo": "chopeira",
                        "entidade_id": c.id,
                    })

        return alertas
