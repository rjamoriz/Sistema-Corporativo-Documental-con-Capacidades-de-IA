# 🔧 Guía de Administrador - Sistema FinancIA DMS

## Manual Técnico para Administradores del Sistema

Esta guía está diseñada para administradores del sistema y equipos de IT responsables del deployment, configuración y mantenimiento.

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación y Deployment](#instalación-y-deployment)
3. [Configuración](#configuración)
4. [Gestión de Usuarios](#gestión-de-usuarios)
5. [Monitoreo y Métricas](#monitoreo-y-métricas)
6. [Mantenimiento](#mantenimiento)
7. [Backup y Recuperación](#backup-y-recuperación)
8. [Seguridad](#seguridad)
9. [Troubleshooting Avanzado](#troubleshooting-avanzado)
10. [Optimización de Performance](#optimización-de-performance)

---

## 💻 Requisitos del Sistema

### Servidor Backend

**Mínimo (Desarrollo/Testing):**
- CPU: 4 cores
- RAM: 8 GB
- Disco: 100 GB SSD
- OS: Ubuntu 20.04+ / RHEL 8+

**Recomendado (Producción):**
- CPU: 8+ cores
- RAM: 16+ GB
- Disco: 500 GB SSD (NVMe preferido)
- OS: Ubuntu 22.04 LTS / RHEL 9

### Servidor Frontend

**Mínimo:**
- CPU: 2 cores
- RAM: 4 GB
- Disco: 50 GB SSD

**Recomendado:**
- CPU: 4 cores
- RAM: 8 GB
- Disco: 100 GB SSD

### Base de Datos PostgreSQL

**Mínimo:**
- PostgreSQL 14+
- CPU: 4 cores
- RAM: 8 GB
- Disco: 200 GB SSD

**Recomendado:**
- PostgreSQL 15+
- CPU: 8+ cores
- RAM: 32+ GB
- Disco: 1 TB SSD (con RAID 10)

### Servicios Adicionales

| Servicio | Versión Mínima | RAM | Disco |
|----------|---------------|-----|-------|
| **Redis** | 6.0+ | 4 GB | 20 GB |
| **OpenSearch** | 2.0+ | 8 GB | 200 GB |
| **MinIO** | Latest | 4 GB | 1+ TB |
| **Kafka** | 3.0+ | 8 GB | 100 GB |

### Red

- Ancho de banda: 1 Gbps mínimo
- Latencia interna: < 1 ms
- Conexión a Internet: 100 Mbps dedicado
- Puertos requeridos:
  - 80, 443 (HTTP/HTTPS)
  - 5432 (PostgreSQL)
  - 6379 (Redis)
  - 9200 (OpenSearch)
  - 9000, 9001 (MinIO)
  - 9092 (Kafka)

---

## 🚀 Instalación y Deployment

### Opción 1: Docker Compose (Recomendado para Testing)

#### 1. Clonar Repositorio

```bash
git clone https://github.com/your-org/financia-dms.git
cd financia-dms
```

#### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
nano .env
```

**Variables críticas:**

```bash
# Base de datos
DATABASE_URL=postgresql://user:password@postgres:5432/financia_dms
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://redis:6379/0

# MinIO (Almacenamiento)
MINIO_HOST=minio
MINIO_PORT=9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=documents

# OpenSearch
OPENSEARCH_HOST=opensearch
OPENSEARCH_PORT=9200

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# SMTP (Email)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@your-domain.com
SMTP_PASSWORD=your_password

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK

# Security
SECRET_KEY=generate-random-64-char-string
JWT_SECRET_KEY=generate-another-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
OFAC_API_KEY=your_ofac_api_key
EU_SANCTIONS_API_KEY=your_eu_api_key
```

#### 3. Levantar Servicios

```bash
docker-compose up -d
```

#### 4. Verificar Estado

```bash
docker-compose ps
docker-compose logs -f backend
```

#### 5. Inicializar Base de Datos

```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/init_db.py
```

---

### Opción 2: Kubernetes (Producción)

#### 1. Preparar Cluster

```bash
kubectl create namespace financia-dms
kubectl config set-context --current --namespace=financia-dms
```

#### 2. Configurar Secrets

```bash
kubectl create secret generic db-credentials \
  --from-literal=username=postgres \
  --from-literal=password=your_secure_password

kubectl create secret generic api-keys \
  --from-literal=ofac_api_key=your_key \
  --from-literal=eu_api_key=your_key

kubectl create secret generic smtp-credentials \
  --from-literal=user=alerts@domain.com \
  --from-literal=password=your_password
```

#### 3. Aplicar Manifests

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgresql.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/minio.yaml
kubectl apply -f k8s/opensearch.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/workers.yaml
kubectl apply -f k8s/ingress.yaml
```

#### 4. Verificar Deployment

```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

#### 5. Aplicar Migraciones

```bash
kubectl exec -it deployment/backend -- alembic upgrade head
```

---

## ⚙️ Configuración

### Configuración de Backend

Archivo: `backend/core/config.py`

```python
class Settings(BaseSettings):
    # Application
    APP_NAME: str = "FinancIA DMS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: list = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        # ... más tipos
    ]
    
    # Workers
    WORKER_CONCURRENCY: int = 4
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json o text
```

### Configuración de Validación

Archivo: `backend/middleware/validation_middleware.py`

```python
validation_rules = {
    "contracts": {
        "sanctions": True,
        "business_registry": True,
        "esg": True,
        "auto_alert": True,
        "priority_threshold": 0.85
    },
    "invoices": {
        "sanctions": True,
        "business_registry": True,
        "esg": False,
        "auto_alert": True,
        "priority_threshold": 0.90
    },
    # ... más reglas
}
```

**Personalizar reglas:**

1. Editar `validation_rules` según necesidades
2. Ajustar `priority_threshold` (0.0 - 1.0)
3. Reiniciar backend: `systemctl restart financia-backend`

### Configuración de Scheduler

Archivo: `backend/schedulers/validation_scheduler.py`

```python
# Sincronización de listas (daily 2 AM)
scheduler.add_job(
    sync_sanctions_lists,
    trigger=CronTrigger(hour=2, minute=0),
    id='sync_sanctions',
    replace_existing=True
)

# Resumen diario (daily 8 AM)
scheduler.add_job(
    send_daily_summary,
    trigger=CronTrigger(hour=8, minute=0),
    id='daily_summary',
    replace_existing=True
)
```

**Modificar horarios:**

```python
# Cambiar a 3 AM
trigger=CronTrigger(hour=3, minute=0)

# Cada 6 horas
trigger=CronTrigger(hour='*/6')

# Lunes a viernes 9 AM
trigger=CronTrigger(day_of_week='mon-fri', hour=9, minute=0)
```

### Configuración de Frontend

Archivo: `frontend/.env.production`

```bash
VITE_API_URL=https://api.your-domain.com
VITE_WS_URL=wss://api.your-domain.com/ws
VITE_APP_NAME=FinancIA DMS
VITE_APP_VERSION=1.0.0

# Features
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_CHAT=true
VITE_MAX_UPLOAD_SIZE=52428800  # 50MB in bytes

# Monitoring
VITE_SENTRY_DSN=your_sentry_dsn
VITE_GA_TRACKING_ID=your_ga_id
```

---

## 👥 Gestión de Usuarios

### Crear Usuario Admin

```bash
# Via CLI
docker-compose exec backend python scripts/create_admin.py \
  --email admin@company.com \
  --password SecurePass123! \
  --name "Admin User"

# Via Python
from backend.services.auth_service import create_user

await create_user(
    email="admin@company.com",
    password="SecurePass123!",
    full_name="Admin User",
    role="admin"
)
```

### Roles y Permisos

| Rol | Permisos |
|-----|----------|
| **admin** | Acceso total, gestión de usuarios, configuración |
| **manager** | Ver todo, gestión de su departamento |
| **analyst** | Ver, buscar, validar documentos |
| **user** | Subir, ver propios documentos, búsqueda limitada |
| **auditor** | Solo lectura, acceso a logs |

### Gestionar Permisos

```python
from backend.models.database_models import User, Role

# Asignar rol
user.role = Role.MANAGER
await db.commit()

# Agregar permiso específico
user.permissions.append("validate_documents")
await db.commit()

# Limitar por departamento
user.department = "Finance"
user.can_see_other_departments = False
await db.commit()
```

### Desactivar Usuario

```bash
# Soft delete (recomendado)
docker-compose exec backend python scripts/deactivate_user.py \
  --email user@company.com

# Hard delete (usar solo en desarrollo)
docker-compose exec backend python scripts/delete_user.py \
  --email user@company.com --force
```

---

## 📊 Monitoreo y Métricas

### Prometheus Metrics

**Endpoint:** `https://your-domain.com/metrics`

**Métricas principales:**

```promql
# Validaciones por segundo
rate(validation_requests_total[5m])

# Duración de validaciones (p95)
histogram_quantile(0.95, validation_duration_seconds_bucket)

# Entidades flagged
sum(entities_flagged_total)

# Llamadas a APIs externas
rate(api_calls_total[5m])

# Documentos en cola
documents_in_queue

# Conexiones a BD
db_connections_active
```

### Configurar Grafana

1. **Agregar Data Source:**
   - Type: Prometheus
   - URL: http://prometheus:9090

2. **Importar Dashboard:**
   - Dashboard ID: Usar archivo `k8s/grafana-dashboard.json`

3. **Alertas recomendadas:**

```yaml
groups:
  - name: financia_dms
    rules:
      - alert: HighValidationLatency
        expr: histogram_quantile(0.95, validation_duration_seconds_bucket) > 10
        for: 5m
        annotations:
          summary: "Validación lenta"
          
      - alert: TooManyFlaggedEntities
        expr: rate(entities_flagged_total[1h]) > 10
        for: 15m
        annotations:
          summary: "Muchas entidades flagged"
          
      - alert: APIFailureRate
        expr: rate(api_failures_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "Alta tasa de fallos en API"
```

### Health Checks

**Endpoint:** `https://your-domain.com/health`

**Respuesta:**

```json
{
  "status": "healthy",
  "timestamp": "2024-10-10T12:00:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "latency_ms": 5
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1
    },
    "opensearch": {
      "status": "healthy",
      "latency_ms": 12
    },
    "scheduler": {
      "status": "healthy",
      "next_run": "2024-10-11T02:00:00Z"
    },
    "external_apis": {
      "ofac": "healthy",
      "eu_sanctions": "healthy",
      "world_bank": "degraded"
    }
  }
}
```

### Logs

**Ubicación:**
- Docker: `docker-compose logs -f backend`
- Kubernetes: `kubectl logs -f deployment/backend`
- Filesystem: `/var/log/financia-dms/`

**Formato JSON:**

```json
{
  "timestamp": "2024-10-10T12:00:00.123Z",
  "level": "INFO",
  "logger": "backend.services.validation",
  "message": "Validation completed",
  "request_id": "abc123",
  "user_id": "user_456",
  "document_id": "doc_789",
  "duration_ms": 523,
  "entities_checked": 5,
  "flagged": 1
}
```

**Consultar logs:**

```bash
# Últimas 100 líneas
tail -n 100 /var/log/financia-dms/backend.log

# Filtrar por nivel ERROR
jq 'select(.level == "ERROR")' /var/log/financia-dms/backend.log

# Filtrar por usuario
jq 'select(.user_id == "user_456")' /var/log/financia-dms/backend.log

# Queries lentas
jq 'select(.duration_ms > 1000)' /var/log/financia-dms/backend.log
```

---

## 🔧 Mantenimiento

### Tareas Diarias

**Automatizadas:**
- ✅ Sincronización de listas de sanciones (2 AM)
- ✅ Resumen diario por email (8 AM)
- ✅ Limpieza de caché antiguo (3 AM)
- ✅ Validación de documentos pendientes (cada 30 min)

**Manuales:**
- Revisar dashboard de métricas
- Verificar alertas en Grafana
- Revisar logs de errores

### Tareas Semanales

```bash
# 1. Análisis de índices de BD
docker-compose exec postgres psql -U postgres -d financia_dms -c "
SELECT schemaname, tablename, idx_scan, idx_tup_read 
FROM pg_stat_user_indexes 
WHERE idx_scan = 0 
ORDER BY idx_tup_read DESC;
"

# 2. Vacuum de tablas
docker-compose exec postgres psql -U postgres -d financia_dms -c "
VACUUM ANALYZE validation_results;
VACUUM ANALYZE sanctions_list;
VACUUM ANALYZE documents;
"

# 3. Refresh vista materializada
docker-compose exec postgres psql -U postgres -d financia_dms -c "
REFRESH MATERIALIZED VIEW CONCURRENTLY validation_stats_cache;
"

# 4. Limpieza de logs antiguos
find /var/log/financia-dms/ -name "*.log" -mtime +30 -delete

# 5. Verificar espacio en disco
df -h
du -sh /var/lib/docker/
du -sh /var/lib/postgresql/
```

### Tareas Mensuales

```bash
# 1. Backup completo (ver sección Backup)

# 2. Actualización de dependencias
docker-compose exec backend pip list --outdated
docker-compose exec frontend npm outdated

# 3. Análisis de seguridad
docker scan financia-backend:latest
docker scan financia-frontend:latest

# 4. Revisar certificados SSL
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates

# 5. Auditoría de usuarios
docker-compose exec backend python scripts/audit_users.py --inactive-days 90
```

---

## 💾 Backup y Recuperación

### Backup de PostgreSQL

**Script automático:**

```bash
#!/bin/bash
# /scripts/backup_db.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="financia_dms"

# Full backup
docker-compose exec -T postgres pg_dump -U postgres $DB_NAME | \
  gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"

# Verificar
if [ $? -eq 0 ]; then
  echo "✅ Backup exitoso: backup_$DATE.sql.gz"
  
  # Eliminar backups > 30 días
  find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
else
  echo "❌ Backup falló"
  exit 1
fi
```

**Cron job:**

```bash
# Backup diario a las 1 AM
0 1 * * * /scripts/backup_db.sh >> /var/log/backups.log 2>&1
```

**Restaurar backup:**

```bash
# 1. Detener aplicación
docker-compose stop backend workers

# 2. Restaurar
gunzip < /backups/postgres/backup_20241010_010000.sql.gz | \
  docker-compose exec -T postgres psql -U postgres financia_dms

# 3. Reiniciar
docker-compose start backend workers
```

### Backup de MinIO (Documentos)

```bash
#!/bin/bash
# /scripts/backup_minio.sh

BACKUP_DIR="/backups/minio"
DATE=$(date +%Y%m%d_%H%M%S)

# Usar MinIO Client (mc)
mc mirror minio/documents "$BACKUP_DIR/$DATE/"

# Comprimir
tar -czf "$BACKUP_DIR/documents_$DATE.tar.gz" "$BACKUP_DIR/$DATE/"
rm -rf "$BACKUP_DIR/$DATE/"

echo "✅ Backup MinIO: documents_$DATE.tar.gz"
```

### Backup de OpenSearch (Índices)

```bash
# Crear snapshot repository
curl -X PUT "localhost:9200/_snapshot/backup_repo" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/backups/opensearch"
  }
}'

# Crear snapshot
curl -X PUT "localhost:9200/_snapshot/backup_repo/snapshot_$(date +%Y%m%d)?wait_for_completion=true"
```

### Disaster Recovery Plan

**RTO (Recovery Time Objective):** 4 horas
**RPO (Recovery Point Objective):** 24 horas

**Procedimiento:**

1. **Servidor caído:**
   ```bash
   # Levantar servidor de respaldo
   ssh backup-server
   docker-compose up -d
   
   # Cambiar DNS
   # A record: your-domain.com → backup-server-ip
   ```

2. **Base de datos corrupta:**
   ```bash
   # Restaurar último backup
   ./scripts/restore_db.sh /backups/postgres/backup_latest.sql.gz
   ```

3. **Pérdida de datos:**
   ```bash
   # Restaurar desde backup
   ./scripts/restore_full.sh --date 20241010
   ```

---

## 🔒 Seguridad

### SSL/TLS

**Configurar certificado (Let's Encrypt):**

```bash
# Instalar certbot
apt-get install certbot python3-certbot-nginx

# Obtener certificado
certbot --nginx -d your-domain.com -d api.your-domain.com

# Auto-renewal
echo "0 3 * * * certbot renew --quiet" | crontab -
```

### Firewall

```bash
# UFW (Ubuntu)
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw enable

# iptables (alternativa)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP
```

### Rate Limiting

**Nginx config:**

```nginx
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
        }
    }
}
```

### Auditoría

**Habilitar audit logging:**

```python
# backend/core/config.py
AUDIT_LOGGING_ENABLED = True
AUDIT_LOG_FILE = "/var/log/financia-dms/audit.log"
```

**Eventos auditados:**
- Login/logout
- Creación/eliminación de usuarios
- Subida/descarga/eliminación de documentos
- Cambios de configuración
- Acceso a datos sensibles
- Validaciones flagged

**Consultar logs de auditoría:**

```bash
# Accesos de un usuario
jq 'select(.user_id == "user_123")' /var/log/financia-dms/audit.log

# Eliminaciones
jq 'select(.action == "delete")' /var/log/financia-dms/audit.log

# Accesos fallidos
jq 'select(.status == "failed")' /var/log/financia-dms/audit.log
```

---

## 🔍 Troubleshooting Avanzado

### Alta Latencia en Validaciones

**Síntomas:**
- Validaciones > 10 segundos
- Timeout en APIs externas

**Diagnóstico:**

```bash
# 1. Verificar métricas
curl http://localhost:9090/metrics | grep validation_duration

# 2. Ver queries lentas en BD
docker-compose exec postgres psql -U postgres -d financia_dms -c "
SELECT pid, now() - query_start as duration, query 
FROM pg_stat_activity 
WHERE state = 'active' AND now() - query_start > interval '5 seconds';
"

# 3. Verificar APIs externas
curl -w "@curl-format.txt" https://api.ofac.treasury.gov/health
```

**Soluciones:**

1. Agregar índices adicionales
2. Aumentar connection pool: `DB_POOL_SIZE=40`
3. Habilitar cache más agresivo
4. Escalar workers: `docker-compose scale workers=4`

### Memoria Alta en Backend

**Síntomas:**
- OOM (Out of Memory)
- Swap usage alto

**Diagnóstico:**

```bash
# Ver uso de memoria
docker stats backend

# Ver procesos Python
docker-compose exec backend ps aux | grep python

# Memory profiling
docker-compose exec backend python -m memory_profiler app.py
```

**Soluciones:**

```yaml
# docker-compose.yml
services:
  backend:
    mem_limit: 4g
    mem_reservation: 2g
```

### Disco Lleno

**Síntomas:**
- `No space left on device`
- Writes fallan

**Diagnóstico:**

```bash
# Ver uso
df -h
du -sh /var/lib/docker/*
du -sh /var/lib/postgresql/*

# Archivos grandes
find / -type f -size +1G -exec ls -lh {} \;
```

**Soluciones:**

```bash
# 1. Limpiar logs antiguos
find /var/log -name "*.log" -mtime +30 -delete

# 2. Limpiar Docker
docker system prune -a --volumes

# 3. Limpiar MinIO
# Eliminar documentos > 5 años (según política)

# 4. Archivar backups antiguos
mv /backups/old/* /archive/
```

---

## ⚡ Optimización de Performance

### Database Tuning

**postgresql.conf:**

```ini
# Connections
max_connections = 200
superuser_reserved_connections = 3

# Memory
shared_buffers = 8GB            # 25% of RAM
effective_cache_size = 24GB     # 75% of RAM
work_mem = 64MB
maintenance_work_mem = 2GB

# Checkpoints
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Query Planning
random_page_cost = 1.1          # Para SSD
effective_io_concurrency = 200  # Para SSD

# Autovacuum (agresivo)
autovacuum_max_workers = 4
autovacuum_naptime = 30s
```

**Aplicar:**

```bash
docker-compose restart postgres
```

### Redis Optimization

**redis.conf:**

```ini
maxmemory 4gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Application-Level Caching

```python
from backend.core.db_performance import query_cache

@app.get("/api/stats")
async def get_stats():
    cache_key = "dashboard_stats"
    
    # Intentar desde cache
    cached = query_cache.get(cache_key)
    if cached:
        return cached
    
    # Calcular
    stats = await calculate_stats()
    
    # Guardar en cache (5 min)
    query_cache.set(cache_key, stats)
    
    return stats
```

### Frontend Optimization

```typescript
// Lazy loading
const Dashboard = lazy(() => import('./Dashboard'));

// Code splitting
import(/* webpackChunkName: "charts" */ './Charts');

// Memoization
const MemoizedTable = React.memo(DataTable);

// Virtual scrolling para listas grandes
import { FixedSizeList } from 'react-window';
```

---

## 📞 Soporte y Escalamiento

### Niveles de Severidad

| Nivel | Descripción | SLA | Ejemplo |
|-------|-------------|-----|---------|
| **P1 - Crítico** | Sistema caído | 1 hora | Base de datos no responde |
| **P2 - Alto** | Funcionalidad crítica afectada | 4 horas | Validaciones no funcionan |
| **P3 - Medio** | Funcionalidad menor afectada | 1 día | Dashboard lento |
| **P4 - Bajo** | Mejora o pregunta | 1 semana | Nueva feature request |

### Contactos de Escalamiento

1. **Nivel 1 - Soporte:** soporte@financia-dms.com
2. **Nivel 2 - DevOps:** devops@financia-dms.com
3. **Nivel 3 - Arquitectos:** arquitectos@financia-dms.com
4. **Nivel 4 - CTO:** cto@financia-dms.com

### On-Call Rotation

```
Semana 1: DevOps Team A
Semana 2: DevOps Team B
Semana 3: Backend Team
Semana 4: Full Stack Team
```

---

## 📚 Recursos Adicionales

- **Documentación de API:** https://api.your-domain.com/docs
- **Repositorio GitHub:** https://github.com/your-org/financia-dms
- **Wiki Interno:** https://wiki.your-org.com/financia-dms
- **Runbook:** https://docs.your-org.com/runbooks/financia-dms

---

## 🔄 Changelog

### v1.0.0 (Oct 2024)
- ✨ Sistema de validación automática
- ✨ Dashboard en tiempo real
- ✨ Métricas Prometheus
- ✨ Structured logging
- ✨ Optimizaciones de performance
- 🐛 Fixes varios de producción

---

*Para actualizaciones de esta guía: docs@financia-dms.com*
