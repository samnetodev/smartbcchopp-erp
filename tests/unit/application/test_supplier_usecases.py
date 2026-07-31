from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.serializers.supplier_schema import SupplierCreate, SupplierUpdate
from database.models.fornecedor import FornecedorModel

NOW = datetime.now(timezone.utc)


def _finalize(instance):
    if not instance.id:
        instance.id = uuid4()
    if not instance.created_at:
        instance.created_at = NOW
    if not instance.updated_at:
        instance.updated_at = NOW
    if instance.status is None:
        instance.status = "ativo"
    return instance


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def sample_fornecedor() -> FornecedorModel:
    f = FornecedorModel(
        tipo_pessoa="PJ",
        nome_razao_social="Fornecedor Teste",
        cpf_cnpj="12345678000199",
        categoria="chope",
    )
    _finalize(f)
    return f


class TestFornecedores:
    async def test_create_supplier(self, mock_session):
        with (
            patch("api.routes.v1.supplier_routes.FornecedorRepositoryImpl") as mock_repo_cls,
            patch("api.routes.v1.supplier_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_cpf_cnpj = AsyncMock(return_value=None)
            mock_repo.save = AsyncMock(side_effect=lambda instance: _finalize(instance))
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.supplier_routes import create_supplier
            body = SupplierCreate(
                nome_razao_social="Fornecedor Teste",
                cpf_cnpj="12345678000199",
                categoria="chope",
                tipo_pessoa="PJ",
            )
            result = await create_supplier(body=body, session=mock_session, _={})

            assert result.nome_razao_social == "Fornecedor Teste"
            assert result.tipo_pessoa == "PJ"
            assert result.status == "ativo"
            assert mock_repo.save.called
            assert mock_uow_cls.return_value.commit.called

    async def test_create_supplier_duplicate_cpf_cnpj(self, mock_session, sample_fornecedor):
        with patch("api.routes.v1.supplier_routes.FornecedorRepositoryImpl") as mock_repo_cls:
            mock_repo_cls.return_value.find_by_cpf_cnpj = AsyncMock(return_value=sample_fornecedor)

            from api.routes.v1.supplier_routes import create_supplier
            body = SupplierCreate(
                nome_razao_social="Fornecedor Teste",
                cpf_cnpj="12345678000199",
                categoria="chope",
                tipo_pessoa="PJ",
            )
            with pytest.raises(HTTPException) as exc:
                await create_supplier(body=body, session=mock_session, _={})
            assert exc.value.status_code == 400

    async def test_update_supplier_status(self, mock_session, sample_fornecedor):
        with (
            patch("api.routes.v1.supplier_routes.FornecedorRepositoryImpl") as mock_repo_cls,
            patch("api.routes.v1.supplier_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=sample_fornecedor)
            mock_uow_cls.return_value.commit = AsyncMock()

            from api.routes.v1.supplier_routes import update_supplier
            body = SupplierUpdate(status="bloqueado")
            result = await update_supplier(
                supplier_id=sample_fornecedor.id, body=body, session=mock_session, _={}
            )

            assert result.status == "bloqueado"
            assert mock_uow_cls.return_value.commit.called

    async def test_delete_supplier_404(self, mock_session):
        with patch("api.routes.v1.supplier_routes.FornecedorRepositoryImpl") as mock_repo_cls:
            mock_repo_cls.return_value.find_by_id = AsyncMock(return_value=None)

            from api.routes.v1.supplier_routes import delete_supplier
            with pytest.raises(HTTPException) as exc:
                await delete_supplier(supplier_id=uuid4(), session=mock_session, _={})
            assert exc.value.status_code == 404
