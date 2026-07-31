from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from api.serializers.fleet_schema import (
    DriverCreate,
    PneuCreate,
    SeguroCreate,
    TrocaOleoCreate,
    VehicleCreate,
    VehicleKmUpdate,
)
from database.models.motorista import MotoristaModel, MotoristaStatus
from database.models.veiculo import VeiculoModel, VeiculoStatus, VeiculoTipo
from database.models.veiculo_pneu import PneuModel, PneuStatus
from database.models.veiculo_seguro import SeguroModel, SeguroStatus

NOW = datetime.now(timezone.utc)


def _finalize(instance):
    """Set SQLAlchemy Python-side defaults that don't fire on object creation."""
    if not instance.id:
        instance.id = uuid4()
    if not instance.created_at:
        instance.created_at = NOW
    if not instance.updated_at:
        instance.updated_at = NOW
    if hasattr(instance, "status") and instance.status is None:
        if isinstance(instance, SeguroModel):
            instance.status = SeguroStatus.ATIVO
        elif isinstance(instance, PneuModel):
            instance.status = PneuStatus.ATIVO
        elif isinstance(instance, MotoristaModel):
            instance.status = MotoristaStatus.DISPONIVEL
    if hasattr(instance, "ativo") and instance.ativo is None:
        instance.ativo = True
    return instance


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def sample_vehicle() -> VeiculoModel:
    v = VeiculoModel(
        placa="ABC1234", marca="VW", modelo="Constellation",
        tipo=VeiculoTipo.CAMINHAO, proprietario="proprio",
        km_atual=50000, status=VeiculoStatus.DISPONIVEL, ativo=True,
    )
    v.id = uuid4()
    return v


class TestVehicles:
    async def test_create_vehicle_creates_and_commits(self, mock_session, sample_vehicle):
        with (
            patch("api.routes.v1.fleet_routes.VeiculoRepositoryImpl") as mock_repo_cls,
            patch("api.routes.v1.fleet_routes.VeiculoHistoricoRepositoryImpl") as mock_hist_cls,
            patch("api.routes.v1.fleet_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_placa = AsyncMock(return_value=None)

            mock_repo.save = AsyncMock(side_effect=lambda instance: _finalize(instance))
            mock_hist = mock_hist_cls.return_value
            mock_hist.save = AsyncMock()
            mock_uow = mock_uow_cls.return_value
            mock_uow.commit = AsyncMock()

            body = VehicleCreate(
                placa="ABC1234", marca="VW", modelo="Constellation",
                tipo="caminhao", proprietario="proprio",
            )

            from api.routes.v1.fleet_routes import create_vehicle
            result = await create_vehicle(
                body=body, session=mock_session,
                current_user={"sub": str(uuid4())}, _={},
            )

            assert result.placa == "ABC1234"
            assert result.status == "disponivel"
            assert mock_repo.save.called
            assert mock_hist.save.called
            assert mock_uow.commit.called

    async def test_create_vehicle_raises_on_duplicate_placa(self, mock_session):
        with patch("api.routes.v1.fleet_routes.VeiculoRepositoryImpl") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_placa = AsyncMock(return_value=MagicMock(spec=VeiculoModel))

            body = VehicleCreate(
                placa="ABC1234", marca="VW", modelo="Constellation",
                tipo="caminhao", proprietario="proprio",
            )

            from fastapi import HTTPException

            from api.routes.v1.fleet_routes import create_vehicle
            with pytest.raises(HTTPException) as exc:
                await create_vehicle(
                    body=body, session=mock_session,
                    current_user={"sub": str(uuid4())}, _={},
                )
            assert exc.value.status_code == 409

    async def test_get_vehicle_returns_404_when_not_found(self, mock_session):
        with patch("api.routes.v1.fleet_routes.VeiculoRepositoryImpl") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=None)

            from fastapi import HTTPException

            from api.routes.v1.fleet_routes import get_vehicle
            with pytest.raises(HTTPException) as exc:
                await get_vehicle(vehicle_id=uuid4(), session=mock_session, _={})
            assert exc.value.status_code == 404

    async def test_update_km_creates_registro_and_history(
        self, mock_session, sample_vehicle,
    ):
        sample_vehicle.km_atual = 1000
        with (
            patch("api.routes.v1.fleet_routes.VeiculoRepositoryImpl") as mock_repo_cls,
            patch("api.routes.v1.fleet_routes.KmRegistroRepositoryImpl") as mock_km_cls,
            patch("api.routes.v1.fleet_routes.VeiculoHistoricoRepositoryImpl") as mock_hist_cls,
            patch("api.routes.v1.fleet_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=sample_vehicle)
            _finalize(sample_vehicle)
            mock_repo.save = AsyncMock(side_effect=lambda instance: _finalize(instance))

            mock_km = mock_km_cls.return_value
            mock_km.save = AsyncMock(side_effect=lambda instance: _finalize(instance))

            mock_hist = mock_hist_cls.return_value
            mock_hist.save = AsyncMock(side_effect=lambda instance: _finalize(instance))

            mock_uow = mock_uow_cls.return_value
            mock_uow.commit = AsyncMock()

            from api.routes.v1.fleet_routes import update_vehicle_km
            body = VehicleKmUpdate(km=2000, data=date.today())
            await update_vehicle_km(
                vehicle_id=sample_vehicle.id, body=body,
                session=mock_session, current_user={"sub": str(uuid4())}, _={},
            )

            assert sample_vehicle.km_atual == 2000
            assert mock_km.save.called
            assert mock_hist.save.called
            assert mock_uow.commit.called

    async def test_update_km_raises_when_not_greater(self, mock_session, sample_vehicle):
        sample_vehicle.km_atual = 5000
        with patch("api.routes.v1.fleet_routes.VeiculoRepositoryImpl") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=sample_vehicle)

            from fastapi import HTTPException

            from api.routes.v1.fleet_routes import update_vehicle_km
            body = VehicleKmUpdate(km=4000)
            with pytest.raises(HTTPException) as exc:
                await update_vehicle_km(
                    vehicle_id=sample_vehicle.id, body=body,
                    session=mock_session, current_user={"sub": str(uuid4())}, _={},
                )
            assert exc.value.status_code == 400


class TestDrivers:
    async def test_create_driver_creates_and_commits(self, mock_session):
        with (
            patch("api.routes.v1.fleet_routes.MotoristaRepositoryImpl") as mock_repo_cls,
            patch("api.routes.v1.fleet_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_cnh = AsyncMock(return_value=None)

            mock_repo.save = AsyncMock(side_effect=lambda instance: _finalize(instance))

            mock_uow = mock_uow_cls.return_value
            mock_uow.commit = AsyncMock()

            body = DriverCreate(
                numero_cnh="12345678901", categoria_cnh="E",
                data_validade_cnh=date(2030, 1, 1),
                funcionario_id=uuid4(),
            )

            from api.routes.v1.fleet_routes import create_driver
            result = await create_driver(
                body=body, session=mock_session,
                current_user={"sub": str(uuid4())}, _={},
            )

            assert result.numero_cnh == "12345678901"
            assert result.categoria_cnh == "E"
            assert mock_repo.save.called
            assert mock_uow.commit.called

    async def test_create_driver_raises_on_duplicate_cnh(self, mock_session):
        with patch("api.routes.v1.fleet_routes.MotoristaRepositoryImpl") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_cnh = AsyncMock(return_value=MagicMock(spec=MotoristaModel))

            body = DriverCreate(
                numero_cnh="12345678901", categoria_cnh="E",
                data_validade_cnh=date(2030, 1, 1),
                funcionario_id=uuid4(),
            )

            from fastapi import HTTPException

            from api.routes.v1.fleet_routes import create_driver
            with pytest.raises(HTTPException) as exc:
                await create_driver(
                    body=body, session=mock_session,
                    current_user={"sub": str(uuid4())}, _={},
                )
            assert exc.value.status_code == 409

    async def test_get_driver_returns_404_when_not_found(self, mock_session):
        with patch("api.routes.v1.fleet_routes.MotoristaRepositoryImpl") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.find_by_id = AsyncMock(return_value=None)

            from fastapi import HTTPException

            from api.routes.v1.fleet_routes import get_driver
            with pytest.raises(HTTPException) as exc:
                await get_driver(driver_id=uuid4(), session=mock_session, _={})
            assert exc.value.status_code == 404


class TestOilChange:
    async def test_create_oil_change_updates_vehicle_km(self, mock_session, sample_vehicle):
        sample_vehicle.km_atual = 50000

        with (
            patch("api.routes.v1.fleet_routes.VeiculoRepositoryImpl") as mock_veic_cls,
            patch("api.routes.v1.fleet_routes.TrocaOleoRepositoryImpl") as mock_oleo_cls,
            patch("api.routes.v1.fleet_routes.VeiculoHistoricoRepositoryImpl") as mock_hist_cls,
            patch("api.routes.v1.fleet_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_veic = mock_veic_cls.return_value
            mock_veic.find_by_id = AsyncMock(return_value=sample_vehicle)

            _finalize(sample_vehicle)
            mock_oleo = mock_oleo_cls.return_value
            mock_oleo.save = AsyncMock(side_effect=lambda instance: _finalize(instance))

            mock_hist = mock_hist_cls.return_value
            mock_hist.save = AsyncMock()

            mock_uow = mock_uow_cls.return_value
            mock_uow.commit = AsyncMock()

            from api.routes.v1.fleet_routes import create_oil_change
            body = TrocaOleoCreate(
                data=date.today(), km_atual=51000, tipo_oleo="15W40",
                quantidade_l=15, valor_oleo=200, valor_total=250,
                km_proxima_troca=56000,
            )
            result = await create_oil_change(
                vehicle_id=sample_vehicle.id, body=body,
                session=mock_session, current_user={"sub": str(uuid4())}, _={},
            )

            assert result.tipo_oleo == "15W40"
            assert sample_vehicle.km_atual == 51000
            assert sample_vehicle.km_proxima_troca_oleo == 56000
            assert mock_hist.save.called


class TestSeguro:
    async def test_create_insurance_updates_vehicle(self, mock_session, sample_vehicle):
        with (
            patch("api.routes.v1.fleet_routes.VeiculoRepositoryImpl") as mock_veic_cls,
            patch("api.routes.v1.fleet_routes.SeguroRepositoryImpl") as mock_seg_cls,
            patch("api.routes.v1.fleet_routes.VeiculoHistoricoRepositoryImpl") as mock_hist_cls,
            patch("api.routes.v1.fleet_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_veic = mock_veic_cls.return_value
            mock_veic.find_by_id = AsyncMock(return_value=sample_vehicle)

            _finalize(sample_vehicle)
            mock_seg = mock_seg_cls.return_value
            mock_seg.save = AsyncMock(side_effect=lambda instance: _finalize(instance))

            mock_hist = mock_hist_cls.return_value
            mock_hist.save = AsyncMock()

            mock_uow = mock_uow_cls.return_value
            mock_uow.commit = AsyncMock()

            from api.routes.v1.fleet_routes import create_insurance
            body = SeguroCreate(
                apolice="APO-001", seguradora="porto_seguro",
                data_inicio_vigencia=date.today(),
                data_fim_vigencia=date(2027, 1, 1),
                premio_total=5000,
            )
            result = await create_insurance(
                vehicle_id=sample_vehicle.id, body=body,
                session=mock_session, current_user={"sub": str(uuid4())}, _={},
            )

            assert result.apolice == "APO-001"
            assert sample_vehicle.data_vencimento_seguro == date(2027, 1, 1)
            assert mock_hist.save.called


class TestPneu:
    async def test_create_tire_creates_and_logs_history(self, mock_session, sample_vehicle):
        with (
            patch("api.routes.v1.fleet_routes.VeiculoRepositoryImpl") as mock_veic_cls,
            patch("api.routes.v1.fleet_routes.PneuRepositoryImpl") as mock_pneu_cls,
            patch("api.routes.v1.fleet_routes.VeiculoHistoricoRepositoryImpl") as mock_hist_cls,
            patch("api.routes.v1.fleet_routes.AsyncUnitOfWork") as mock_uow_cls,
        ):
            mock_veic = mock_veic_cls.return_value
            mock_veic.find_by_id = AsyncMock(return_value=sample_vehicle)

            _finalize(sample_vehicle)
            mock_pneu = mock_pneu_cls.return_value
            mock_pneu.save = AsyncMock(side_effect=lambda instance: _finalize(instance))

            mock_hist = mock_hist_cls.return_value
            mock_hist.save = AsyncMock()

            mock_uow = mock_uow_cls.return_value
            mock_uow.commit = AsyncMock()

            from api.routes.v1.fleet_routes import create_tire
            body = PneuCreate(
                posicao="dianteiro_e", marca="pirelli", modelo="Scorpion",
                medida="225/75R16", km_instalacao=50000,
                data_instalacao=date.today(),
            )
            result = await create_tire(
                vehicle_id=sample_vehicle.id, body=body,
                session=mock_session, current_user={"sub": str(uuid4())}, _={},
            )

            assert result.posicao == "dianteiro_e"
            assert mock_hist.save.called
