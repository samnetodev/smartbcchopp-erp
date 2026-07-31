from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from database.models.comercial import MetaModel, MetaStatus

NOW = datetime.now(timezone.utc)
TODAY = date.today()


def _finalize(instance):
    if not instance.id:
        instance.id = uuid4()
    if not instance.created_at:
        instance.created_at = NOW
    if not instance.updated_at:
        instance.updated_at = NOW
    if hasattr(instance, "status") and instance.status is None:
        instance.status = MetaStatus.ABERTA
    for attr in ("valor_meta", "valor_realizado", "comissao_percentual"):
        if hasattr(instance, attr) and getattr(instance, attr) is None:
            setattr(instance, attr, 0.0)
    return instance


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def sample_meta() -> MetaModel:
    m = MetaModel(
        descricao="Meta Q1 2026",
        periodo_inicio=date(2026, 1, 1),
        periodo_fim=date(2026, 3, 31),
        valor_meta=100000.0,
        status=MetaStatus.ABERTA,
    )
    _finalize(m)
    return m


class TestDashboard:
    async def test_dashboard_returns_all_data(self, mock_session):
        with (
            patch("api.routes.v1.commercial_routes.ComercialRepositoryImpl") as mock_repo_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.dashboard = AsyncMock(return_value={
                "indicadores": {
                    "total_pedidos": 50,
                    "pedidos_finalizados": 40,
                    "pedidos_cancelados": 3,
                    "taxa_conversao": 80.0,
                    "taxa_cancelamento": 6.0,
                    "receita_total": 150000.0,
                    "ticket_medio": 3000.0,
                },
                "faturamento_periodo": [
                    {"periodo": "2026-01-01", "receita": 50000.0, "qtd_pedidos": 20},
                ],
                "ranking_clientes": [
                    {"cliente_id": str(uuid4()), "cliente_nome": "Cliente A",
                     "total_vendas": 30000.0, "qtd_pedidos": 5},
                ],
                "ticket_medio": 3000.0,
                "total_clientes_ativos": 100,
            })

            from api.routes.v1.commercial_routes import commercial_dashboard
            data = await commercial_dashboard(
                data_inicio=date(2026, 1, 1), data_fim=date(2026, 3, 31),
                session=mock_session, _={},
            )

            assert data.ticket_medio == 3000.0
            assert data.total_clientes_ativos == 100
            assert data.indicadores.total_pedidos == 50
            assert len(data.faturamento_periodo) == 1
            assert len(data.ranking_clientes) == 1


class TestClientesInativos:
    async def test_list_clientes_inativos(self, mock_session):
        with (
            patch("api.routes.v1.commercial_routes.ComercialRepositoryImpl") as mock_repo_cls,
        ):
            from unittest.mock import MagicMock
            mock_cliente = MagicMock(spec=[])
            mock_cliente.id = uuid4()
            mock_cliente.nome_razao_social = "Cliente Inativo"
            mock_cliente.nome_fantasia = None
            mock_cliente.cpf_cnpj = "00000000000"
            mock_cliente.email = None
            mock_cliente.celular = None
            mock_cliente.status = "ativo"
            mock_cliente.ultima_compra = None

            mock_repo = mock_repo_cls.return_value
            mock_repo.find_clientes_inativos = AsyncMock(return_value=[mock_cliente])

            from api.routes.v1.commercial_routes import list_clientes_inativos
            result = await list_clientes_inativos(
                meses_sem_compra=3, session=mock_session, _={},
            )

            assert len(result) == 1
            assert result[0].nome_razao_social == "Cliente Inativo"


class TestRanking:
    async def test_ranking_returns_sorted(self, mock_session):
        with (
            patch("api.routes.v1.commercial_routes.ComercialRepositoryImpl") as mock_repo_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_ranking_clientes = AsyncMock(return_value=[
                {"cliente_id": str(uuid4()), "cliente_nome": "Top 1",
                 "total_vendas": 50000.0, "qtd_pedidos": 10},
                {"cliente_id": str(uuid4()), "cliente_nome": "Top 2",
                 "total_vendas": 30000.0, "qtd_pedidos": 7},
            ])

            from api.routes.v1.commercial_routes import ranking_clientes
            result = await ranking_clientes(
                data_inicio=date(2026, 1, 1), data_fim=date(2026, 3, 31),
                limit=10, session=mock_session, _={},
            )

            assert len(result) == 2
            assert result[0].total_vendas == 50000.0


class TestTicketMedio:
    async def test_ticket_medio_returns_value(self, mock_session):
        with (
            patch("api.routes.v1.commercial_routes.ComercialRepositoryImpl") as mock_repo_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.calcular_ticket_medio = AsyncMock(return_value=2500.0)

            from api.routes.v1.commercial_routes import ticket_medio
            result = await ticket_medio(
                data_inicio=date(2026, 1, 1), data_fim=date(2026, 3, 31),
                session=mock_session, _={},
            )

            assert result["ticket_medio"] == 2500.0


class TestFaturamento:
    async def test_faturamento_returns_periodos(self, mock_session):
        with (
            patch("api.routes.v1.commercial_routes.ComercialRepositoryImpl") as mock_repo_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.calcular_faturamento = AsyncMock(return_value=[
                {"periodo": "2026-01-01", "receita": 50000.0, "qtd_pedidos": 20},
                {"periodo": "2026-02-01", "receita": 60000.0, "qtd_pedidos": 25},
            ])

            from api.routes.v1.commercial_routes import faturamento
            result = await faturamento(
                data_inicio=date(2026, 1, 1), data_fim=date(2026, 3, 31),
                agrupamento="mes", session=mock_session, _={},
            )

            assert len(result) == 2
            assert result[0].receita == 50000.0


class TestIndicadores:
    async def test_indicadores_returns_all_kpis(self, mock_session):
        with (
            patch("api.routes.v1.commercial_routes.ComercialRepositoryImpl") as mock_repo_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.calcular_indicadores = AsyncMock(return_value={
                "total_pedidos": 100,
                "pedidos_finalizados": 80,
                "pedidos_cancelados": 5,
                "taxa_conversao": 80.0,
                "taxa_cancelamento": 5.0,
                "receita_total": 250000.0,
                "ticket_medio": 2500.0,
            })

            from api.routes.v1.commercial_routes import indicadores
            result = await indicadores(
                data_inicio=date(2026, 1, 1), data_fim=date(2026, 3, 31),
                session=mock_session, _={},
            )

            assert result.total_pedidos == 100
            assert result.taxa_conversao == 80.0
            assert result.receita_total == 250000.0


class TestRelatorios:
    async def test_relatorio_vendas(self, mock_session):
        with (
            patch("api.routes.v1.commercial_routes.ComercialRepositoryImpl") as mock_repo_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.calcular_indicadores = AsyncMock(return_value={
                "total_pedidos": 50, "pedidos_finalizados": 40,
                "pedidos_cancelados": 3, "taxa_conversao": 80.0,
                "taxa_cancelamento": 6.0, "receita_total": 150000.0,
                "ticket_medio": 3000.0,
            })
            mock_repo.calcular_faturamento = AsyncMock(return_value=[
                {"periodo": "2026-01-01", "receita": 50000.0, "qtd_pedidos": 20},
            ])
            mock_repo.find_ranking_clientes = AsyncMock(return_value=[
                {"cliente_id": str(uuid4()), "cliente_nome": "Top 1",
                 "total_vendas": 30000.0, "qtd_pedidos": 5},
            ])

            from api.routes.v1.commercial_routes import relatorio_vendas
            result = await relatorio_vendas(
                data_inicio=date(2026, 1, 1), data_fim=date(2026, 3, 31),
                session=mock_session, _={},
            )

            assert result["periodo"]["inicio"] == "2026-01-01"
            assert result["indicadores"]["total_pedidos"] == 50
            assert len(result["faturamento"]) == 1
            assert len(result["ranking_clientes"]) == 1

    async def test_relatorio_clientes(self, mock_session):
        with (
            patch("api.routes.v1.commercial_routes.ComercialRepositoryImpl") as mock_repo_cls,
        ):
            from unittest.mock import MagicMock
            mock_cliente = MagicMock(spec=[])
            mock_cliente.id = uuid4()
            mock_cliente.nome_razao_social = "Inativo"
            mock_cliente.nome_fantasia = None
            mock_cliente.cpf_cnpj = "00000000000"
            mock_cliente.email = None
            mock_cliente.celular = None
            mock_cliente.status = "ativo"
            mock_cliente.ultima_compra = None

            mock_repo = mock_repo_cls.return_value
            mock_repo.find_clientes_inativos = AsyncMock(return_value=[mock_cliente])

            from api.routes.v1.commercial_routes import relatorio_clientes
            result = await relatorio_clientes(session=mock_session, _={})

            assert result["total_clientes_inativos"] == 1
            assert result["clientes_inativos"][0].nome_razao_social == "Inativo"


class TestMetasCrud:
    async def test_create_meta(self, mock_session, sample_meta):
        with (
            patch("api.routes.v1.commercial_routes.MetaRepositoryImpl") as mock_repo_cls,
            patch("api.routes.v1.commercial_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.save = AsyncMock(side_effect=lambda i: _finalize(i))
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.commercial_routes import create_meta
            from api.serializers.commercial_schema import MetaCreate
            body = MetaCreate(
                descricao="Meta Q1 2026",
                periodo_inicio=date(2026, 1, 1),
                periodo_fim=date(2026, 3, 31),
                valor_meta=100000,
            )
            result = await create_meta(body=body, session=mock_session, _={})

            assert result.descricao == "Meta Q1 2026"
            assert float(result.valor_meta) == 100000
            assert mock_repo.save.called

    async def test_get_meta_404(self, mock_session):
        with (
            patch("api.routes.v1.commercial_routes.MetaRepositoryImpl") as mock_repo_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=None)

            from fastapi import HTTPException

            from api.routes.v1.commercial_routes import get_meta

            with pytest.raises(HTTPException) as exc:
                await get_meta(meta_id=uuid4(), session=mock_session, _={})
            assert exc.value.status_code == 404

    async def test_list_metas(self, mock_session, sample_meta):
        with (
            patch("api.routes.v1.commercial_routes.MetaRepositoryImpl") as mock_repo_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_all = AsyncMock(return_value=[sample_meta])
            mock_repo.count = AsyncMock(return_value=1)

            from api.routes.v1.commercial_routes import list_metas
            result = await list_metas(skip=0, limit=100, session=mock_session, _={})

            assert result.total == 1
            assert len(result.items) == 1
            assert result.items[0].descricao == "Meta Q1 2026"

    async def test_update_meta(self, mock_session, sample_meta):
        with (
            patch("api.routes.v1.commercial_routes.MetaRepositoryImpl") as mock_repo_cls,
            patch("api.routes.v1.commercial_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=sample_meta)
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.commercial_routes import update_meta
            from api.serializers.commercial_schema import MetaUpdate
            body = MetaUpdate(valor_meta=120000, status="atingida")
            result = await update_meta(
                meta_id=sample_meta.id, body=body,
                session=mock_session, _={},
            )

            assert float(result.valor_meta) == 120000
            assert result.status == "atingida"

    async def test_delete_meta(self, mock_session, sample_meta):
        with (
            patch("api.routes.v1.commercial_routes.MetaRepositoryImpl") as mock_repo_cls,
            patch("api.routes.v1.commercial_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.delete = AsyncMock(return_value=True)
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.commercial_routes import delete_meta
            result = await delete_meta(
                meta_id=sample_meta.id, session=mock_session, _={},
            )

            assert result is None
            assert mock_repo.delete.called

    async def test_delete_meta_404(self, mock_session):
        with (
            patch("api.routes.v1.commercial_routes.MetaRepositoryImpl") as mock_repo_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.delete = AsyncMock(return_value=False)

            from fastapi import HTTPException

            from api.routes.v1.commercial_routes import delete_meta

            with pytest.raises(HTTPException) as exc:
                await delete_meta(meta_id=uuid4(), session=mock_session, _={})
            assert exc.value.status_code == 404
