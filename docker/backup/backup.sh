#!/bin/sh
set -e

# Database backup script for SmartBcChopp ERP
# Usage: ./backup.sh [output_directory]
# Default output: /backup (mounted volume in container) or ./backups locally

BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="${POSTGRES_DB:-smartbcchopp}"
DB_USER="${POSTGRES_USER:-smartbcchopp}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"

mkdir -p "$BACKUP_DIR"

echo "=== Database Backup: $DB_NAME ==="
echo "Backup directory: $BACKUP_DIR"
echo "Timestamp: $TIMESTAMP"

# Dump with compression
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -F c \
    -Z 9 \
    -v \
    -f "${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump" 2>&1

# Create plain SQL backup (lighter for diffs)
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-acl \
    -f "${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql"

# Compress SQL
gzip -f "${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql"

echo "=== Backup completed ==="
echo "Files:"
ls -lh "${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}"*

# Retention: keep last 30 days
find "$BACKUP_DIR" -name "${DB_NAME}_*.dump" -mtime +30 -delete
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +30 -delete
echo "Old backups (>30 days) cleaned up."
