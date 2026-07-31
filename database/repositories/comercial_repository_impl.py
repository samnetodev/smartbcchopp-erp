from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cliente import ClienteModel
from database.models.comercial import MetaModel, MetaStatus
from database.models.pedido import PedidoModel, PedidoStatus
from database.repositories.base_repository import BaseRepository


class MetaRepositoryImpl(BaseRepository[MetaModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MetaModel)

    async def find_by_vendedor(
        self, vendedor_id: UUID, skip: int = 0, limit: int = 100,
    ) -> list[MetaModel]:
        stmt = (
            select(MetaModel)
            .where(MetaModel.vendedor_id == vendedor_id)
            .offset(skip).limit(limit)
            .order_by(MetaModel.periodo_inicio.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_periodo(
        self, inicio: date, fim: date, skip: int = 0, limit: int = 100,
    ) -> list[MetaModel]:
        stmt = (
            select(MetaModel)
            .where(MetaModel.periodo_inicio >= inicio)
            .where(MetaModel.periodo_fim <= fim)
            .offset(skip).limit(limit)
            .order_by(MetaModel.periodo_inicio.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_status(self, status: MetaStatus) -> int:
        stmt = select(func.count()).select_from(MetaModel).where(MetaModel.status == status)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def sum_meta_by_periodo(self, inicio: date, fim: date) -> float:
        stmt = select(func.coalesce(func.sum(MetaModel.valor_meta), 0)).where(
            MetaModel.periodo_inicio >= inicio,
            MetaModel.periodo_fim <= fim,
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one())

    async def sum_realizado_by_periodo(self, inicio: date, fim: date) -> float:
        stmt = select(func.coalesce(func.sum(MetaModel.valor_realizado), 0)).where(
            MetaModel.periodo_inicio >= inicio,
            MetaModel.periodo_fim <= fim,
        )
        result = await self._session.execute(stmt)
        return float(result.scalar_one())


class ComercialRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_clientes_inativos(
        self, meses_sem_compra: int = 3, skip: int = 0, limit: int = 100,
    ) -> list[ClienteModel]:
        data_corte = text(f"NOW() - INTERVAL '{meses_sem_compra} months'")
        subq = (
            select(
                PedidoModel.cliente_id,
                func.max(PedidoModel.data_emissao).label("ultima_compra"),
            )
            .where(PedidoModel.status != PedidoStatus.CANCELADO)
            .group_by(PedidoModel.cliente_id)
            .subquery()
        )
        stmt = (
            select(ClienteModel)
            .outerjoin(subq, ClienteModel.id == subq.c.cliente_id)
            .where(
                ClienteModel.deleted_at.is_(None),
                ClienteModel.status != "inativo",
            )
            .where(
                (subq.c.ultima_compra.is_(None)) | (subq.c.ultima_compra < data_corte),
            )
            .offset(skip).limit(limit)
            .order_by(ClienteModel.nome_razao_social)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_ranking_clientes(
        self, data_inicio: date, data_fim: date, limit: int = 10,
    ) -> list[dict[str, Any]]:
        stmt = (
            select(
                PedidoModel.cliente_id,
                func.sum(PedidoModel.total).label("total_vendas"),
                func.count(PedidoModel.id).label("qtd_pedidos"),
            )
            .where(
                PedidoModel.data_emissao >= data_inicio,
                PedidoModel.data_emissao <= data_fim,
                PedidoModel.status.notin_([PedidoStatus.CANCELADO, PedidoStatus.RASCUNHO]),
            )
            .group_by(PedidoModel.cliente_id)
            .order_by(text("total_vendas DESC"))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        rows = []
        for row in result.all():
            cliente = await self._session.get(ClienteModel, row.cliente_id)
            rows.append({
                "cliente_id": row.cliente_id,
                "cliente_nome": cliente.nome_razao_social if cliente else "",
                "total_vendas": float(row.total_vendas),
                "qtd_pedidos": row.qtd_pedidos,
            })
        return rows

    async def calcular_ticket_medio(self, data_inicio: date, data_fim: date) -> Decimal:
        stmt = select(
            func.coalesce(func.avg(PedidoModel.total), 0)
        ).where(
            PedidoModel.data_emissao >= data_inicio,
            PedidoModel.data_emissao <= data_fim,
            PedidoModel.status.notin_([PedidoStatus.CANCELADO, PedidoStatus.RASCUNHO]),
        )
        result = await self._session.execute(stmt)
        return Decimal(str(result.scalar_one()))

    async def calcular_faturamento(
        self, data_inicio: date, data_fim: date, agrupamento: str = "mes",
    ) -> list[dict[str, Any]]:
        if agrupamento == "dia":
            fmt = func.date_trunc("day", PedidoModel.data_emissao)
        elif agrupamento == "ano":
            fmt = func.date_trunc("year", PedidoModel.data_emissao)
        else:
            fmt = func.date_trunc("month", PedidoModel.data_emissao)
        stmt = (
            select(
                fmt.label("periodo"),
                func.coalesce(func.sum(PedidoModel.total), 0).label("receita"),
                func.count(PedidoModel.id).label("qtd_pedidos"),
            )
            .where(
                PedidoModel.data_emissao >= data_inicio,
                PedidoModel.data_emissao <= data_fim,
                PedidoModel.status.notin_([PedidoStatus.CANCELADO, PedidoStatus.RASCUNHO]),
            )
            .group_by(text("periodo"))
            .order_by(text("periodo"))
        )
        result = await self._session.execute(stmt)
        return [
            {
                "periodo": str(row.periodo),
                "receita": float(row.receita),
                "qtd_pedidos": row.qtd_pedidos,
            }
            for row in result.all()
        ]

    async def calcular_indicadores(self, data_inicio: date, data_fim: date) -> dict[str, Any]:
        total_pedidos = select(func.count()).select_from(PedidoModel).where(
            PedidoModel.data_emissao >= data_inicio,
            PedidoModel.data_emissao <= data_fim,
        )
        total_result = await self._session.execute(total_pedidos)
        total = total_result.scalar_one()

        finalizados = select(func.count()).select_from(PedidoModel).where(
            PedidoModel.data_emissao >= data_inicio,
            PedidoModel.data_emissao <= data_fim,
            PedidoModel.status.in_([PedidoStatus.FATURADO, PedidoStatus.ENTREGUE]),
        )
        finalizados_result = await self._session.execute(finalizados)
        total_finalizados = finalizados_result.scalar_one()

        cancelados = select(func.count()).select_from(PedidoModel).where(
            PedidoModel.data_emissao >= data_inicio,
            PedidoModel.data_emissao <= data_fim,
            PedidoModel.status == PedidoStatus.CANCELADO,
        )
        cancelados_result = await self._session.execute(cancelados)
        total_cancelados = cancelados_result.scalar_one()

        receita = select(func.coalesce(func.sum(PedidoModel.total), 0)).where(
            PedidoModel.data_emissao >= data_inicio,
            PedidoModel.data_emissao <= data_fim,
            PedidoModel.status.notin_([PedidoStatus.CANCELADO, PedidoStatus.RASCUNHO]),
        )
        receita_result = await self._session.execute(receita)
        total_receita = float(receita_result.scalar_one())

        ticket = await self.calcular_ticket_medio(data_inicio, data_fim)

        conversao = (total_finalizados / total * 100) if total > 0 else 0
        taxa_cancelamento = (total_cancelados / total * 100) if total > 0 else 0

        return {
            "total_pedidos": total,
            "pedidos_finalizados": total_finalizados,
            "pedidos_cancelados": total_cancelados,
            "taxa_conversao": round(conversao, 2),
            "taxa_cancelamento": round(taxa_cancelamento, 2),
            "receita_total": total_receita,
            "ticket_medio": float(ticket),
        }

    async def dashboard(
        self, data_inicio: date, data_fim: date,
    ) -> dict[str, Any]:
        indicadores = await self.calcular_indicadores(data_inicio, data_fim)
        faturamento = await self.calcular_faturamento(data_inicio, data_fim)
        ranking = await self.find_ranking_clientes(data_inicio, data_fim, limit=5)
        ticket = await self.calcular_ticket_medio(data_inicio, data_fim)

        clientes_ativos = select(func.count()).select_from(ClienteModel).where(
            ClienteModel.deleted_at.is_(None),
            ClienteModel.status == "ativo",
        )
        ca_result = await self._session.execute(clientes_ativos)
        total_clientes_ativos = ca_result.scalar_one()

        return {
            "indicadores": indicadores,
            "faturamento_periodo": faturamento,
            "ranking_clientes": ranking,
            "ticket_medio": float(ticket),
            "total_clientes_ativos": total_clientes_ativos,
        }
