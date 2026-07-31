from datetime import date, timedelta
from typing import Any

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cliente import ClienteModel
from database.models.conta_pagar import ContaPagarModel
from database.models.conta_receber import ContaReceberModel, ContaStatus
from database.models.fornecedor import FornecedorModel
from infrastructure.automation.base import BaseJob
from infrastructure.automation.registry import register_job


@register_job
class ContasAReceberJob(BaseJob):
    """Alerta para contas a receber próximas do vencimento."""

    DIAS_ANTECEDENCIA = 7

    def job_id(self) -> str:
        return "contas_receber"

    def description(self) -> str:
        return "Alertas de contas a receber vencendo"

    def trigger(self) -> BaseTrigger:
        return CronTrigger(hour=8, minute=15)

    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        hoje = date.today()
        alertas: list[dict[str, Any]] = []

        stmt = (
            select(ContaReceberModel, ClienteModel)
            .join(ClienteModel, ClienteModel.id == ContaReceberModel.cliente_id)
            .where(
                ContaReceberModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]),
                ContaReceberModel.data_vencimento <= hoje + timedelta(days=self.DIAS_ANTECEDENCIA),
            )
            .limit(100)
        )
        result = await session.execute(stmt)
        rows = result.all()

        for conta, cliente in rows:
            dias = (conta.data_vencimento - hoje).days
            if dias <= 0:
                nivel = "critical"
                status_text = f"ATRASADA há {-dias} dia(s)" if dias < 0 else "vence HOJE"
            else:
                nivel = "warning"
                status_text = f"vence em {dias} dia(s)"

            alertas.append({
                "tipo": "conta_receber_vencendo",
                "nivel": nivel,
                "titulo": f"Conta a receber {status_text} — {cliente.nome_razao_social}",
                "mensagem": (
                    f"Conta a receber nº {conta.numero_documento} no valor de "
                    f"R$ {conta.valor_original:.2f} do cliente "
                    f"{cliente.nome_razao_social} {status_text}. "
                    f"Vencimento: {conta.data_vencimento.isoformat()}."
                ),
                "entidade_tipo": "conta_receber",
                "entidade_id": conta.id,
            })

        return alertas


@register_job
class ContasAPagarJob(BaseJob):
    """Alerta para contas a pagar próximas do vencimento."""

    DIAS_ANTECEDENCIA = 7

    def job_id(self) -> str:
        return "contas_pagar"

    def description(self) -> str:
        return "Alertas de contas a pagar vencendo"

    def trigger(self) -> BaseTrigger:
        return CronTrigger(hour=8, minute=30)

    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        hoje = date.today()
        alertas: list[dict[str, Any]] = []

        stmt = (
            select(ContaPagarModel, FornecedorModel)
            .join(FornecedorModel, FornecedorModel.id == ContaPagarModel.fornecedor_id)
            .where(
                ContaPagarModel.status.in_([ContaStatus.ABERTO, ContaStatus.PARCIAL]),
                ContaPagarModel.data_vencimento <= hoje + timedelta(days=self.DIAS_ANTECEDENCIA),
            )
            .limit(100)
        )
        result = await session.execute(stmt)
        rows = result.all()

        for conta, fornecedor in rows:
            dias = (conta.data_vencimento - hoje).days
            if dias <= 0:
                nivel = "critical"
                status_text = f"ATRASADA há {-dias} dia(s)" if dias < 0 else "vence HOJE"
            else:
                nivel = "warning"
                status_text = f"vence em {dias} dia(s)"

            alertas.append({
                "tipo": "conta_pagar_vencendo",
                "nivel": nivel,
                "titulo": f"Conta a pagar {status_text} — {fornecedor.nome_razao_social}",
                "mensagem": (
                    f"Conta a pagar nº {conta.numero_documento} no valor de "
                    f"R$ {conta.valor_original:.2f} do fornecedor "
                    f"{fornecedor.nome_razao_social} {status_text}. "
                    f"Vencimento: {conta.data_vencimento.isoformat()}."
                ),
                "entidade_tipo": "conta_pagar",
                "entidade_id": conta.id,
            })

        return alertas
