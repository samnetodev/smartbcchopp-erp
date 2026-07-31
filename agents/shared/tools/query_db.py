#!/usr/bin/env python3
"""
Executor de consultas SQL read-only para Agentes de IA.

Uso:
    python query_db.py "SELECT * FROM cliente LIMIT 5"
    python query_db.py --json "SELECT COUNT(*) FROM pedido"
    python query_db.py --db-url "postgresql+asyncpg://user:pass@localhost:5432/db" "SELECT 1"

Valida que apenas comandos SELECT / WITH / EXPLAIN são executados.
Retorna código 0 em sucesso, 1 em erro (query inválida ou falha de conexão).
"""

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

# ── Caminho do projeto para importar settings ──
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Regex para validar queries read-only
READ_ONLY_RE = re.compile(
    r"^\s*(SELECT|WITH|EXPLAIN|SHOW|DESCRIBE)\s",
    re.IGNORECASE | re.MULTILINE,
)


def is_read_only(query: str) -> bool:
    """Verifica se a query é somente leitura."""
    stripped = query.strip().rstrip(";")
    if not stripped:
        return False
    return bool(READ_ONLY_RE.match(stripped))


async def execute_query(database_url: str, query: str, output_json: bool = False) -> None:
    """Executa uma query e imprime o resultado."""
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    engine = create_async_engine(database_url, echo=False)
    try:
        async with AsyncSession(engine) as session:
            result = await session.execute(text(query))

            if result.returns_rows:
                rows = result.all()
                col_names = list(result.keys())

                if output_json:
                    data = [dict(zip(col_names, row)) for row in rows]
                    # Converte tipos não serializáveis
                    output = json.dumps(data, default=str, ensure_ascii=False, indent=2)
                    print(output)
                else:
                    if not rows:
                        print("(0 rows)")
                        return
                    # Formata como tabela simples
                    col_widths = [len(c) for c in col_names]
                    for row in rows:
                        for i, val in enumerate(row):
                            col_widths[i] = max(col_widths[i], len(str(val)))
                    # Header
                    header = " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(col_names))
                    sep = "-+-".join("-" * w for w in col_widths)
                    print(header)
                    print(sep)
                    for row in rows:
                        line = " | ".join(
                            str(val).ljust(col_widths[i]) for i, val in enumerate(row)
                        )
                        print(line)
                    print(f"\n({len(rows)} rows)")
            else:
                print("Query executed (no rows returned)")
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Executor de SQL read-only para Agentes IA")
    parser.add_argument("query", type=str, help="SQL query a ser executada")
    parser.add_argument("--json", action="store_true", help="Saída em formato JSON")
    parser.add_argument("--db-url", type=str, default=None, help="URL do banco (opcional)")

    args = parser.parse_args()

    # Valida query read-only
    if not is_read_only(args.query):
        print("ERRO: Apenas consultas SELECT / WITH / EXPLAIN são permitidas.", file=sys.stderr)
        sys.exit(1)

    # Resolve DATABASE_URL
    db_url = args.db_url
    if not db_url:
        try:
            from config.settings import get_settings

            settings = get_settings()
            db_url = settings.DATABASE_URL
        except Exception as e:
            print(f"ERRO: Não foi possível carregar settings: {e}", file=sys.stderr)
            print("Dica: Use --db-url para informar a URL do banco.", file=sys.stderr)
            sys.exit(1)

    if not db_url:
        print("ERRO: DATABASE_URL não configurada.", file=sys.stderr)
        sys.exit(1)

    try:
        asyncio.run(execute_query(db_url, args.query, output_json=args.json))
    except Exception as e:
        print(f"ERRO na consulta: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
