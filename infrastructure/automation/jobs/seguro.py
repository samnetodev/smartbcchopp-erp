from datetime import date, timedelta
from typing import Any

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.veiculo import VeiculoModel, VeiculoStatus
from database.models.veiculo_seguro import SeguroModel, SeguroStatus
from infrastructure.automation.base import BaseJob
from infrastructure.automation.registry import register_job


@register_job
class SeguroJob(BaseJob):
    """Alerta para vencimento de seguro de veículos."""

    DIAS_ANTECEDENCIA = 30

    def job_id(self) -> str:
        return "seguro"

    def description(self) -> str:
        return "Alertas de vencimento de seguro"

    def trigger(self) -> BaseTrigger:
        return CronTrigger(hour=7, minute=30)

    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        hoje = date.today()
        limite = hoje + timedelta(days=self.DIAS_ANTECEDENCIA)
        alertas: list[dict[str, Any]] = []

        stmt = (
            select(SeguroModel, VeiculoModel)
            .join(VeiculoModel, VeiculoModel.id == SeguroModel.veiculo_id)
            .where(SeguroModel.status == SeguroStatus.ATIVO)
            .where(SeguroModel.data_fim_vigencia <= limite)
        )
        result = await session.execute(stmt)
        rows = result.all()

        for seguro, veiculo in rows:
            dias = (seguro.data_fim_vigencia - hoje).days
            if dias <= 0:
                nivel = "critical"
                status_text = "VENCIDO"
            elif dias <= 7:
                nivel = "critical"
                status_text = f"vence em {dias} dia(s)"
            else:
                nivel = "warning"
                status_text = f"vence em {dias} dia(s)"

            alertas.append({
                "tipo": "seguro_vencendo",
                "nivel": nivel,
                "titulo": f"Seguro {status_text} — {veiculo.placa}",
                "mensagem": (
                    f"Seguro apólice {seguro.apolice} do veículo {veiculo.placa} "
                    f"({veiculo.marca} {veiculo.modelo}) {status_text}. "
                    f"Seguradora: {seguro.seguradora.value}. "
                    f"Vigência até: {seguro.data_fim_vigencia.isoformat()}."
                ),
                "entidade_tipo": "veiculo_seguro",
                "entidade_id": seguro.id,
            })

        stmt_sem_seguro = select(VeiculoModel).where(
            VeiculoModel.status.in_([VeiculoStatus.DISPONIVEL, VeiculoStatus.EM_ROTA]),
            VeiculoModel.ativo.is_(True),
        )
        result_sem = await session.execute(stmt_sem_seguro)
        veiculos_ativos = list(result_sem.scalars().all())

        for v in veiculos_ativos:
            stmt_tem_seguro = (
                select(SeguroModel)
                .where(SeguroModel.veiculo_id == v.id)
                .where(SeguroModel.status == SeguroStatus.ATIVO)
                .limit(1)
            )
            result_tem = await session.execute(stmt_tem_seguro)
            if not result_tem.scalar_one_or_none():
                alertas.append({
                    "tipo": "seguro_ausente",
                    "nivel": "critical",
                    "titulo": f"Sem seguro ativo — {v.placa}",
                    "mensagem": (
                        f"O veículo {v.placa} ({v.marca} {v.modelo}) "
                        "não possui seguro ativo cadastrado."
                    ),
                    "entidade_tipo": "veiculo",
                    "entidade_id": v.id,
                })

        return alertas
