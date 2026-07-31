from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from api.serializers.financial_schema import (
    BoletoGerarInput,
    ContaPagarCreate,
    ContaReceberCreate,
    LancamentoCreate,
    PagarBaixaInput,
    PixGerarInput,
    ReceberBaixaInput,
)
from database.models.conta_pagar import ContaPagarModel
from database.models.conta_receber import ContaReceberModel, ContaStatus

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
        instance.status = ContaStatus.ABERTO
    for attr in ("valor_pago", "desconto", "juros", "multa"):
        if hasattr(instance, attr) and getattr(instance, attr) is None:
            setattr(instance, attr, 0.0)
    return instance


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def sample_conta_receber() -> ContaReceberModel:
    c = ContaReceberModel(
        cliente_id=uuid4(),
        numero_documento="NF-001",
        data_emissao=TODAY,
        data_vencimento=TODAY,
        valor_original=5000.0,
        status=ContaStatus.ABERTO,
    )
    _finalize(c)
    return c


@pytest.fixture
def sample_conta_pagar() -> ContaPagarModel:
    c = ContaPagarModel(
        fornecedor_id=uuid4(),
        numero_documento="NF-Compra-001",
        data_emissao=TODAY,
        data_vencimento=TODAY,
        valor_original=3000.0,
        status=ContaStatus.ABERTO,
    )
    _finalize(c)
    return c


class TestDashboard:
    async def test_dashboard_returns_summary(self, mock_session):
        with (
            patch("api.routes.v1.financial_routes.ContaReceberRepositoryImpl") as mock_rec_cls,
            patch("api.routes.v1.financial_routes.ContaPagarRepositoryImpl") as mock_pag_cls,
            patch(
                "api.routes.v1.financial_routes.ContaReceberSaldoRepositoryImpl"
            ) as mock_rec_saldo,
            patch(
                "api.routes.v1.financial_routes.ContaPagarSaldoRepositoryImpl"
            ) as mock_pag_saldo,
            patch("api.routes.v1.financial_routes.LancamentoRepositoryImpl") as mock_lanc_cls,
        ):
            mock_rec_cls.return_value.sum_open = AsyncMock(return_value=10000.0)
            mock_pag_cls.return_value.sum_open = AsyncMock(return_value=6000.0)
            mock_rec_saldo.return_value.total_receber_vencido = AsyncMock(return_value=2000.0)
            mock_pag_saldo.return_value.total_pagar_vencido = AsyncMock(return_value=1000.0)
            mock_lanc_cls.return_value.sum_by_periodo = AsyncMock(return_value=(5000.0, 3000.0))
            mock_lanc_cls.return_value.saldo_ate_data = AsyncMock(return_value=8000.0)

            from api.routes.v1.financial_routes import financial_dashboard
            result = await financial_dashboard(session=mock_session, _={})

            assert result.total_a_receber == 10000.0
            assert result.total_a_pagar == 6000.0
            assert result.saldo_previsto == 4000.0
            assert result.total_recebido_mes == 5000.0
            assert result.total_pago_mes == 3000.0
            assert result.saldo_disponivel == 8000.0


class TestContasReceber:
    async def test_create_conta_receber(self, mock_session):
        with (
            patch("api.routes.v1.financial_routes.ContaReceberRepositoryImpl") as mock_cls,
            patch("api.routes.v1.financial_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_cls.return_value
            mock_repo.save = AsyncMock(side_effect=lambda instance: _finalize(instance))
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.financial_routes import create_conta_receber
            body = ContaReceberCreate(
                cliente_id=uuid4(),
                data_vencimento=TODAY,
                valor_original=5000,
                numero_documento="NF-001",
            )
            result = await create_conta_receber(
                body=body, session=mock_session, _={},
            )

            assert result.valor_original == 5000
            assert result.status == "aberto"
            assert mock_repo.save.called
            assert mock_uow_cls.return_value.commit.called

    async def test_get_conta_receber_404(self, mock_session):
        with patch("api.routes.v1.financial_routes.ContaReceberRepositoryImpl") as mock_cls:
            mock_cls.return_value.find_by_id = AsyncMock(return_value=None)

            from fastapi import HTTPException

            from api.routes.v1.financial_routes import get_conta_receber
            with pytest.raises(HTTPException) as exc:
                await get_conta_receber(conta_id=uuid4(), session=mock_session, _={})
            assert exc.value.status_code == 404

    async def test_registrar_recebimento_marca_pago(
        self, mock_session, sample_conta_receber,
    ):
        with (
            patch("api.routes.v1.financial_routes.ContaReceberRepositoryImpl") as mock_rec_cls,
            patch("api.routes.v1.financial_routes.BaixaRepositoryImpl") as mock_baixa_cls,
            patch("api.routes.v1.financial_routes.LancamentoRepositoryImpl") as mock_lanc_cls,
            patch("api.routes.v1.financial_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_rec = mock_rec_cls.return_value
            mock_rec.find_by_id = AsyncMock(return_value=sample_conta_receber)
            mock_baixa_cls.return_value.save = AsyncMock(side_effect=lambda i: _finalize(i))
            mock_lanc_cls.return_value.save = AsyncMock(side_effect=lambda i: _finalize(i))
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.financial_routes import registrar_recebimento
            body = ReceberBaixaInput(
                valor_pago=5000,
                forma_pagamento="pix",
            )
            result = await registrar_recebimento(
                conta_id=sample_conta_receber.id, body=body,
                session=mock_session, current_user={"sub": str(uuid4())}, _={},
            )

            assert result.status == "pago"
            assert result.valor_pago == 5000
            assert mock_uow_cls.return_value.commit.called


class TestContasPagar:
    async def test_create_conta_pagar(self, mock_session):
        with (
            patch("api.routes.v1.financial_routes.ContaPagarRepositoryImpl") as mock_cls,
            patch("api.routes.v1.financial_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_cls.return_value
            mock_repo.save = AsyncMock(side_effect=lambda instance: _finalize(instance))
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.financial_routes import create_conta_pagar
            body = ContaPagarCreate(
                data_vencimento=TODAY,
                valor_original=3000,
                numero_documento="NF-Compra-001",
            )
            result = await create_conta_pagar(
                body=body, session=mock_session, _={},
            )

            assert result.valor_original == 3000
            assert result.status == "aberto"

    async def test_get_conta_pagar_404(self, mock_session):
        with patch("api.routes.v1.financial_routes.ContaPagarRepositoryImpl") as mock_cls:
            mock_cls.return_value.find_by_id = AsyncMock(return_value=None)

            from fastapi import HTTPException

            from api.routes.v1.financial_routes import get_conta_pagar
            with pytest.raises(HTTPException) as exc:
                await get_conta_pagar(conta_id=uuid4(), session=mock_session, _={})
            assert exc.value.status_code == 404

    async def test_registrar_pagamento_marca_pago(
        self, mock_session, sample_conta_pagar,
    ):
        with (
            patch("api.routes.v1.financial_routes.ContaPagarRepositoryImpl") as mock_pag_cls,
            patch("api.routes.v1.financial_routes.BaixaRepositoryImpl") as mock_baixa_cls,
            patch("api.routes.v1.financial_routes.LancamentoRepositoryImpl") as mock_lanc_cls,
            patch("api.routes.v1.financial_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_pag = mock_pag_cls.return_value
            mock_pag.find_by_id = AsyncMock(return_value=sample_conta_pagar)
            mock_baixa_cls.return_value.save = AsyncMock(side_effect=lambda i: _finalize(i))
            mock_lanc_cls.return_value.save = AsyncMock(side_effect=lambda i: _finalize(i))
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.financial_routes import registrar_pagamento
            body = PagarBaixaInput(valor_pago=3000)
            result = await registrar_pagamento(
                conta_id=sample_conta_pagar.id, body=body,
                session=mock_session, current_user={"sub": str(uuid4())}, _={},
            )

            assert result.status == "pago"
            assert result.valor_pago == 3000


class TestFluxoCaixa:
    async def test_create_lancamento(self, mock_session):
        with (
            patch("api.routes.v1.financial_routes.LancamentoRepositoryImpl") as mock_cls,
            patch("api.routes.v1.financial_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_cls.return_value
            mock_repo.save = AsyncMock(side_effect=lambda instance: _finalize(instance))
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.financial_routes import create_lancamento
            body = LancamentoCreate(
                tipo="entrada",
                valor=1000,
                categoria="vendas",
                descricao="Venda do dia",
            )
            result = await create_lancamento(
                body=body, session=mock_session, _={},
            )

            assert result.valor == 1000
            assert result.tipo == "entrada"
            assert result.categoria == "vendas"

    async def test_projecao_fluxo_caixa(self, mock_session):
        with (
            patch("api.routes.v1.financial_routes.LancamentoRepositoryImpl") as mock_lanc_cls,
            patch("api.routes.v1.financial_routes.ContaReceberSaldoRepositoryImpl") as mock_rec_cls,
            patch("api.routes.v1.financial_routes.ContaPagarSaldoRepositoryImpl") as mock_pag_cls,
        ):
            mock_lanc_cls.return_value.saldo_ate_data = AsyncMock(return_value=5000.0)
            mock_rec_cls.return_value.entradas_previstas_periodo = AsyncMock(return_value=8000.0)
            mock_pag_cls.return_value.saidas_previstas_periodo = AsyncMock(return_value=4000.0)

            from api.routes.v1.financial_routes import fluxo_caixa_projecao
            result = await fluxo_caixa_projecao(
                dias=90, session=mock_session, _={},
            )

            assert result.saldo_atual == 5000.0
            assert len(result.items) == 3
            assert result.items[0].entradas_previstas == 8000.0
            assert result.items[0].saidas_previstas == 4000.0


class TestBoleto:
    async def test_gerar_boleto(self, mock_session, sample_conta_receber):
        with (
            patch("api.routes.v1.financial_routes.ContaReceberRepositoryImpl") as mock_rec_cls,
            patch("api.routes.v1.financial_routes.BoletoRepositoryImpl") as mock_bol_cls,
            patch("api.routes.v1.financial_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_rec = mock_rec_cls.return_value
            mock_rec.find_by_id = AsyncMock(return_value=sample_conta_receber)
            mock_bol = mock_bol_cls.return_value
            mock_bol.save = AsyncMock(side_effect=lambda instance: _finalize(instance))
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.financial_routes import gerar_boleto
            body = BoletoGerarInput(data_vencimento=TODAY)
            result = await gerar_boleto(
                conta_id=sample_conta_receber.id, body=body,
                session=mock_session, _={},
            )

            assert result.nosso_numero is not None
            assert result.valor_nominal == 5000
            assert result.status == "gerado"
            assert mock_bol.save.called

    async def test_get_boleto_404(self, mock_session):
        with patch("api.routes.v1.financial_routes.BoletoRepositoryImpl") as mock_cls:
            mock_cls.return_value.find_by_id = AsyncMock(return_value=None)

            from fastapi import HTTPException

            from api.routes.v1.financial_routes import get_boleto
            with pytest.raises(HTTPException) as exc:
                await get_boleto(boleto_id=uuid4(), session=mock_session, _={})
            assert exc.value.status_code == 404


class TestPix:
    async def test_gerar_pix(self, mock_session, sample_conta_receber):
        with (
            patch("api.routes.v1.financial_routes.ContaReceberRepositoryImpl") as mock_rec_cls,
            patch("api.routes.v1.financial_routes.PixCobrancaRepositoryImpl") as mock_pix_cls,
            patch("api.routes.v1.financial_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_rec = mock_rec_cls.return_value
            mock_rec.find_by_id = AsyncMock(return_value=sample_conta_receber)
            mock_pix = mock_pix_cls.return_value
            mock_pix.save = AsyncMock(side_effect=lambda instance: _finalize(instance))
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.financial_routes import gerar_pix
            body = PixGerarInput()
            result = await gerar_pix(
                conta_id=sample_conta_receber.id, body=body,
                session=mock_session, _={},
            )

            assert result.txid is not None
            assert result.valor == 5000
            assert result.status == "ativo"
            assert mock_pix.save.called


class TestInadimplencia:
    async def test_list_inadimplencia(self, mock_session):
        with patch(
            "api.routes.v1.financial_routes.ContaReceberSaldoRepositoryImpl"
        ) as mock_cls:
            mock_conta = MagicMock(spec=ContaReceberModel)
            mock_conta.id = uuid4()
            mock_conta.cliente_id = uuid4()
            mock_conta.cliente.nome_razao_social = "Cliente Teste"
            mock_conta.numero_documento = "NF-001"
            mock_conta.data_vencimento = date(2026, 1, 1)
            mock_conta.valor_original = 5000.0
            mock_conta.valor_pago = 0.0
            mock_conta.desconto = 0.0
            mock_conta.juros = 0.0
            mock_conta.multa = 0.0
            mock_cls.return_value.find_vencidos_com_cliente = AsyncMock(
                return_value=[mock_conta]
            )

            from api.routes.v1.financial_routes import list_inadimplencia
            result = await list_inadimplencia(session=mock_session, _={})

            assert result.quantidade_total == 1
            assert result.total_geral > 0
            assert result.items[0].cliente_nome == "Cliente Teste"


class TestRelatorios:
    async def test_relatorio_dre(self, mock_session):
        with patch(
            "api.routes.v1.financial_routes.LancamentoRepositoryImpl"
        ) as mock_cls:
            mock_cls.return_value.sum_by_categoria_periodo = AsyncMock(return_value=[
                {"categoria": "vendas", "tipo": "entrada", "total": 10000.0},
                {"categoria": "salarios", "tipo": "saida", "total": 5000.0},
                {"categoria": "impostos", "tipo": "saida", "total": 2000.0},
            ])

            from api.routes.v1.financial_routes import relatorio_dre
            result = await relatorio_dre(
                data_inicio=date(2026, 1, 1),
                data_fim=date(2026, 1, 31),
                session=mock_session, _={},
            )

            assert result.total_receitas == 10000.0
            assert result.total_despesas == 7000.0
            assert result.resultado == 3000.0
            assert result.data_inicio == date(2026, 1, 1)
