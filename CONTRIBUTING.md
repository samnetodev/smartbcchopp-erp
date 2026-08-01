# Contribuindo

Obrigado pelo interesse em contribuir! Este projeto segue **Clean Architecture + DDD** e padrões rigorosos de qualidade. Antes de abrir um PR, leia este guia.

## Setup

```bash
# 1. Dependências Python
pip install -e ".[dev]"

# 2. PostgreSQL + Redis (Docker)
docker compose -f docker/docker-compose.yml up -d postgres redis

# 3. Migrations
make migrate

# 4. Dados demo (opcional)
python -m entrypoints.cli.seed_data
```

## Padrões de código

- **Camadas**: `api/` (thin, HTTP) → `core/application/usecases/` (orquestração) → `core/domain/` (entidades puras) → `database/` (ORM/repos).
- **`core/` não pode importar nada de fora de `core/`** (nem SQLAlchemy).
- Use cases retornam `Success[T] | Failure[E]` (`core/shared/result.py`) — **nunca** lance exceções de negócio.
- Entidades de domínio são **dataclasses**; ORM models ficam em `database/models/`.
- Novas rotas em `api/routes/v1/` e registradas em `app/main.py:register_routes()`.
- Commits seguem [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `infra:`.

## Checklist antes do PR

- [ ] `make lint` (ruff check .) — 0 erros
- [ ] `make typecheck` (mypy --strict .) — 0 erros
- [ ] `make test` — todos os testes verdes
- [ ] Frontend: `npx tsc --noEmit` e `npm run build` em `web/`
- [ ] Documentação atualizada quando necessário

## Fluxo

1. Fork o repositório.
2. Crie uma branch: `git checkout -b feat/minha-feature`.
3. Commit suas mudanças com mensagem convencional.
4. Abra um Pull Request para `main` descrevendo o que mudou e como testar.
