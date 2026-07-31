from typing import Any

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.veiculo import VeiculoModel, VeiculoStatus
from infrastructure.automation.base import BaseJob
from infrastructure.automation.registry import register_job


@register_job
class TrocaOleoJob(BaseJob):
    """Alerta para troca de óleo programada (km ou data)."""

    KM_ALERTA_ANTES = 500
    DIAS_ALERTA_ANTES = 7

    def job_id(self) -> str:
        return "troca_oleo"

    def description(self) -> str:
        return "Alertas de troca de óleo programada"

    def trigger(self) -> BaseTrigger:
        return CronTrigger(hour=7, minute=0)

    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        alertas: list[dict[str, Any]] = []

        stmt = select(VeiculoModel).where(
            VeiculoModel.status.in_([VeiculoStatus.DISPONIVEL, VeiculoStatus.EM_ROTA]),
            VeiculoModel.ativo.is_(True),
        )
        result = await session.execute(stmt)
        veiculos = list(result.scalars().all())

        for v in veiculos:
            motivos: list[str] = []

            if v.km_proxima_troca_oleo is not None:
                km_restante = v.km_proxima_troca_oleo - v.km_atual
                if km_restante <= 0:
                    motivos.append(f"KM excedido em {-km_restante} km")
                elif km_restante <= self.KM_ALERTA_ANTES:
                    motivos.append(f"KM próxima (falta {km_restante} km)")

            from database.models.veiculo_troca_oleo import TrocaOleoModel

            stmt_ultima = (
                select(TrocaOleoModel)
                .where(TrocaOleoModel.veiculo_id == v.id)
                .order_by(TrocaOleoModel.data.desc())
                .limit(1)
            )
            result_ultima = await session.execute(stmt_ultima)
            ultima = result_ultima.scalar_one_or_none()

            if ultima and ultima.km_proxima_troca:
                km_restante = ultima.km_proxima_troca - v.km_atual
                if km_restante <= 0:
                    motivos.append(f"KM excedido (última troca: {ultima.km_proxima_troca} km)")
                elif km_restante <= self.KM_ALERTA_ANTES:
                    motivos.append(f"KM próxima da última troca (falta {km_restante} km)")

            if motivos:
                alertas.append({
                    "tipo": "troca_oleo",
                    "nivel": "warning",
                    "titulo": f"Troca de óleo necessária — {v.placa}",
                    "mensagem": (
                        f"Veículo {v.placa} ({v.marca} {v.modelo}) requer troca de óleo. "
                        f"KM atual: {v.km_atual}. Motivos: {'; '.join(motivos)}."
                    ),
                    "entidade_tipo": "veiculo",
                    "entidade_id": v.id,
                })

        return alertas
