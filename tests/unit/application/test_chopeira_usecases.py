from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from api.serializers.chopeira_schema import ChopeiraCreate, InstallChopeiraInput
from database.models.chopeira import ChopeiraModel, ChopeiraStatus, ChopeiraTipo
from database.models.chopeira_manutencao import (
    ChopeiraManutencaoModel,
    ManutencaoStatus,
    ManutencaoTipo,
)


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def chopeira_repo_patch():
    return patch(
        "api.routes.v1.chopeira_routes.ChopeiraRepositoryImpl"
    )


@pytest.fixture
def sample_chopeira() -> ChopeiraModel:
    c = ChopeiraModel(
        codigo_identificacao="CHP-001",
        numero_serie="SN-12345",
        marca="Brahma",
        modelo="B100",
        tipo=ChopeiraTipo.CHOPEIRA,
        status=ChopeiraStatus.DISPONIVEL,
        ativo=True,
    )
    c.id = uuid4()
    return c


class TestChopeiraCrud:
    async def test_create_chopeira_creates_and_commits(self, mock_session, sample_chopeira):
        with (
            patch(
                "api.routes.v1.chopeira_routes.ChopeiraRepositoryImpl"
            ) as mock_repo_cls,
            patch(
                "api.routes.v1.chopeira_routes.AsyncUnitOfWork"
            ) as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_codigo = AsyncMock(return_value=None)
            mock_repo.save = AsyncMock(return_value=sample_chopeira)

            mock_uow_instance = mock_uow_cls.return_value
            mock_uow_instance.commit = AsyncMock()

            body = ChopeiraCreate(
                codigo_identificacao="CHP-001",
                marca="Brahma",
                modelo="B100",
                tipo="chopeira",
            )

            from api.routes.v1.chopeira_routes import create_chopeira

            result = await create_chopeira(
                body=body,
                session=mock_session,
                current_user={"sub": str(uuid4())},
                _={},
            )

            assert result.codigo_identificacao == "CHP-001"
            assert result.marca == "Brahma"
            assert result.status == ChopeiraStatus.DISPONIVEL.value
            assert mock_repo.save.called
            assert mock_uow_instance.commit.called

    async def test_create_chopeira_raises_on_duplicate_codigo(self, mock_session):
        with patch(
            "api.routes.v1.chopeira_routes.ChopeiraRepositoryImpl"
        ) as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_codigo = AsyncMock(
                return_value=MagicMock(spec=ChopeiraModel)
            )

            body = ChopeiraCreate(
                codigo_identificacao="CHP-001",
                marca="Brahma",
                modelo="B100",
                tipo="chopeira",
            )

            from fastapi import HTTPException

            from api.routes.v1.chopeira_routes import create_chopeira

            with pytest.raises(HTTPException) as exc:
                await create_chopeira(
                    body=body,
                    session=mock_session,
                    current_user={"sub": str(uuid4())},
                    _={},
                )
            assert exc.value.status_code == 409

    async def test_get_chopeira_returns_404_when_not_found(self, mock_session):
        with patch(
            "api.routes.v1.chopeira_routes.ChopeiraRepositoryImpl"
        ) as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=None)

            from fastapi import HTTPException

            from api.routes.v1.chopeira_routes import get_chopeira

            with pytest.raises(HTTPException) as exc:
                await get_chopeira(
                    chopeira_id=uuid4(),
                    session=mock_session,
                    _={},
                )
            assert exc.value.status_code == 404


class TestChopeiraInstall:
    async def test_install_sets_status_and_creates_history(self, mock_session, sample_chopeira):
        with (
            patch(
                "api.routes.v1.chopeira_routes.ChopeiraRepositoryImpl"
            ) as mock_repo_cls,
            patch(
                "api.routes.v1.chopeira_routes.ChopeiraHistoricoRepositoryImpl"
            ) as mock_hist_repo_cls,
            patch(
                "api.routes.v1.chopeira_routes.AsyncUnitOfWork"
            ) as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=sample_chopeira)
            mock_repo.save = AsyncMock(return_value=sample_chopeira)

            mock_hist_repo = mock_hist_repo_cls.return_value
            mock_hist_repo.save = AsyncMock()

            mock_uow_instance = mock_uow_cls.return_value
            mock_uow_instance.commit = AsyncMock()

            mock_session.get = AsyncMock(
                return_value=MagicMock(
                    spec=["id", "nome_razao_social"], id=uuid4(), nome_razao_social="Cliente Teste"
                )
            )

            from api.routes.v1.chopeira_routes import install_chopeira

            body = InstallChopeiraInput(
                cliente_id=uuid4(),
                data_instalacao=date.today(),
            )
            result = await install_chopeira(
                chopeira_id=sample_chopeira.id,
                body=body,
                session=mock_session,
                current_user={"sub": str(uuid4())},
                _={},
            )

            assert result.status == ChopeiraStatus.INSTALADA.value
            assert mock_repo.save.called
            assert mock_hist_repo.save.called
            assert mock_uow_instance.commit.called

    async def test_uninstall_returns_to_available(self, mock_session, sample_chopeira):
        sample_chopeira.status = ChopeiraStatus.INSTALADA
        sample_chopeira.cliente_id = uuid4()

        with (
            patch(
                "api.routes.v1.chopeira_routes.ChopeiraRepositoryImpl"
            ) as mock_repo_cls,
            patch(
                "api.routes.v1.chopeira_routes.ChopeiraHistoricoRepositoryImpl"
            ) as mock_hist_repo_cls,
            patch(
                "api.routes.v1.chopeira_routes.AsyncUnitOfWork"
            ) as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=sample_chopeira)
            mock_repo.save = AsyncMock(return_value=sample_chopeira)

            mock_hist_repo = mock_hist_repo_cls.return_value
            mock_hist_repo.save = AsyncMock()

            mock_uow_instance = mock_uow_cls.return_value
            mock_uow_instance.commit = AsyncMock()

            from api.routes.v1.chopeira_routes import uninstall_chopeira

            result = await uninstall_chopeira(
                chopeira_id=sample_chopeira.id,
                session=mock_session,
                current_user={"sub": str(uuid4())},
                _={},
            )

            assert result.status == ChopeiraStatus.DISPONIVEL.value
            assert result.cliente_id is None
            assert mock_hist_repo.save.called


class TestChopeiraMaintenance:
    async def test_create_maintenance_changes_chopeira_status(self, mock_session, sample_chopeira):
        sample_chopeira.status = ChopeiraStatus.INSTALADA
        sample_chopeira.id = uuid4()

        with (
            patch(
                "api.routes.v1.chopeira_routes.ChopeiraManutencaoRepositoryImpl"
            ) as mock_manut_repo_cls,
            patch(
                "api.routes.v1.chopeira_routes.ChopeiraRepositoryImpl"
            ) as mock_repo_cls,
            patch(
                "api.routes.v1.chopeira_routes.ChopeiraHistoricoRepositoryImpl"
            ) as mock_hist_repo_cls,
            patch(
                "api.routes.v1.chopeira_routes.AsyncUnitOfWork"
            ) as mock_uow_cls,
        ):
            mock_manut_repo = mock_manut_repo_cls.return_value

            async def save_and_return(instance):
                instance.id = uuid4()
                return instance

            mock_manut_repo.save = AsyncMock(side_effect=save_and_return)

            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=sample_chopeira)

            mock_hist_repo = mock_hist_repo_cls.return_value
            mock_hist_repo.save = AsyncMock()

            mock_uow_instance = mock_uow_cls.return_value
            mock_uow_instance.commit = AsyncMock()

            from api.routes.v1.chopeira_routes import create_maintenance
            from api.serializers.chopeira_schema import ManutencaoCreate

            body = ManutencaoCreate(
                tipo="preventiva",
                data_solicitacao=date.today(),
                descricao_problema="Revisão periódica",
            )
            result = await create_maintenance(
                chopeira_id=sample_chopeira.id,
                body=body,
                session=mock_session,
                current_user={"sub": str(uuid4())},
                _={},
            )

            assert result.tipo == ManutencaoTipo.PREVENTIVA.value
            assert sample_chopeira.status == ChopeiraStatus.MANUTENCAO
            assert mock_manut_repo.save.called
            assert mock_hist_repo.save.called

    async def test_complete_maintenance_restores_status(self, mock_session, sample_chopeira):
        sample_chopeira.status = ChopeiraStatus.MANUTENCAO
        sample_chopeira.cliente_id = uuid4()

        manutencao = ChopeiraManutencaoModel(
            tipo=ManutencaoTipo.CORRETIVA,
            status=ManutencaoStatus.ANDAMENTO,
            data_solicitacao=date.today(),
            custo_pecas=0.0,
            custo_servico=0.0,
            chopeira_id=sample_chopeira.id,
        )
        manutencao.id = uuid4()

        with (
            patch(
                "api.routes.v1.chopeira_routes.ChopeiraManutencaoRepositoryImpl"
            ) as mock_manut_repo_cls,
            patch(
                "api.routes.v1.chopeira_routes.ChopeiraRepositoryImpl"
            ) as mock_repo_cls,
            patch(
                "api.routes.v1.chopeira_routes.AsyncUnitOfWork"
            ) as mock_uow_cls,
        ):
            mock_manut_repo = mock_manut_repo_cls.return_value
            mock_manut_repo.find_by_id = AsyncMock(return_value=manutencao)
            mock_manut_repo.save = AsyncMock(return_value=manutencao)

            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=sample_chopeira)

            mock_uow_instance = mock_uow_cls.return_value
            mock_uow_instance.commit = AsyncMock()

            from api.routes.v1.chopeira_routes import complete_maintenance

            result = await complete_maintenance(
                manutencao_id=manutencao.id,
                session=mock_session,
                current_user={"sub": str(uuid4())},
                _={},
            )

            assert result.status == ManutencaoStatus.CONCLUIDA.value
            assert sample_chopeira.status == ChopeiraStatus.INSTALADA
            assert mock_manut_repo.save.called
