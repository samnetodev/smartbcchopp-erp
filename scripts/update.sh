#!/bin/bash
set -euo pipefail

#=============================================================================
# SmartBcChopp ERP — Update Script
#=============================================================================
# This script updates the application to the latest version with zero downtime.
# It pulls new code, rebuilds containers, and performs a rolling restart.
#
# Usage:
#   sudo ./scripts/update.sh [--rollback]
#
# Options:
#   --rollback    Revert to the previous deployment
#=============================================================================

APP_DIR="/opt/smartbcchopp"
DOCKER_COMPOSE="docker compose -f $APP_DIR/docker/docker-compose.yml"
BACKUP_DIR="$APP_DIR/rollback"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

ROLLBACK=false
if [ "${1:-}" = "--rollback" ]; then
    ROLLBACK=true
fi

check_root() {
    if [ "$(id -u)" -ne 0 ] && [ ! -w /var/run/docker.sock ]; then
        log_error "Run as root or with Docker access: sudo $0"
        exit 1
    fi
}

rollback() {
    log_info "Performing rollback to previous version..."

    if [ ! -d "$BACKUP_DIR/prev" ]; then
        log_error "No rollback backup found at $BACKUP_DIR/prev"
        exit 1
    fi

    cd "$APP_DIR"
    cp -r "$BACKUP_DIR/prev/"* "$APP_DIR/" 2>/dev/null || true
    $DOCKER_COMPOSE up -d --build --no-deps api nginx

    log_info "Rollback completed."
    exit 0
}

update() {
    log_info "=== SmartBcChopp ERP Update ==="
    echo "Started at: $(date)"
    echo ""

    # 1. Backup current state
    log_info "Backing up current deployment..."
    mkdir -p "$BACKUP_DIR/prev"
    cp "$APP_DIR/docker/docker-compose.yml" "$BACKUP_DIR/prev/" 2>/dev/null || true

    # 2. Database backup
    log_info "Backing up database..."
    $DOCKER_COMPOSE exec -T postgres /backup/backup.sh "$BACKUP_DIR"
    log_info "Database backup saved to $BACKUP_DIR"

    # 3. Pull latest code
    log_info "Pulling latest code..."
    cd "$APP_DIR"
    git fetch origin
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u})

    if [ "$LOCAL" = "$REMOTE" ]; then
        log_info "Already up to date. Skipping."
        exit 0
    fi

    git pull origin main

    # 4. Build and restart services (zero-downtime)
    log_info "Rebuilding and restarting services..."

    # Rebuild API image
    $DOCKER_COMPOSE build --no-cache api

    # Rebuild web image
    $DOCKER_COMPOSE build --no-cache nginx

    # Restart API (new container starts before old one stops)
    $DOCKER_COMPOSE up -d --no-deps --scale api=2 api
    sleep 5

    # Health check
    for i in $(seq 1 20); do
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            log_info "New API version is healthy!"
            break
        fi
        if [ "$i" -eq 20 ]; then
            log_error "New API version failed health check. Rolling back..."
            rollback
            exit 1
        fi
        sleep 3
    done

    # Restart nginx
    $DOCKER_COMPOSE up -d --no-deps nginx

    # Scale down old API
    $DOCKER_COMPOSE up -d --no-deps --scale api=1 api

    # Run migrations
    log_info "Running database migrations..."
    $DOCKER_COMPOSE exec -T api alembic upgrade head

    # Clean up old Docker images
    log_info "Cleaning up old images..."
    docker image prune -f

    echo ""
    log_info "=== Update completed successfully ==="
    echo "New version: $(git log --oneline -1)"
    echo "Finished at: $(date)"
}

#=============================================================================
# Main
#=============================================================================

check_root

if [ "$ROLLBACK" = true ]; then
    rollback
else
    update
fi
