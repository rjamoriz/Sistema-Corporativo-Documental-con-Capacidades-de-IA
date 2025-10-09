# Scripts de Operación

Este directorio contiene scripts para la gestión operacional del sistema FinancIA 2030.

## Scripts Disponibles

### 1. setup.sh
**Propósito:** Configuración inicial del entorno

**Uso:**
```bash
./scripts/setup.sh
```

**Acciones:**
- Verifica requisitos (Docker, Docker Compose)
- Crea archivo .env desde plantilla
- Crea estructura de directorios
- Descarga imágenes Docker necesarias

---

### 2. start.sh
**Propósito:** Inicio de todos los servicios con verificaciones de salud

**Uso:**
```bash
./scripts/start.sh
```

**Acciones:**
- Inicia todos los servicios en Docker Compose
- Verifica salud de cada servicio secuencialmente:
  - PostgreSQL + pgvector
  - OpenSearch
  - Redis
  - Kafka + Zookeeper
  - MinIO
  - Backend API
- Muestra puntos de acceso para cada servicio

**Servicios y Puertos:**
- API Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- OpenSearch: http://localhost:9200
- OpenSearch Dashboards: http://localhost:5601
- MinIO Console: http://localhost:9001
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090
- MLflow: http://localhost:5000

---

### 3. stop.sh
**Propósito:** Detención ordenada de todos los servicios

**Uso:**
```bash
./scripts/stop.sh
```

**Acciones:**
- Detiene todos los contenedores
- Preserva volúmenes de datos

**Para eliminar también los datos:**
```bash
cd infrastructure/docker
docker-compose down -v
```

---

### 4. backup.sh
**Propósito:** Creación de backup completo del sistema

**Uso:**
```bash
./scripts/backup.sh
```

**Acciones:**
- Crea directorio con timestamp: `backups/YYYYMMDD_HHMMSS/`
- Backup PostgreSQL (comprimido con gzip)
- Backup MinIO (documentos y objetos)
- Backup logs de aplicación
- Genera metadata del backup (JSON)

**Contenido del Backup:**
- `postgres_backup.sql.gz`: Base de datos completa
- `minio_backup/`: Bucket de documentos
- `logs/`: Logs de aplicación y auditoría
- `backup_metadata.json`: Información del backup

---

### 5. restore.sh
**Propósito:** Restauración desde backup

**Uso:**
```bash
./scripts/restore.sh <backup_directory>
```

**Ejemplo:**
```bash
./scripts/restore.sh ./backups/20240115_143022/
```

**Acciones:**
- Verifica integridad del backup
- Detiene servicios existentes
- Restaura PostgreSQL
- Restaura MinIO
- Restaura logs
- Reinicia todos los servicios

**⚠️ ADVERTENCIA:** Esta operación sobrescribirá los datos actuales

---

### 6. test.sh
**Propósito:** Ejecución de suite completa de pruebas

**Uso:**
```bash
./scripts/test.sh
```

**Acciones:**
- Crea/activa entorno virtual Python
- Instala dependencias de testing
- Ejecuta pruebas unitarias
- Ejecuta pruebas de integración
- Ejecuta pruebas de API
- Genera reporte de cobertura (HTML)
- Ejecuta verificaciones de calidad:
  - Black (formato de código)
  - Flake8 (linting)
  - MyPy (type checking)
- Ejecuta análisis de seguridad:
  - Bandit (vulnerabilidades en código)
  - Safety (vulnerabilidades en dependencias)

**Salida:**
- Terminal: Resultados de todas las pruebas
- `htmlcov/index.html`: Reporte de cobertura interactivo

---

## Flujo de Trabajo Típico

### Instalación Inicial
```bash
# 1. Configurar entorno
./scripts/setup.sh

# 2. Iniciar servicios
./scripts/start.sh

# 3. Ejecutar pruebas
./scripts/test.sh
```

### Operación Diaria
```bash
# Iniciar sistema
./scripts/start.sh

# Detener sistema
./scripts/stop.sh
```

### Mantenimiento
```bash
# Crear backup antes de actualizaciones
./scripts/backup.sh

# Después de cambios, ejecutar pruebas
./scripts/test.sh

# Si hay problemas, restaurar backup
./scripts/restore.sh ./backups/20240115_143022/
```

---

## Requisitos

### Sistemas Operativos Soportados
- Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
- macOS (11.0+)
- Windows (WSL2)

### Dependencias
- Docker 24.0+
- Docker Compose 2.20+
- Bash 4.0+
- Python 3.11+ (para test.sh)

### Permisos
Todos los scripts requieren permisos de ejecución:
```bash
chmod +x scripts/*.sh
```

---

## Estructura de Datos

### Directorio de Backups
```
backups/
├── 20240115_143022/
│   ├── postgres_backup.sql.gz
│   ├── minio_backup/
│   │   └── financia-documents/
│   ├── logs/
│   │   ├── app.log
│   │   └── audit.log
│   └── backup_metadata.json
└── 20240116_090000/
    └── ...
```

### Logs
```
backend/logs/
├── app.log           # Logs de aplicación
├── audit.log         # Logs de auditoría (inmutables)
└── error.log         # Logs de errores
```

---

## Solución de Problemas

### Error: "Docker no está instalado"
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# macOS
brew install docker docker-compose
```

### Error: "Servicio X no responde"
```bash
# Ver logs del servicio
cd infrastructure/docker
docker-compose logs <servicio>

# Reiniciar servicio específico
docker-compose restart <servicio>
```

### Error: "Puerto ya en uso"
```bash
# Identificar proceso usando el puerto
sudo lsof -i :<puerto>

# Cambiar puerto en .env
nano .env
# Modificar: API_PORT=8001
```

### Backup/Restore falla
```bash
# Verificar espacio en disco
df -h

# Verificar permisos
ls -la backups/

# Verificar logs de Docker
docker-compose logs postgres minio
```

---

## Variables de Entorno Clave

Scripts utilizan estas variables de `.env`:

```bash
# PostgreSQL
POSTGRES_USER=financia_user
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=financia_db

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=<secure_password>

# API
API_PORT=8000
API_HOST=0.0.0.0

# Testing
LOG_LEVEL=DEBUG  # En .env.test
```

---

## CI/CD Integration

Estos scripts están diseñados para integrarse con CI/CD:

```yaml
# Ejemplo GitHub Actions
- name: Run Tests
  run: ./scripts/test.sh

- name: Create Backup
  run: ./scripts/backup.sh

- name: Deploy
  run: |
    ./scripts/stop.sh
    docker-compose pull
    ./scripts/start.sh
```

---

## Monitorización

### Healthchecks
Todos los servicios tienen healthchecks configurados:
```bash
docker-compose ps  # Ver estado de salud
```

### Logs en Tiempo Real
```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f backend
```

### Métricas
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

---

## Seguridad

### Backups
- Los backups contienen datos sensibles
- Almacenar en ubicación segura y cifrada
- Implementar rotación de backups (retención: 30 días)
- No versionar backups en Git

### Credenciales
- Nunca versionar `.env`
- Usar secretos gestionados en producción
- Rotar contraseñas periódicamente

### Logs
- `audit.log` es inmutable (solo append)
- Contiene trazabilidad completa para auditorías
- No eliminar sin autorización de DPO

---

## Contacto y Soporte

Para reportar problemas con los scripts:
1. Verificar logs: `docker-compose logs`
2. Revisar issues conocidos en GitHub
3. Crear issue con detalles del error

Documentación adicional:
- `/docs/ARCHITECTURE.md` - Arquitectura del sistema
- `/docs/GOVERNANCE.md` - Gobernanza y cumplimiento
- `/backend/README.md` - Documentación del backend
