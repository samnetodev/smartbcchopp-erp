#!/bin/bash
set -euo pipefail

#=============================================================================
# SmartBcChopp ERP — Production Setup Script
#=============================================================================
# This script sets up a fresh production server with Docker and the application.
# It installs Docker, clones the repository, configures environment variables,
# obtains SSL certificates, and starts all services.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/yourorg/smartbcchopp/main/scripts/setup.sh | bash
#
# Or locally:
#   ./scripts/setup.sh
#
# Requirements: Ubuntu 22.04+, root or sudo access
#=============================================================================

REPO_URL="https://github.com/yourorg/smartbcchopp.git"
BRANCH="main"
APP_DIR="/opt/smartbcchopp"
DOMAIN="${DOMAIN:-}"
EMAIL="${EMAIL:-admin@example.com}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        log_error "This script must be run as root. Use: sudo $0"
        exit 1
    fi
}

install_docker() {
    log_info "Installing Docker and Docker Compose..."

    if ! command -v docker &>/dev/null; then
        curl -fsSL https://get.docker.com | bash
        systemctl enable docker
        systemctl start docker
        log_info "Docker installed successfully."
    else
        log_info "Docker already installed. Skipping."
    fi

    if ! command -v docker compose &>/dev/null; then
        log_warn "Docker Compose plugin not found. Installing..."
        apt-get update
        apt-get install -y docker-compose-plugin
    fi

    log_info "Docker version: $(docker --version)"
    log_info "Docker Compose version: $(docker compose version)"
}

clone_repo() {
    if [ -d "$APP_DIR" ]; then
        log_info "Application directory exists. Updating..."
        cd "$APP_DIR"
        git fetch origin
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
    else
        log_info "Cloning repository..."
        git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$APP_DIR"
        cd "$APP_DIR"
    fi
}

configure_environment() {
    log_info "Configuring environment..."

    if [ ! -f "$APP_DIR/.env" ]; then
        cp "$APP_DIR/.env.example" "$APP_DIR/.env"

        # Generate secure random values
        SECRET_KEY=$(openssl rand -hex 32)
        JWT_SECRET_KEY=$(openssl rand -hex 32)
        DB_PASSWORD=$(openssl rand -base64 24)

        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" "$APP_DIR/.env"
        sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" "$APP_DIR/.env"
        sed -i "s/DEBUG=.*/DEBUG=false/" "$APP_DIR/.env"

        # Database settings — compose will use these
        export POSTGRES_PASSWORD="$DB_PASSWORD"
        export POSTGRES_USER="smartbcchopp"
        export POSTGRES_DB="smartbcchopp"

        log_info "Environment configured. Secrets generated."
        log_warn "IMPORTANT: Review $APP_DIR/.env and update API keys."
    else
        log_info "Environment file already exists. Skipping."
    fi
}

setup_ssl() {
    if [ -z "$DOMAIN" ]; then
        log_warn "No DOMAIN specified. SSL setup skipped."
        log_warn "Set DOMAIN env var and run: docker compose -f docker/docker-compose.yml run --rm certbot"
        return
    fi

    log_info "Setting up SSL for $DOMAIN..."

    # Start nginx temporarily for certbot challenge
    docker compose -f "$APP_DIR/docker/docker-compose.yml" up -d nginx

    docker compose -f "$APP_DIR/docker/docker-compose.yml" run --rm certbot \
        certonly --webroot -w /var/www/certbot \
        -d "$DOMAIN" \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive

    # Reload nginx to pick up certificates
    docker compose -f "$APP_DIR/docker/docker-compose.yml" exec nginx nginx -s reload

    log_info "SSL certificate obtained for $DOMAIN."
}

start_services() {
    log_info "Starting all services..."
    cd "$APP_DIR"
    docker compose -f docker/docker-compose.yml up -d --build
    log_info "Services started. Waiting for health checks..."

    # Wait for API to be healthy
    for i in $(seq 1 30); do
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            log_info "API is healthy!"
            break
        fi
        if [ "$i" -eq 30 ]; then
            log_error "API failed to start. Check logs: docker compose logs api"
            exit 1
        fi
        sleep 2
    done

    log_info "All services running!"
}

setup_cron() {
    log_info "Setting up automated database backup (daily at 03:00)..."

    cat >/etc/cron.d/smartbcchopp-backup <<EOF
0 3 * * * root cd $APP_DIR && docker compose -f docker/docker-compose.yml exec -T postgres /backup/backup.sh >> /var/log/smartbcchopp-backup.log 2>&1
EOF

    chmod 644 /etc/cron.d/smartbcchopp-backup
    log_info "Cron job installed."
}

print_summary() {
    echo ""
    echo "============================================================================="
    echo -e "${GREEN}  SmartBcChopp ERP — Setup Complete${NC}"
    echo "============================================================================="
    echo ""
    echo "  Application:  $APP_DIR"
    echo "  Domain:       ${DOMAIN:-Not configured}"
    echo ""
    echo "  Services:"
    echo "    - Nginx (Web):   http://localhost:80 / https://${DOMAIN:-?}"
    echo "    - API:           http://localhost:8000"
    echo "    - PostgreSQL:    localhost:5432"
    echo "    - Redis:         localhost:6379"
    echo ""
    echo "  Useful commands:"
    echo "    docker compose -f $APP_DIR/docker/docker-compose.yml ps"
    echo "    docker compose -f $APP_DIR/docker/docker-compose.yml logs -f api"
    echo "    docker compose -f $APP_DIR/docker/docker-compose.yml logs -f nginx"
    echo "    $APP_DIR/scripts/update.sh"
    echo ""
    echo "  Backup:"
    echo "    Manual:  docker compose exec postgres /backup/backup.sh"
    echo "    Restore: docker compose exec postgres /backup/restore.sh <file>"
    echo ""
    echo "  Documentation: $APP_DIR/README.md"
    echo "============================================================================="
}

#=============================================================================
# Main
#=============================================================================

check_root

echo ""
echo "============================================================================="
echo "  SmartBcChopp ERP — Production Setup"
echo "============================================================================="
echo ""

install_docker
clone_repo
configure_environment
setup_ssl
start_services
setup_cron
print_summary
