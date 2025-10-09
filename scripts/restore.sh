#!/bin/bash
# FinancIA 2030 - Restore Script
# Restores data from a backup

set -e

if [ -z "$1" ]; then
    echo "❌ Error: Please provide backup directory path"
    echo "Usage: ./restore.sh <backup_directory>"
    echo ""
    echo "Available backups:"
    ls -1d ./backups/*/ 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_DIR="$1"
SCRIPT_DIR="$(dirname "$0")"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Error: Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "🔄 Restoring from backup: $BACKUP_DIR"
echo ""

# Verify backup contents
if [ ! -f "$BACKUP_DIR/postgres_backup.sql.gz" ]; then
    echo "❌ Error: PostgreSQL backup not found"
    exit 1
fi

# Navigate to docker directory
cd "$SCRIPT_DIR/../infrastructure/docker"

# Stop services
echo "🛑 Stopping services..."
docker-compose down

# Start only database services
echo "🚀 Starting database services..."
docker-compose up -d postgres minio

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
sleep 10
until docker-compose exec -T postgres pg_isready -U financia_user > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

# Restore PostgreSQL
echo "📊 Restoring PostgreSQL database..."
gunzip -c "$BACKUP_DIR/postgres_backup.sql.gz" | docker-compose exec -T postgres psql -U financia_user financia_db

# Wait for MinIO
echo "⏳ Waiting for MinIO..."
sleep 5

# Restore MinIO data
echo "📦 Restoring MinIO data..."
if [ -d "$BACKUP_DIR/minio_backup" ]; then
    docker-compose exec -T minio mc alias set local http://localhost:9000 minioadmin minioadmin
    docker-compose exec -T minio mc mirror "$BACKUP_DIR/minio_backup" local/financia-documents
fi

# Restore logs
echo "📝 Restoring logs..."
if [ -d "$BACKUP_DIR/logs" ]; then
    cp -r "$BACKUP_DIR/logs" "$SCRIPT_DIR/../backend/logs"
fi

# Start remaining services
echo "🚀 Starting remaining services..."
docker-compose up -d

echo ""
echo "✅ Restore completed successfully"
echo "ℹ️  Services are starting. Use ./start.sh to verify health checks"
