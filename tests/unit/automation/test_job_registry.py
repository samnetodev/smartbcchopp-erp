from unittest.mock import AsyncMock

import pytest

from infrastructure.automation.base import BaseJob
from infrastructure.automation.registry import (
    get_all_jobs,
    get_job,
    list_job_info,
    register_job,
)


class _JobParaTeste(BaseJob):
    def job_id(self) -> str:
        return "job_teste"

    def description(self) -> str:
        return "Job de teste"

    def trigger(self):
        from apscheduler.triggers.interval import IntervalTrigger
        return IntervalTrigger(hours=1)

    async def execute(self, session):
        return [{"tipo": "teste", "titulo": "Teste", "nivel": "info"}]


class TestRegistry:
    def setup_method(self):
        # Limpa registry entre testes
        import infrastructure.automation.registry as reg
        reg._job_registry = {}

    def test_register_and_get(self):
        register_job(_JobParaTeste)
        cls = get_job("job_teste")
        assert cls is not None
        assert cls().job_id() == "job_teste"

    def test_list_job_info(self):
        register_job(_JobParaTeste)
        info = list_job_info()
        assert len(info) == 1
        assert info[0]["job_id"] == "job_teste"
        assert "description" in info[0]
        assert "trigger" in info[0]

    def test_get_all_jobs(self):
        register_job(_JobParaTeste)
        all_jobs = get_all_jobs()
        assert "job_teste" in all_jobs

    def test_get_job_not_found(self):
        assert get_job("nao_existe") is None


class TestBaseJob:
    @pytest.mark.asyncio
    async def test_execute_returns_list(self):
        job = _JobParaTeste()
        mock_session = AsyncMock()
        result = await job.execute(mock_session)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["tipo"] == "teste"

    @pytest.mark.asyncio
    async def test_pre_execute_logs(self):
        job = _JobParaTeste()
        mock_session = AsyncMock()
        await job.pre_execute(mock_session)

    @pytest.mark.asyncio
    async def test_post_execute(self):
        job = _JobParaTeste()
        mock_session = AsyncMock()
        await job.post_execute(mock_session, [])
        await job.post_execute(mock_session, [{"tipo": "x"}])


@pytest.mark.asyncio
async def test_jobs_are_registered():
    """Verifica que os jobs reais estão registrados ao importá-los."""
    import infrastructure.automation.jobs.alertas_documento  # noqa: F401
    import infrastructure.automation.jobs.alertas_multa  # noqa: F401
    import infrastructure.automation.jobs.boleto  # noqa: F401
    import infrastructure.automation.jobs.chopeira_parada  # noqa: F401
    import infrastructure.automation.jobs.cliente_inativo  # noqa: F401
    import infrastructure.automation.jobs.contas  # noqa: F401
    import infrastructure.automation.jobs.estoque_baixo  # noqa: F401
    import infrastructure.automation.jobs.seguro  # noqa: F401
    import infrastructure.automation.jobs.troca_oleo  # noqa: F401

    all_jobs = get_all_jobs()
    expected = [
        "alerta_documento",
        "alerta_multa",
        "troca_oleo",
        "seguro",
        "cliente_inativo",
        "estoque_baixo",
        "chopeira_parada",
        "boleto",
        "contas_receber",
        "contas_pagar",
    ]
    for jid in expected:
        assert jid in all_jobs, f"Job '{jid}' não registrado"
