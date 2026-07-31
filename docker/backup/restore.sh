#!/bin/sh
set -e

# Database restore script for SmartBcChopp ERP
# Usage: ./restore.sh <backup_file.dump>
#
# WARNING: This will DROP and recreate the database.

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.dump>"
    echo "Available backups:"
    ls -lh ./backups/*.dump 2>/dev/null || echo "No .dump files found in ./backups/"
    exit 1
fi

BACKUP_FILE="$1"
DB_NAME="${POSTGRES_DB:-smartbcchopp}"
DB_USER="${POSTGRES_USER:-smartbcchopp}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: File '$BACKUP_FILE' not found."
    exit 1
fi

echo "=== Database Restore: $DB_NAME ==="
echo "Backup file: $BACKUP_FILE"
echo "WARNING: This will DROP the existing database '$DB_NAME'!"
echo "Press Ctrl+C within 5 seconds to abort..."
sleep 5

echo "Proceeding with restore..."

# Terminate existing connections and drop database
PGPASSWORD="${POSTGRES_PASSWORD}" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d postgres \
    -c "SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '$DB_NAME'
          AND pid <> pg_backend_pid();" 2>/dev/null || true

PGPASSWORD="${POSTGRES_PASSWORD}" dropdb \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    --if-exists \
    "$DB_NAME"

PGPASSWORD="${POSTGRES_PASSWORD}" createdb \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    "$DB_NAME"

# Restore from custom format dump
PGPASSWORD="${POSTGRES_PASSWORD}" pg_restore \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-acl \
    --verbose \
    "$BACKUP_FILE"

echo "=== Restore completed successfully ==="
