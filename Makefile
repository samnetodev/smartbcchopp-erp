.PHONY: install dev lint typecheck test test-cov migrate makemigrations shell \
        docker-up docker-down docker-prod docker-logs docker-ps clean \
        web-install web-dev web-build backup restore setup update

# ──────────────────────────────────────
# Development
# ──────────────────────────────────────

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check . --fix

typecheck:
	mypy .

test:
	pytest

test-cov:
	pytest --cov=app --cov=core --cov=api --cov=database --cov-report=term-missing

migrate:
	alembic upgrade head

makemigrations:
	alembic revision --autogenerate -m "$(message)"

shell:
	python

# ──────────────────────────────────────
# Docker
# ──────────────────────────────────────

docker-up:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d --build

docker-down:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml down

docker-prod:
	docker compose -f docker/docker-compose.yml up -d --build

docker-logs:
	docker compose -f docker/docker-compose.yml logs -f $(service)

docker-ps:
	docker compose -f docker/docker-compose.yml ps

docker-clean:
	docker compose -f docker/docker-compose.yml down -v

# ──────────────────────────────────────
# Web (Frontend)
# ──────────────────────────────────────

web-install:
	cd web && npm install

web-dev:
	cd web && npm run dev

web-build:
	cd web && npm run build

# ──────────────────────────────────────
# Production
# ──────────────────────────────────────

setup:
	sudo bash scripts/setup.sh

update:
	sudo bash scripts/update.sh

backup:
	docker compose -f docker/docker-compose.yml exec -T postgres /backup/backup.sh

restore:
	docker compose -f docker/docker-compose.yml exec -T postgres /backup/restore.sh $(file)

# ──────────────────────────────────────
# Utilities
# ──────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
