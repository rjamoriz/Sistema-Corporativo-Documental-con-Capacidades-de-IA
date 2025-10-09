#!/bin/bash
# FinancIA 2030 - Start Script
# Starts all services with Docker Compose

set -e

echo "🚀 Starting FinancIA 2030 services..."

# Navigate to docker directory
cd "$(dirname "$0")/../infrastructure/docker"

# Start services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until docker-compose exec -T postgresql pg_isready -U financia -d financia_db > /dev/null 2>&1; do
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Wait for OpenSearch
echo "Waiting for OpenSearch..."
until curl -s -f http://localhost:9200/_cluster/health > /dev/null 2>&1; do
    sleep 2
done
echo "✅ OpenSearch is ready"

# Wait for Redis
echo "Waiting for Redis..."
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    sleep 1
done
echo "✅ Redis is ready"

# Wait for Kafka
echo "Waiting for Kafka..."
sleep 15
echo "✅ Kafka should be ready"

# Wait for MinIO
echo "Waiting for MinIO..."
until curl -s -f http://localhost:9000/minio/health/live > /dev/null 2>&1; do
    sleep 2
done
echo "✅ MinIO is ready"

echo ""
echo "✅ All services are running!"
echo ""
echo "📍 Access points:"
echo "   - API Docs (Swagger):        http://localhost:8000/docs"
echo "   - API Docs (ReDoc):          http://localhost:8000/redoc"
echo "   - OpenSearch Dashboards:     http://localhost:5601"
echo "   - MinIO Console:             http://localhost:9001"
echo "   - Grafana:                   http://localhost:3001 (admin/admin)"
echo "   - Prometheus:                http://localhost:9090"
echo "   - MLflow:                    http://localhost:5000"
echo ""
echo "📋 View logs:"
echo "   docker-compose logs -f [service_name]"
echo ""
echo "🛑 Stop services:"
echo "   ./scripts/stop.sh"
