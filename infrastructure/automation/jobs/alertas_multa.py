from datetime import date
from typing import Any

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.multa import MultaModel, MultaStatus
from database.models.veiculo import VeiculoModel
from infrastructure.automation.base import BaseJob
from infrastructure.automation.registry import register_job


@register_job
class AlertaMultaJob(BaseJob):
    """Alerta para multas pendentes ou próximas do vencimento."""

    def job_id(self) -> str:
        return "alerta_multa"

    def description(self) -> str:
        return "Alertas de multas de trânsito pendentes"

    def trigger(self) -> BaseTrigger:
        return CronTrigger(hour=8, minute=0)

    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        hoje = date.today()
        alertas: list[dict[str, Any]] = []

        stmt = (
            select(MultaModel, VeiculoModel)
            .join(VeiculoModel, VeiculoModel.id == MultaModel.veiculo_id)
            .where(MultaModel.status.in_([MultaStatus.PENDENTE, MultaStatus.RECORRENDO]))
        )
        result = await session.execute(stmt)
        rows = result.all()

        for multa, veiculo in rows:
            if multa.data_vencimento:
                dias = (multa.data_vencimento - hoje).days
                if dias <= 3:
                    nivel = "critical" if dias <= 0 else "warning"
                    status_texto = "VENCIDA" if dias <= 0 else f"vence em {dias} dia(s)"
                    alertas.append({
                        "tipo": "multa_vencendo",
                        "nivel": nivel,
                        "titulo": f"Multa {status_texto} — {veiculo.placa}",
                        "mensagem": (
                            f"Multa de R$ {multa.valor_original:.2f} para o veículo "
                            f"{veiculo.placa} ({veiculo.marca} {veiculo.modelo}). "
                            f"Órgão: {multa.orgao_autuador}. "
                            f"Vencimento: {multa.data_vencimento.isoformat()}."
                        ),
                        "entidade_tipo": "multa",
                        "entidade_id": multa.id,
                    })
            else:
                if (hoje - multa.data_infracao).days >= 30:
                    alertas.append({
                        "tipo": "multa_sem_vencimento",
                        "nivel": "info",
                        "titulo": f"Multa sem data de vencimento — {veiculo.placa}",
                        "mensagem": (
                            f"Multa de R$ {multa.valor_original:.2f} para o veículo "
                            f"{veiculo.placa}. Data da infração: {multa.data_infracao}. "
                            "Não possui data de vencimento cadastrada."
                        ),
                        "entidade_tipo": "multa",
                        "entidade_id": multa.id,
                    })

        return alertas
