from datetime import date, timedelta
from typing import Any

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.boleto import BoletoModel, BoletoStatus
from database.models.cliente import ClienteModel
from database.models.conta_receber import ContaReceberModel
from infrastructure.automation.base import BaseJob
from infrastructure.automation.registry import register_job


@register_job
class BoletoJob(BaseJob):
    """Alerta para boletos vencendo ou vencidos."""

    DIAS_ANTECEDENCIA = 5

    def job_id(self) -> str:
        return "boleto"

    def description(self) -> str:
        return "Alertas de boletos a vencer / vencidos"

    def trigger(self) -> BaseTrigger:
        return CronTrigger(hour=8, minute=0)

    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        hoje = date.today()
        alertas: list[dict[str, Any]] = []

        stmt = (
            select(BoletoModel, ContaReceberModel, ClienteModel)
            .join(ContaReceberModel, ContaReceberModel.id == BoletoModel.conta_receber_id)
            .join(ClienteModel, ClienteModel.id == ContaReceberModel.cliente_id)
            .where(
                BoletoModel.status.in_([
                    BoletoStatus.GERADO,
                    BoletoStatus.REGISTRADO,
                    BoletoStatus.VENCIDO,
                ])
            )
            .where(BoletoModel.data_vencimento <= hoje + timedelta(days=self.DIAS_ANTECEDENCIA))
            .limit(100)
        )
        result = await session.execute(stmt)
        rows = result.all()

        for boleto, conta, cliente in rows:
            dias = (boleto.data_vencimento - hoje).days
            if dias <= 0:
                nivel = "critical" if dias <= -5 else "warning"
                status_text = f"VENCIDO há {-dias} dia(s)" if dias < 0 else "vence HOJE"
            else:
                nivel = "warning"
                status_text = f"vence em {dias} dia(s)"

            alertas.append({
                "tipo": "boleto_vencendo",
                "nivel": nivel,
                "titulo": f"Boleto {status_text} — {cliente.nome_razao_social}",
                "mensagem": (
                    f"Boleto {boleto.nosso_numero} no valor de "
                    f"R$ {boleto.valor_nominal:.2f} do cliente "
                    f"{cliente.nome_razao_social} {status_text}. "
                    f"Vencimento: {boleto.data_vencimento.isoformat()}."
                ),
                "entidade_tipo": "boleto",
                "entidade_id": boleto.id,
            })

        return alertas
