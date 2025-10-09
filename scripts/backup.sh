#!/bin/bash
# FinancIA 2030 - Backup Script
# Creates backups of PostgreSQL, MinIO, and logs

set -e

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
SCRIPT_DIR="$(dirname "$0")"

echo "💾 Creating backup in $BACKUP_DIR..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Navigate to docker directory
cd "$SCRIPT_DIR/../infrastructure/docker"

# Backup PostgreSQL
echo "📊 Backing up PostgreSQL database..."
docker-compose exec -T postgres pg_dump -U financia_user financia_db | gzip > "$BACKUP_DIR/postgres_backup.sql.gz"

# Backup MinIO data
echo "📦 Backing up MinIO data..."
docker-compose exec -T minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker-compose exec -T minio mc mirror local/financia-documents "$BACKUP_DIR/minio_backup"

# Backup logs
echo "📝 Backing up logs..."
if [ -d "$SCRIPT_DIR/../backend/logs" ]; then
    cp -r "$SCRIPT_DIR/../backend/logs" "$BACKUP_DIR/logs"
fi

# Create metadata file
cat > "$BACKUP_DIR/backup_metadata.json" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "docker_images": $(docker-compose ps --format json | jq -s '[.[] | {name: .Name, image: .Image, status: .Status}]'),
  "backup_size": "$(du -sh "$BACKUP_DIR" | cut -f1)"
}
EOF

echo "✅ Backup completed successfully"
echo "📂 Backup location: $BACKUP_DIR"
echo "💿 Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"
