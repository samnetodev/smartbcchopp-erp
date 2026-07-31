from datetime import date
from typing import Any

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cliente import ClienteModel
from database.models.pedido import PedidoModel
from infrastructure.automation.base import BaseJob
from infrastructure.automation.registry import register_job


@register_job
class ClienteInativoJob(BaseJob):
    """Alerta para clientes sem compras há mais de X dias."""

    DIAS_SEM_COMPRA = 90
    DIAS_ALERTA_PREVIO = 60

    def job_id(self) -> str:
        return "cliente_inativo"

    def description(self) -> str:
        return "Alertas de clientes sem compras recentes"

    def trigger(self) -> BaseTrigger:
        return CronTrigger(hour=9, minute=0)

    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        hoje = date.today()
        alertas: list[dict[str, Any]] = []

        stmt = (
            select(
                ClienteModel.id,
                ClienteModel.nome_razao_social,
                ClienteModel.cpf_cnpj,
                func.max(PedidoModel.data_emissao).label("ultima_compra"),
            )
            .outerjoin(PedidoModel, PedidoModel.cliente_id == ClienteModel.id)
            .where(ClienteModel.deleted_at.is_(None))
            .where(ClienteModel.status.in_(["ativo"]))
            .group_by(ClienteModel.id, ClienteModel.nome_razao_social, ClienteModel.cpf_cnpj)
        )
        result = await session.execute(stmt)
        rows = result.all()

        for row in rows:
            ultima = row.ultima_compra
            if ultima is None:
                alertas.append({
                    "tipo": "cliente_sem_compra",
                    "nivel": "info",
                    "titulo": f"Cliente sem histórico: {row.nome_razao_social}",
                    "mensagem": (
                        f"O cliente {row.nome_razao_social} ({row.cpf_cnpj}) "
                        "nunca realizou nenhuma compra."
                    ),
                    "entidade_tipo": "cliente",
                    "entidade_id": row.id,
                })
            else:
                dias_sem_compra = (hoje - ultima).days
                if dias_sem_compra >= self.DIAS_ALERTA_PREVIO:
                    nivel = "critical" if dias_sem_compra >= self.DIAS_SEM_COMPRA else "warning"
                    alertas.append({
                        "tipo": "cliente_inativo",
                        "nivel": nivel,
                        "titulo": f"Cliente inativo — {row.nome_razao_social}",
                        "mensagem": (
                            f"{row.nome_razao_social} ({row.cpf_cnpj}) está há "
                            f"{dias_sem_compra} dias sem comprar. "
                            f"Última compra: {ultima.isoformat()}."
                        ),
                        "entidade_tipo": "cliente",
                        "entidade_id": row.id,
                    })

        return alertas
