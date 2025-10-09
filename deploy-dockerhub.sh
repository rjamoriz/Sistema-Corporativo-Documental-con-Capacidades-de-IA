#!/bin/bash

# FinancIA 2030 - Complete Docker Hub Deployment Script
# Este script automatiza todo el proceso de deployment con Docker Hub

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║      🚀 FINANCIA 2030 - DEPLOYMENT COMPLETO DOCKER HUB        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored messages
print_step() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check if .docker.env exists
if [ ! -f ".docker.env" ]; then
    echo -e "${RED}❌ Error: .docker.env no encontrado${NC}"
    echo ""
    echo "Crea el archivo .docker.env con:"
    cat << 'EOF'
DOCKER_USERNAME=rjamoriz
DOCKER_TOKEN=your_docker_token_here
DOCKER_REGISTRY=docker.io
DOCKER_NAMESPACE=rjamoriz
DOCKER_IMAGE_PREFIX=financia2030
DOCKER_TAG=latest
EOF
    exit 1
fi

# Load configuration
source .docker.env

# ============================================================================
# STEP 1: Login to Docker Hub
# ============================================================================
print_step "🔐 PASO 1: Login en Docker Hub"

echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USERNAME" --password-stdin 2>&1 | grep -v "WARNING"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Login exitoso${NC}"
else
    echo -e "${RED}❌ Error en login${NC}"
    exit 1
fi

echo ""

# ============================================================================
# STEP 2: Build and Push Images
# ============================================================================
print_step "🏗️  PASO 2: Build y Push de Imágenes"

# Ask user if they want to build
read -p "¿Deseas construir y subir las imágenes? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${BLUE}Iniciando build de imágenes...${NC}"
    echo ""
    
    ./docker-build-push.sh
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error en build/push de imágenes${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Saltando build, usando imágenes existentes en Docker Hub${NC}"
fi

echo ""

# ============================================================================
# STEP 3: Verify Images in Docker Hub
# ============================================================================
print_step "🔍 PASO 3: Verificando Imágenes en Docker Hub"

IMAGES=(
    "backend"
    "frontend"
    "worker-ingest"
    "worker-process"
    "worker-index"
)

echo "Verificando imágenes disponibles:"
echo ""

for IMAGE in "${IMAGES[@]}"; do
    IMAGE_NAME="${DOCKER_USERNAME}/${DOCKER_IMAGE_PREFIX}-${IMAGE}:${DOCKER_TAG}"
    
    # Try to pull image info
    if docker manifest inspect "$IMAGE_NAME" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ${IMAGE_NAME}${NC}"
    else
        echo -e "${RED}❌ ${IMAGE_NAME} - NO ENCONTRADA${NC}"
        echo -e "${YELLOW}   Necesitas construir esta imagen primero${NC}"
    fi
done

echo ""

# ============================================================================
# STEP 4: Stop existing containers
# ============================================================================
print_step "🛑 PASO 4: Deteniendo Contenedores Existentes"

cd infrastructure/docker

if [ -f "docker-compose.hub.yml" ]; then
    docker-compose -f docker-compose.hub.yml down -v 2>/dev/null || true
    echo -e "${GREEN}✅ Contenedores detenidos${NC}"
else
    echo -e "${YELLOW}⚠️  docker-compose.hub.yml no encontrado${NC}"
fi

echo ""

# ============================================================================
# STEP 5: Pull latest images
# ============================================================================
print_step "📥 PASO 5: Descargando Últimas Imágenes"

docker-compose -f docker-compose.hub.yml pull

echo -e "${GREEN}✅ Imágenes descargadas${NC}"
echo ""

# ============================================================================
# STEP 6: Start services
# ============================================================================
print_step "🚀 PASO 6: Iniciando Servicios"

# Check if .env exists in backend
if [ ! -f "../../backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env no encontrado${NC}"
    echo -e "${YELLOW}   Creando desde .env.example...${NC}"
    
    if [ -f "../../.env.example" ]; then
        cp ../../.env.example ../../backend/.env
        echo -e "${GREEN}✅ .env creado${NC}"
        echo -e "${YELLOW}   IMPORTANTE: Edita backend/.env y agrega tus API keys${NC}"
    fi
fi

# Start services
docker-compose -f docker-compose.hub.yml up -d

echo -e "${GREEN}✅ Servicios iniciados${NC}"
echo ""

# ============================================================================
# STEP 7: Health checks
# ============================================================================
print_step "🏥 PASO 7: Verificando Salud de Servicios"

echo "Esperando a que los servicios estén listos (esto puede tomar 1-2 minutos)..."
echo ""

sleep 10

SERVICES=(
    "financia-postgres:5432"
    "financia-opensearch:9200"
    "financia-redis:6379"
    "financia-kafka:9092"
    "financia-minio:9000"
    "financia-phoenix:6006"
    "financia-backend:8000"
    "financia-frontend:80"
)

for SERVICE in "${SERVICES[@]}"; do
    CONTAINER="${SERVICE%%:*}"
    PORT="${SERVICE##*:}"
    
    STATUS=$(docker inspect -f '{{.State.Status}}' "$CONTAINER" 2>/dev/null || echo "not found")
    
    if [ "$STATUS" = "running" ]; then
        echo -e "${GREEN}✅ ${CONTAINER} - Running${NC}"
    else
        echo -e "${RED}❌ ${CONTAINER} - ${STATUS}${NC}"
    fi
done

echo ""

# ============================================================================
# STEP 8: Display access information
# ============================================================================
print_step "🌐 PASO 8: Información de Acceso"

cat << 'EOF'

╔════════════════════════════════════════════════════════════════╗
║                     SERVICIOS DISPONIBLES                      ║
╚════════════════════════════════════════════════════════════════╝

📱 APLICACIONES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🌐 Frontend:          http://localhost:3000
   🔌 Backend API:       http://localhost:8000
   📚 API Docs:          http://localhost:8000/docs
   📊 Phoenix UI:        http://localhost:6006

🗄️  INFRAESTRUCTURA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🐘 PostgreSQL:        localhost:5432
   🔍 OpenSearch:        http://localhost:9200
   💾 Redis:             localhost:6379
   📨 Kafka:             localhost:9092
   📦 MinIO:             http://localhost:9000
   📈 Prometheus:        http://localhost:9090
   📊 Grafana:           http://localhost:3001
   🧪 MLflow:            http://localhost:5000

🔧 MONITOREO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Ver logs:             docker-compose -f docker-compose.hub.yml logs -f
   Ver contenedores:     docker-compose -f docker-compose.hub.yml ps
   Detener todo:         docker-compose -f docker-compose.hub.yml down

🐳 DOCKER HUB:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Ver imágenes:         https://hub.docker.com/u/rjamoriz

EOF

echo -e "${GREEN}✅ DEPLOYMENT COMPLETADO EXITOSAMENTE${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
