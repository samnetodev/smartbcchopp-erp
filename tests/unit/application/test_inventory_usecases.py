from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from core.application.use_cases.inventory.create_movement_usecase import (
    CreateMovementUseCase,
    MovementInput,
)
from database.models.estoque import EstoqueModel
from database.models.movimentacao import MovimentacaoTipo


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.session = AsyncMock()
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    return uow


@pytest.fixture
def use_case(mock_uow):
    return CreateMovementUseCase(mock_uow)


@pytest.fixture
def produto_id() -> UUID:
    return uuid4()


@pytest.fixture
def deposito_id() -> UUID:
    return uuid4()


class TestCreateMovementUseCase:
    async def test_create_entrada_creates_movement_and_increases_stock(
        self, use_case, mock_uow, produto_id, deposito_id
    ):
        with (
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.EstoqueRepositoryImpl"
            ) as mock_estoque_repo,
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.MovimentacaoRepositoryImpl"
            ) as mock_mov_repo,
        ):
            mock_estoque_instance = mock_estoque_repo.return_value
            mock_mov_instance = mock_mov_repo.return_value
            mock_estoque_instance.find_one_by_produto_deposito = AsyncMock(return_value=None)
            mock_estoque_instance.save = AsyncMock()
            mock_mov_instance.save = AsyncMock()

            result = await use_case.execute(
                MovementInput(
                    tipo="entrada",
                    produto_id=produto_id,
                    quantidade=100.0,
                    deposito_id_origem=deposito_id,
                    observacao="Teste entrada",
                )
            )

            assert result.tipo == MovimentacaoTipo.ENTRADA
            assert result.quantidade == 100.0
            assert result.produto_id == produto_id
            assert mock_uow.commit.called

    async def test_create_saida_raises_error_when_insufficient_stock(
        self, use_case, mock_uow, produto_id, deposito_id
    ):
        with (
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.EstoqueRepositoryImpl"
            ) as mock_estoque_repo,
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.MovimentacaoRepositoryImpl"
            ),
        ):
            mock_estoque_instance = mock_estoque_repo.return_value
            saldo = MagicMock(spec=EstoqueModel)
            saldo.quantidade_atual = 10.0
            mock_estoque_instance.find_one_by_produto_deposito = AsyncMock(return_value=saldo)

            with pytest.raises(ValueError, match="Estoque insuficiente"):
                await use_case.execute(
                    MovementInput(
                        tipo="saida",
                        produto_id=produto_id,
                        quantidade=100.0,
                        deposito_id_origem=deposito_id,
                    )
                )

    async def test_create_saida_succeeds_with_enough_stock(
        self, use_case, mock_uow, produto_id, deposito_id
    ):
        with (
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.EstoqueRepositoryImpl"
            ) as mock_estoque_repo,
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.MovimentacaoRepositoryImpl"
            ) as mock_mov_repo,
        ):
            mock_estoque_instance = mock_estoque_repo.return_value
            mock_mov_instance = mock_mov_repo.return_value
            saldo = MagicMock(spec=EstoqueModel)
            saldo.quantidade_atual = 100.0
            saldo.produto_id = produto_id
            saldo.deposito_id = deposito_id
            saldo.lote_id = None
            mock_estoque_instance.find_one_by_produto_deposito = AsyncMock(return_value=saldo)
            mock_mov_instance.save = AsyncMock()

            result = await use_case.execute(
                MovementInput(
                    tipo="saida",
                    produto_id=produto_id,
                    quantidade=50.0,
                    deposito_id_origem=deposito_id,
                    observacao="Teste saida",
                )
            )

            assert result.tipo == MovimentacaoTipo.SAIDA
            assert result.quantidade == 50.0
            assert mock_uow.commit.called

    async def test_create_transferencia_moves_stock_between_depositos(
        self, use_case, mock_uow, produto_id, deposito_id
    ):
        destino_id = uuid4()
        with (
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.EstoqueRepositoryImpl"
            ) as mock_estoque_repo,
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.MovimentacaoRepositoryImpl"
            ) as mock_mov_repo,
        ):
            mock_estoque_instance = mock_estoque_repo.return_value
            mock_mov_instance = mock_mov_repo.return_value
            saldo_origem = MagicMock(spec=EstoqueModel)
            saldo_origem.quantidade_atual = 100.0
            saldo_origem.produto_id = produto_id
            saldo_origem.deposito_id = deposito_id
            saldo_origem.lote_id = None
            mock_estoque_instance.find_one_by_produto_deposito = AsyncMock(
                side_effect=[saldo_origem, None]
            )
            mock_estoque_instance.save = AsyncMock()
            mock_mov_instance.save = AsyncMock()

            result = await use_case.execute(
                MovementInput(
                    tipo="transferencia",
                    produto_id=produto_id,
                    quantidade=30.0,
                    deposito_id_origem=deposito_id,
                    deposito_id_destino=destino_id,
                    observacao="Teste transferencia",
                )
            )

            assert result.tipo == MovimentacaoTipo.TRANSFERENCIA
            assert result.deposito_id_destino == destino_id
            assert result.quantidade == 30.0
            assert mock_uow.commit.called

    async def test_create_perda_reduces_stock(
        self, use_case, mock_uow, produto_id, deposito_id
    ):
        with (
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.EstoqueRepositoryImpl"
            ) as mock_estoque_repo,
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.MovimentacaoRepositoryImpl"
            ) as mock_mov_repo,
        ):
            mock_estoque_instance = mock_estoque_repo.return_value
            mock_mov_instance = mock_mov_repo.return_value
            saldo = MagicMock(spec=EstoqueModel)
            saldo.quantidade_atual = 50.0
            mock_estoque_instance.find_one_by_produto_deposito = AsyncMock(return_value=saldo)
            mock_mov_instance.save = AsyncMock()

            result = await use_case.execute(
                MovementInput(
                    tipo="perda",
                    produto_id=produto_id,
                    quantidade=10.0,
                    deposito_id_origem=deposito_id,
                    motivo_perda="quebra",
                    observacao="Teste perda",
                )
            )

            assert result.tipo == MovimentacaoTipo.PERDA
            assert result.motivo_perda == "quebra"
            assert result.quantidade == 10.0
            assert mock_uow.commit.called

    async def test_create_ajuste_with_existing_decimal_stock(
        self, use_case, mock_uow, produto_id, deposito_id
    ):
        with (
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.EstoqueRepositoryImpl"
            ) as mock_estoque_repo,
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.MovimentacaoRepositoryImpl"
            ) as mock_mov_repo,
        ):
            mock_estoque_instance = mock_estoque_repo.return_value
            mock_mov_instance = mock_mov_repo.return_value
            saldo = MagicMock(spec=EstoqueModel)
            saldo.quantidade_atual = Decimal("5.000")
            mock_estoque_instance.find_one_by_produto_deposito = AsyncMock(return_value=saldo)
            mock_mov_instance.save = AsyncMock()

            result = await use_case.execute(
                MovementInput(
                    tipo="ajuste",
                    produto_id=produto_id,
                    quantidade=9.0,
                    deposito_id_origem=deposito_id,
                    observacao="Teste ajuste",
                )
            )

            assert result.tipo == MovimentacaoTipo.AJUSTE
            assert saldo.quantidade_atual == 9.0
            assert mock_uow.commit.called

    async def test_create_ajuste_creates_stock_when_absent(
        self, use_case, mock_uow, produto_id, deposito_id
    ):
        with (
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.EstoqueRepositoryImpl"
            ) as mock_estoque_repo,
            patch(
                "core.application.use_cases.inventory.create_movement_usecase.MovimentacaoRepositoryImpl"
            ) as mock_mov_repo,
        ):
            mock_estoque_instance = mock_estoque_repo.return_value
            mock_mov_instance = mock_mov_repo.return_value
            mock_estoque_instance.find_one_by_produto_deposito = AsyncMock(return_value=None)
            mock_estoque_instance.save = AsyncMock()
            mock_mov_instance.save = AsyncMock()

            result = await use_case.execute(
                MovementInput(
                    tipo="ajuste",
                    produto_id=produto_id,
                    quantidade=12.0,
                    deposito_id_origem=deposito_id,
                )
            )

            assert result.tipo == MovimentacaoTipo.AJUSTE
            created = mock_estoque_instance.save.await_args.args[0]
            assert created.quantidade_atual == 12.0
            assert mock_uow.commit.called


class TestCloseInventoryCountUseCase:
    async def test_close_inventory_adjusts_stock(self):
        from core.application.use_cases.inventory.close_inventory_usecase import (
            CloseInventoryCountUseCase,
        )

        mock_uow = MagicMock()
        mock_uow.session = AsyncMock()
        mock_uow.commit = AsyncMock()

        inventario_id = uuid4()
        produto_id = uuid4()
        deposito_id = uuid4()

        with (
            patch(
                "core.application.use_cases.inventory.close_inventory_usecase.InventarioRepositoryImpl"
            ) as mock_inv_repo,
            patch(
                "core.application.use_cases.inventory.close_inventory_usecase.EstoqueRepositoryImpl"
            ) as mock_estoque_repo,
            patch(
                "core.application.use_cases.inventory.close_inventory_usecase.MovimentacaoRepositoryImpl"
            ) as mock_mov_repo,
        ):
            mock_inv_instance = mock_inv_repo.return_value
            mock_estoque_instance = mock_estoque_repo.return_value
            mock_mov_instance = mock_mov_repo.return_value

            inventario = MagicMock()
            inventario.id = inventario_id
            inventario.status = "aberto"
            inventario.produto_id = produto_id
            inventario.deposito_id = deposito_id
            inventario.lote_id = None
            inventario.quantidade_sistema = 50.0
            inventario.quantidade_contada = 60.0
            inventario.diferenca = 0
            inventario.observacao = "contagem fisica"

            mock_inv_instance.find_by_id = AsyncMock(return_value=inventario)
            mock_estoque_instance.find_one_by_produto_deposito = AsyncMock(return_value=None)
            mock_estoque_instance.save = AsyncMock()
            mock_mov_instance.save = AsyncMock()

            use_case = CloseInventoryCountUseCase(mock_uow)
            result = await use_case.execute(inventario_id, usuario_id=uuid4())

            assert result.status == "fechado"
            assert result.diferenca == 10.0
            assert mock_uow.commit.called
