from typing import Any

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.deposito import DepositoModel
from database.models.estoque import EstoqueModel
from database.models.produto import ProdutoModel
from infrastructure.automation.base import BaseJob
from infrastructure.automation.registry import register_job


@register_job
class EstoqueBaixoJob(BaseJob):
    """Alerta para produtos com estoque baixo (abaixo do mínimo)."""

    def job_id(self) -> str:
        return "estoque_baixo"

    def description(self) -> str:
        return "Alertas de estoque baixo"

    def trigger(self) -> BaseTrigger:
        return CronTrigger(hour=6, minute=0)

    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        alertas: list[dict[str, Any]] = []

        stmt = (
            select(ProdutoModel, EstoqueModel, DepositoModel)
            .join(EstoqueModel, EstoqueModel.produto_id == ProdutoModel.id)
            .join(DepositoModel, DepositoModel.id == EstoqueModel.deposito_id)
            .where(ProdutoModel.ativo.is_(True))
            .where(EstoqueModel.quantidade_atual <= ProdutoModel.estoque_minimo)
            .limit(100)
        )
        result = await session.execute(stmt)
        rows = result.all()

        for produto, estoque, deposito in rows:
            if produto.estoque_minimo <= 0:
                continue

            if estoque.quantidade_atual <= 0:
                nivel = "critical"
                status = "ESGOTADO"
            elif estoque.quantidade_atual <= produto.estoque_minimo * 0.5:
                nivel = "critical"
                status = "CRÍTICO"
            else:
                nivel = "warning"
                status = "BAIXO"

            alertas.append({
                "tipo": "estoque_baixo",
                "nivel": nivel,
                "titulo": f"Estoque {status} — {produto.nome}",
                "mensagem": (
                    f"Produto {produto.codigo} — {produto.nome} no depósito "
                    f"{deposito.nome}: saldo atual de "
                    f"{float(estoque.quantidade_atual):.3f} "
                    f"(mínimo: {float(produto.estoque_minimo):.3f})."
                ),
                "entidade_tipo": "estoque",
                "entidade_id": estoque.id,
            })

        return alertas
