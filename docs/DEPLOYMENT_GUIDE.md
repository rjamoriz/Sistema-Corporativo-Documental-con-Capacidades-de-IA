# 🚀 Deployment Guide - FinancIA DMS
## Guía Completa de Despliegue del Sistema de Validación

---

## 📋 Índice

1. [Requisitos Previos](#requisitos-previos)
2. [Opción 1: Docker Compose](#opción-1-docker-compose)
3. [Opción 2: Kubernetes](#opción-2-kubernetes)
4. [Variables de Entorno](#variables-de-entorno)
5. [Configuración de Base de Datos](#configuración-de-base-de-datos)
6. [Configuración de APIs Externas](#configuración-de-apis-externas)
7. [SSL/TLS y Seguridad](#ssltls-y-seguridad)
8. [Monitoreo y Logs](#monitoreo-y-logs)
9. [Backup y Restore](#backup-y-restore)
10. [Troubleshooting](#troubleshooting)
11. [Checklist de Go-Live](#checklist-de-go-live)

---

## 📦 Requisitos Previos

### Hardware Mínimo

**Desarrollo/Testing:**
- CPU: 4 cores
- RAM: 16 GB
- Disco: 50 GB SSD
- Red: 100 Mbps

**Producción:**
- CPU: 8 cores (16 recomendado)
- RAM: 32 GB (64 GB recomendado)
- Disco: 500 GB SSD (RAID 10 recomendado)
- Red: 1 Gbps

### Software Requerido

| Software | Versión Mínima | Notas |
|----------|----------------|-------|
| Docker | 24.0+ | Con compose plugin |
| Docker Compose | 2.20+ | Incluido en Docker Desktop |
| Kubernetes | 1.27+ | Solo para opción K8s |
| kubectl | 1.27+ | Solo para opción K8s |
| Git | 2.30+ | Para clonar repositorio |
| OpenSSL | 1.1.1+ | Para generación de certificados |

### Cuentas y Credenciales

- [ ] API Key de OpenAI (o Anthropic/Llama)
- [ ] Credenciales SMTP para emails
- [ ] Webhook de Slack (opcional)
- [ ] Cuenta de Twilio para SMS (opcional)
- [ ] Acceso a APIs de sanciones (OFAC, EU, World Bank)

---

## 🐳 Opción 1: Docker Compose

### Paso 1: Clonar Repositorio

```bash
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA
```

### Paso 2: Configurar Variables de Entorno

```bash
# Crear archivo .env desde el template
cp infrastructure/docker/.env.example infrastructure/docker/.env

# Editar con tus credenciales
nano infrastructure/docker/.env
```

**Variables críticas a configurar:**
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# PostgreSQL
POSTGRES_PASSWORD=your_secure_password_here

# JWT Secret (generar con: openssl rand -hex 32)
JWT_SECRET_KEY=your_jwt_secret_key_here

# SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Slack (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# APIs de Sanciones
OFAC_API_KEY=your_ofac_api_key
EU_SANCTIONS_API_KEY=your_eu_api_key
WORLD_BANK_API_KEY=your_worldbank_api_key
```

### Paso 3: Generar Certificados SSL (Producción)

```bash
# Crear directorio para certificados
mkdir -p infrastructure/docker/certs

# Generar certificado autofirmado (desarrollo)
openssl req -x509 -newkey rsa:4096 \
  -keyout infrastructure/docker/certs/key.pem \
  -out infrastructure/docker/certs/cert.pem \
  -days 365 -nodes \
  -subj "/C=ES/ST=Madrid/L=Madrid/O=FinancIA/CN=financia.local"

# Para producción, usar certificados de Let's Encrypt o CA corporativa
```

### Paso 4: Iniciar Servicios

```bash
cd infrastructure/docker

# Iniciar todos los servicios
docker-compose up -d

# Verificar que todos los servicios estén running
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f backend
```

**Orden de inicio recomendado:**
1. PostgreSQL
2. Redis
3. Kafka + Zookeeper
4. MinIO
5. OpenSearch
6. Backend
7. Frontend
8. Workers
9. Prometheus + Grafana

### Paso 5: Ejecutar Migraciones

```bash
# Conectar al contenedor backend
docker-compose exec backend bash

# Ejecutar migraciones Alembic
alembic upgrade head

# Verificar migraciones
alembic current

# Salir del contenedor
exit
```

### Paso 6: Cargar Datos Iniciales

```bash
# Cargar datos de demo (opcional)
docker-compose exec -T postgres psql -U postgres -d financia_dms < scripts/demo_data.sql

# Crear usuario administrador
docker-compose exec backend python -c "
from backend.core.security import get_password_hash
from backend.models.user import User
from backend.core.database import SessionLocal

db = SessionLocal()
admin = User(
    email='admin@financia.com',
    password_hash=get_password_hash('Admin123!'),
    full_name='Administrator',
    role='admin',
    department='IT'
)
db.add(admin)
db.commit()
print('✅ Admin user created')
"
```

### Paso 7: Verificar Despliegue

```bash
# Health check de servicios
curl http://localhost:8000/health
curl http://localhost:3000/

# Verificar Prometheus
curl http://localhost:9090/-/healthy

# Verificar Grafana
curl http://localhost:3001/api/health

# Verificar Phoenix (observabilidad)
curl http://localhost:6006/health
```

**URLs de acceso:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090
- Phoenix: http://localhost:6006

### Paso 8: Configurar Backups Automáticos

```bash
# Agregar cron job para backups diarios
crontab -e

# Agregar línea (backup a las 2 AM)
0 2 * * * /path/to/scripts/backup.sh >> /var/log/financia-backup.log 2>&1
```

---

## ☸️ Opción 2: Kubernetes

### Paso 1: Preparar Cluster

```bash
# Verificar cluster
kubectl cluster-info
kubectl get nodes

# Crear namespace
kubectl create namespace financia-dms

# Configurar contexto
kubectl config set-context --current --namespace=financia-dms
```

### Paso 2: Crear Secrets

```bash
# Secret para PostgreSQL
kubectl create secret generic postgres-secret \
  --from-literal=password='your_secure_password' \
  --namespace=financia-dms

# Secret para API keys
kubectl create secret generic api-keys \
  --from-literal=openai-api-key='sk-...' \
  --from-literal=ofac-api-key='...' \
  --from-literal=eu-api-key='...' \
  --from-literal=worldbank-api-key='...' \
  --namespace=financia-dms

# Secret para JWT
kubectl create secret generic jwt-secret \
  --from-literal=secret-key="$(openssl rand -hex 32)" \
  --namespace=financia-dms

# Secret para SMTP
kubectl create secret generic smtp-secret \
  --from-literal=server='smtp.gmail.com' \
  --from-literal=port='587' \
  --from-literal=username='your_email@gmail.com' \
  --from-literal=password='your_app_password' \
  --namespace=financia-dms
```

### Paso 3: Crear ConfigMaps

```bash
# ConfigMap para aplicación
kubectl create configmap app-config \
  --from-literal=environment='production' \
  --from-literal=log-level='INFO' \
  --from-literal=cors-origins='https://financia.com' \
  --namespace=financia-dms
```

### Paso 4: Desplegar PersistentVolumes

```yaml
# postgres-pv.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: financia-dms
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: standard
---
# minio-pv.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: minio-pvc
  namespace: financia-dms
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Gi
  storageClassName: standard
```

```bash
kubectl apply -f postgres-pv.yaml
kubectl apply -f minio-pv.yaml
```

### Paso 5: Desplegar Base de Datos

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: financia-dms
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: pgvector/pgvector:pg15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: financia_dms
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: financia-dms
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
```

```bash
kubectl apply -f postgres-deployment.yaml
```

### Paso 6: Desplegar Backend

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: financia-dms
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: rjamoriz/financia-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://postgres:$(POSTGRES_PASSWORD)@postgres:5432/financia_dms"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-api-key
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret-key
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: environment
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 5
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: financia-dms
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

```bash
kubectl apply -f backend-deployment.yaml
```

### Paso 7: Desplegar Frontend

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: financia-dms
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: rjamoriz/financia-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: VITE_API_URL
          value: "https://api.financia.com"
        resources:
          requests:
            memory: "512Mi"
            cpu: "0.5"
          limits:
            memory: "1Gi"
            cpu: "1"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: financia-dms
spec:
  selector:
    app: frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
```

```bash
kubectl apply -f frontend-deployment.yaml
```

### Paso 8: Configurar Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: financia-ingress
  namespace: financia-dms
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/websocket-services: "backend"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - financia.com
    - api.financia.com
    secretName: financia-tls
  rules:
  - host: financia.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
  - host: api.financia.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

```bash
kubectl apply -f ingress.yaml
```

### Paso 9: Configurar Autoscaling

```yaml
# backend-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: financia-dms
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

```bash
kubectl apply -f backend-hpa.yaml
```

### Paso 10: Verificar Despliegue

```bash
# Ver todos los recursos
kubectl get all -n financia-dms

# Ver pods
kubectl get pods -n financia-dms

# Ver logs de backend
kubectl logs -f deployment/backend -n financia-dms

# Ejecutar migraciones
kubectl exec -it deployment/backend -n financia-dms -- alembic upgrade head

# Port-forward para testing local
kubectl port-forward service/frontend 3000:3000 -n financia-dms
kubectl port-forward service/backend 8000:8000 -n financia-dms
```

---

## 🔧 Variables de Entorno

### Backend

| Variable | Requerido | Default | Descripción |
|----------|-----------|---------|-------------|
| `DATABASE_URL` | ✅ | - | URL de PostgreSQL |
| `REDIS_URL` | ✅ | redis://localhost:6379 | URL de Redis |
| `KAFKA_BOOTSTRAP_SERVERS` | ✅ | localhost:9092 | Kafka brokers |
| `MINIO_ENDPOINT` | ✅ | localhost:9000 | MinIO endpoint |
| `MINIO_ACCESS_KEY` | ✅ | minioadmin | MinIO access key |
| `MINIO_SECRET_KEY` | ✅ | minioadmin | MinIO secret key |
| `OPENSEARCH_HOST` | ✅ | localhost:9200 | OpenSearch host |
| `OPENAI_API_KEY` | ✅ | - | OpenAI API key |
| `JWT_SECRET_KEY` | ✅ | - | JWT secret (32 bytes hex) |
| `JWT_ALGORITHM` | ❌ | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | 60 | Token expiration |
| `SMTP_SERVER` | ✅ | - | SMTP server |
| `SMTP_PORT` | ✅ | 587 | SMTP port |
| `SMTP_USERNAME` | ✅ | - | SMTP username |
| `SMTP_PASSWORD` | ✅ | - | SMTP password |
| `SLACK_WEBHOOK_URL` | ❌ | - | Slack webhook |
| `TWILIO_ACCOUNT_SID` | ❌ | - | Twilio SID |
| `TWILIO_AUTH_TOKEN` | ❌ | - | Twilio token |
| `OFAC_API_KEY` | ✅ | - | OFAC API key |
| `EU_SANCTIONS_API_KEY` | ✅ | - | EU Sanctions API key |
| `WORLD_BANK_API_KEY` | ✅ | - | World Bank API key |
| `LOG_LEVEL` | ❌ | INFO | Log level (DEBUG/INFO/WARNING/ERROR) |
| `ENVIRONMENT` | ❌ | development | Environment (development/staging/production) |
| `CORS_ORIGINS` | ❌ | * | CORS allowed origins |

### Frontend

| Variable | Requerido | Default | Descripción |
|----------|-----------|---------|-------------|
| `VITE_API_URL` | ✅ | http://localhost:8000 | Backend API URL |
| `VITE_WS_URL` | ✅ | ws://localhost:8000 | WebSocket URL |
| `VITE_ENVIRONMENT` | ❌ | development | Environment |

---

## 🗄️ Configuración de Base de Datos

### Optimización de PostgreSQL

**postgresql.conf:**
```ini
# Memoria
shared_buffers = 8GB                    # 25% de RAM
effective_cache_size = 24GB             # 75% de RAM
work_mem = 64MB
maintenance_work_mem = 2GB

# Conexiones
max_connections = 200

# Checkpoints
checkpoint_completion_target = 0.9
wal_buffers = 16MB

# Planner
random_page_cost = 1.1                  # Para SSD
effective_io_concurrency = 200

# Autovacuum
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 10s
```

### Índices Recomendados

Ya creados en migración `008_performance_optimizations.py`:
- GIN indexes para full-text search
- GiST indexes para trigram similarity
- B-tree indexes para queries frecuentes
- Partial indexes para casos específicos

---

## 🔌 Configuración de APIs Externas

### OFAC API

```bash
# Obtener API key en: https://ofac.treasury.gov/developer
OFAC_API_KEY=your_key_here
OFAC_API_ENDPOINT=https://api.ofac.treasury.gov/v1
```

### EU Sanctions API

```bash
# Obtener API key en: https://webgate.ec.europa.eu/
EU_SANCTIONS_API_KEY=your_key_here
EU_SANCTIONS_API_ENDPOINT=https://webgate.ec.europa.eu/fsd/fsf
```

### World Bank API

```bash
# Obtener API key en: https://data.worldbank.org/
WORLD_BANK_API_KEY=your_key_here
WORLD_BANK_API_ENDPOINT=https://api.worldbank.org/v2/debarred
```

---

## 🔒 SSL/TLS y Seguridad

### Generar Certificados Let's Encrypt

```bash
# Instalar certbot
sudo apt-get install certbot

# Obtener certificado
sudo certbot certonly --standalone \
  -d financia.com \
  -d api.financia.com \
  --email admin@financia.com \
  --agree-tos

# Certificados en:
# /etc/letsencrypt/live/financia.com/fullchain.pem
# /etc/letsencrypt/live/financia.com/privkey.pem

# Renovación automática (cron)
0 0 1 * * certbot renew --quiet
```

### Nginx con SSL

```nginx
server {
    listen 443 ssl http2;
    server_name api.financia.com;

    ssl_certificate /etc/letsencrypt/live/financia.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/financia.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 📊 Monitoreo y Logs

### Prometheus

**prometheus.yml** ya configurado en `infrastructure/docker/prometheus.yml`

Métricas expuestas:
- `/metrics` - Métricas de aplicación
- Validaciones, latencia, API calls, etc.

### Grafana Dashboards

```bash
# Acceder a Grafana
http://localhost:3001
# Usuario: admin
# Password: admin

# Importar dashboards pre-configurados:
# - FinancIA Overview
# - Validation Metrics
# - System Resources
```

### Logs Estructurados

```bash
# Ver logs en JSON
docker-compose logs backend | jq .

# Filtrar por nivel
docker-compose logs backend | jq 'select(.level=="ERROR")'

# Filtrar por request_id
docker-compose logs backend | jq 'select(.request_id=="abc123")'
```

---

## 💾 Backup y Restore

### Backup Manual

```bash
# Ejecutar script de backup
./scripts/backup.sh

# Backup generado en: /var/backups/financia/
# Incluye:
# - PostgreSQL dump
# - MinIO (documentos)
# - Logs
```

### Restore

```bash
# Restaurar desde backup
./scripts/restore.sh /var/backups/financia/backup-2024-11-01.tar.gz

# Verificar restauración
docker-compose exec backend python -c "
from backend.core.database import SessionLocal
from backend.models.document import Document
db = SessionLocal()
count = db.query(Document).count()
print(f'Documents: {count}')
"
```

---

## 🔧 Troubleshooting

### Problema: Backend no inicia

**Síntomas:**
```
backend_1  | ERROR: Cannot connect to database
backend_1  | psycopg2.OperationalError: could not connect to server
```

**Solución:**
```bash
# Verificar que PostgreSQL esté running
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs postgres

# Reiniciar PostgreSQL
docker-compose restart postgres

# Esperar 10 segundos y reiniciar backend
sleep 10
docker-compose restart backend
```

### Problema: Validaciones muy lentas

**Síntomas:**
- Validaciones tardan >10 segundos
- Timeout en APIs externas

**Solución:**
```bash
# Verificar cache hit rate
curl http://localhost:8000/metrics | grep cache_hit_rate

# Limpiar caché corrupto
docker-compose exec redis redis-cli FLUSHALL

# Verificar conexiones a APIs externas
docker-compose exec backend python -c "
import requests
print('OFAC:', requests.get('https://api.ofac.treasury.gov/v1/health').status_code)
"

# Aumentar timeout en .env
API_TIMEOUT=30
```

### Problema: Out of Memory

**Síntomas:**
```
backend_1  | Killed
```

**Solución:**
```bash
# Verificar uso de memoria
docker stats

# Aumentar límites en docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G

# Reiniciar servicios
docker-compose down
docker-compose up -d
```

### Problema: WebSocket desconexiones

**Síntomas:**
- Dashboard no actualiza en tiempo real
- WebSocket se desconecta frecuentemente

**Solución:**
```nginx
# Configurar nginx/ingress para WebSockets
location /ws/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
}
```

---

## ✅ Checklist de Go-Live

### Pre-Despliegue

- [ ] Todas las variables de entorno configuradas
- [ ] Certificados SSL generados y configurados
- [ ] Base de datos creada y migraciones ejecutadas
- [ ] Backup inicial realizado
- [ ] Usuarios administradores creados
- [ ] APIs externas probadas y funcionando
- [ ] Monitoreo (Prometheus + Grafana) configurado
- [ ] Alertas de Grafana configuradas
- [ ] Logs centralizados funcionando
- [ ] Documentación actualizada

### Testing

- [ ] Health checks de todos los servicios OK
- [ ] Login y autenticación funcionando
- [ ] Upload y procesamiento de documentos OK
- [ ] Validación contra listas de sanciones OK
- [ ] Dashboard mostrando métricas correctas
- [ ] Alertas de entidades flagged enviándose
- [ ] Búsqueda (simple y semántica) funcionando
- [ ] WebSocket updates en tiempo real OK
- [ ] Performance tests pasados (validación <3s)
- [ ] Load tests pasados (100+ usuarios concurrentes)
- [ ] Security scan completado sin vulnerabilidades críticas

### Post-Despliegue

- [ ] Monitorear logs por 24 horas
- [ ] Verificar métricas de Prometheus
- [ ] Confirmar que backups automáticos funcionan
- [ ] Documentar cualquier issue encontrado
- [ ] Capacitar a usuarios finales
- [ ] Configurar on-call rotation
- [ ] Revisar y ajustar alertas según patrones reales
- [ ] Optimizar queries lentas identificadas

---

## 📞 Soporte

**Equipo DevOps:**
- Email: devops@financia.com
- Slack: #financia-support
- On-call: +XX XXX XXX XXXX

**Documentación:**
- [ADMIN_GUIDE.md](./ADMIN_GUIDE.md)
- [USER_GUIDE.md](./USER_GUIDE.md)
- [API_REFERENCE.md](./API_REFERENCE.md)

---

**Versión:** 1.0  
**Última actualización:** Noviembre 2024  
**Mantenido por:** Equipo FinancIA DMS
