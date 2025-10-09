#!/bin/bash
# FinancIA 2030 - Stop Script
# Stops all services

set -e

echo "🛑 Stopping FinancIA 2030 services..."

# Navigate to docker directory
cd "$(dirname "$0")/../infrastructure/docker"

# Stop services
docker-compose down

echo "✅ All services stopped"
echo ""
echo "ℹ️  Data volumes are preserved"
echo "To remove volumes as well, run: docker-compose down -v"
