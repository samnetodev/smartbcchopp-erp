#!/bin/sh
set -e

echo "--- Running database migrations ---"
alembic upgrade head

if [ "${DEMO_SEED:-false}" = "true" ]; then
    echo "--- Seeding demo data (idempotent) ---"
    python -m entrypoints.cli.seed_data --if-empty
fi

echo "--- Starting application ---"
exec "$@"
