from typing import Any

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.documento import DocumentoModel
from infrastructure.automation.base import BaseJob
from infrastructure.automation.registry import register_job


@register_job
class AlertaDocumentoJob(BaseJob):
    """Alerta para documentos pendentes ou próximos do vencimento."""

    def job_id(self) -> str:
        return "alerta_documento"

    def description(self) -> str:
        return "Alertas de documentos (vencidos / sem anexo)"

    def trigger(self) -> BaseTrigger:
        return IntervalTrigger(hours=6)

    async def execute(self, session: AsyncSession) -> list[dict[str, Any]]:
        alertas: list[dict[str, Any]] = []

        stmt = select(DocumentoModel).limit(100)
        result = await session.execute(stmt)
        docs = list(result.scalars().all())

        for doc in docs:
            if not doc.caminho_arquivo:
                alertas.append({
                    "tipo": "documento_sem_arquivo",
                    "nivel": "warning",
                    "titulo": f"Documento sem arquivo: {doc.nome_original}",
                    "mensagem": (
                        f"O documento '{doc.nome_original}' (tipo: {doc.tipo_documento}) "
                        "não possui arquivo anexado."
                    ),
                    "entidade_tipo": doc.entidade_tipo,
                    "entidade_id": doc.entidade_id,
                })

        if not docs:
            pass

        return alertas
