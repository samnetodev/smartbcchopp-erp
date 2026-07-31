#!/bin/bash
set -euo pipefail

#=============================================================================
# SmartBcChopp ERP — Deploy Script (CI/CD)
#=============================================================================
# This script is called by GitHub Actions to deploy to production.
# It connects via SSH and runs the update script on the server.
#
# Usage:
#   ./scripts/deploy.sh <environment>
#
# Environment:
#   The script reads config from .deploy/<environment>.env
#   e.g., .deploy/production.env
#=============================================================================

ENV="${1:-}"
if [ -z "$ENV" ]; then
    echo "Usage: $0 <environment>"
    echo "Environments: production, staging"
    exit 1
fi

CONFIG_FILE=".deploy/${ENV}.env"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: $CONFIG_FILE not found."
    echo "Create it with:"
    echo "  DEPLOY_HOST=<server-ip>"
    echo "  DEPLOY_USER=<ssh-user>"
    echo "  DEPLOY_KEY=<ssh-private-key-path>"
    echo "  DEPLOY_PATH=/opt/smartbcchopp"
    exit 1
fi

source "$CONFIG_FILE"

echo "=== Deploying to $ENV ==="
echo "Host: $DEPLOY_HOST"
echo "Path: $DEPLOY_PATH"

# Run update on remote server
ssh -i "${DEPLOY_KEY:-~/.ssh/id_rsa}" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "${DEPLOY_USER}@${DEPLOY_HOST}" \
    "cd $DEPLOY_PATH && git fetch origin && git reset --hard origin/main && docker compose -f docker/docker-compose.yml up -d --build"

echo "=== Deploy completed ==="
