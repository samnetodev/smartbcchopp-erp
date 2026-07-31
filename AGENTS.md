# AGENTS.md — SmartBcChopp ERP

## Architecture

Clean Architecture + DDD. Dependency rule: `core/` has zero external dependencies.

```
app/main.py              → FastAPI factory, register_routes()
api/routes/v1/           → HTTP handlers (thin, delegate to use cases)
core/application/usecases → Orchestration (receive DTO, call repos + domain services)
core/domain/             → Entities, VOs, Aggregates, Domain Events, Repository interfaces
database/models/         → SQLAlchemy ORM (separate from domain entities)
database/repositories/   → Implement repository interfaces
infrastructure/          → Cache (Redis), messaging (event bus), external integrations
config/container.py      → DI wiring (dependency-injector)
```

## Domain entities are NOT ORM models

`core/domain/entities/` are plain dataclasses. `database/models/` are SQLAlchemy `Base` subclasses. The repository layer maps between them.

## Result monad pattern

Use cases return `Success[T] | Failure[E]` (`core/shared/result.py`), never raise business exceptions.
Pattern: `return Success(order)` or `return Failure("credit_limit_exceeded")`.

## Dependency injection

Container defined in `config/container.py` using `dependency-injector`. Wiring modules are listed there. FastAPI routes use `Depends(get_uow)` from `api/deps.py`.

## Commands

| Action | Command |
|--------|---------|
| Dev server (API) | `make dev` (uvicorn --reload) |
| Dev server (Web) | `make web-dev` (vite) |
| Install web deps | `make web-install` |
| Build web | `make web-build` |
| Lint | `make lint` (ruff check . --fix) |
| Typecheck | `make typecheck` (mypy --strict) |
| Test | `make test` (pytest, asyncio_mode=auto) |
| Test with coverage | `make test-cov` |
| Create migration | `make makemigrations message="desc"` |
| Apply migrations | `make migrate` |
| Docker up | `make docker-up` |
| Docker down | `make docker-down` |

Mypy is **strict** (`disallow_untyped_defs = true`). Ruff line-length is **100**.

## Database

- Async driver: **asyncpg** via `DATABASE_URL`. Alembic uses `DATABASE_SYNC_URL` (sync).
- Alembic config: `database/migrations/alembic.ini` (not root).
- `alembic revision --autogenerate` scans `database.models.Base.metadata`.
- UoW pattern: `async with AsyncUnitOfWork() as uow:` — rollback on exit unless `commit()` called.

## Project state

Scaffolding phase. Most files are stubs (`...`). No business logic implemented yet. All 20 tables are modeled (see `database/models/__init__.py` for the full list).

## Path note

Repo root has a space: `"/home/samneto/projetos/dashboard -smartbcchopp"`. Quote paths in shell commands.

## Makefile vs pyproject.toml

`Makefile` calls `poetry install` but `pyproject.toml` uses setuptools. Use `pip install -e ".[dev]"` if poetry is unavailable.

## Settings

Loaded from `.env` via Pydantic Settings (`config/settings.py`, `get_settings()` singleton). Must define `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`.

## Repo structure cheat sheet

- `models/`, `schemas/`, `repositories/`, `middlewares/` at root are **re-exports** for import convenience. Real code lives in `database/models/`, `api/serializers/`, `database/repositories/`, `api/middlewares/`.
- New routes go in `api/routes/v1/` + registered in `app/main.py:register_routes()`.
- Domain events in `core/domain/events/` are published after `uow.commit()` via `EventBus`.
- Infrastructure integrations (Maps, SEFAZ, Pagar.me) go in `infrastructure/messaging/integrations/`.
