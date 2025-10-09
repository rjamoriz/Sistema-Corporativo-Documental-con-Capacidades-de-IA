#!/bin/bash

# FinancIA 2030 - Docker Hub Build & Push Script
# Este script construye y sube las imágenes Docker a Docker Hub

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║      🐳 FINANCIA 2030 - DOCKER HUB DEPLOYMENT                 ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load Docker Hub credentials
if [ -f ".docker.env" ]; then
    source .docker.env
    echo -e "${GREEN}✅ Credenciales de Docker Hub cargadas${NC}"
else
    echo -e "${RED}❌ Error: .docker.env no encontrado${NC}"
    echo "   Crea el archivo .docker.env con tus credenciales de Docker Hub"
    exit 1
fi

# Login to Docker Hub
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 Iniciando sesión en Docker Hub..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USERNAME" --password-stdin 2>&1 | grep -v "WARNING"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Login exitoso en Docker Hub${NC}"
else
    echo -e "${RED}❌ Error en login de Docker Hub${NC}"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏗️  Construyendo imágenes Docker..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to build and push image
build_and_push() {
    local SERVICE=$1
    local DOCKERFILE=$2
    local CONTEXT=$3
    local IMAGE_NAME="${DOCKER_USERNAME}/${DOCKER_IMAGE_PREFIX}-${SERVICE}:${DOCKER_TAG}"
    
    echo -e "${BLUE}📦 Construyendo: ${SERVICE}${NC}"
    echo "   Imagen: ${IMAGE_NAME}"
    echo "   Dockerfile: ${DOCKERFILE}"
    echo "   Context: ${CONTEXT}"
    
    # Build
    if docker build -f "$DOCKERFILE" -t "$IMAGE_NAME" "$CONTEXT"; then
        echo -e "${GREEN}   ✅ Build exitoso${NC}"
        
        # Push
        echo -e "${BLUE}   📤 Subiendo a Docker Hub...${NC}"
        if docker push "$IMAGE_NAME"; then
            echo -e "${GREEN}   ✅ Push exitoso${NC}"
            echo -e "${GREEN}   🌐 Disponible en: https://hub.docker.com/r/${DOCKER_USERNAME}/${DOCKER_IMAGE_PREFIX}-${SERVICE}${NC}"
        else
            echo -e "${RED}   ❌ Error en push${NC}"
            return 1
        fi
    else
        echo -e "${RED}   ❌ Error en build${NC}"
        return 1
    fi
    
    echo ""
}

# 1. Backend
build_and_push "backend" "infrastructure/docker/backend/Dockerfile" "backend"

# 2. Frontend
build_and_push "frontend" "infrastructure/docker/frontend/Dockerfile" "frontend"

# 3. Worker Ingest
build_and_push "worker-ingest" "infrastructure/docker/workers/Dockerfile.ingest" "backend"

# 4. Worker Process
build_and_push "worker-process" "infrastructure/docker/workers/Dockerfile.process" "backend"

# 5. Worker Index
build_and_push "worker-index" "infrastructure/docker/workers/Dockerfile.index" "backend"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ TODAS LAS IMÁGENES CONSTRUIDAS Y SUBIDAS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Imágenes disponibles en Docker Hub:"
echo ""
echo "   🔹 ${DOCKER_USERNAME}/${DOCKER_IMAGE_PREFIX}-backend:${DOCKER_TAG}"
echo "   🔹 ${DOCKER_USERNAME}/${DOCKER_IMAGE_PREFIX}-frontend:${DOCKER_TAG}"
echo "   🔹 ${DOCKER_USERNAME}/${DOCKER_IMAGE_PREFIX}-worker-ingest:${DOCKER_TAG}"
echo "   🔹 ${DOCKER_USERNAME}/${DOCKER_IMAGE_PREFIX}-worker-process:${DOCKER_TAG}"
echo "   🔹 ${DOCKER_USERNAME}/${DOCKER_IMAGE_PREFIX}-worker-index:${DOCKER_TAG}"
echo ""
echo "🌐 Ver en Docker Hub:"
echo "   https://hub.docker.com/u/${DOCKER_USERNAME}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Próximo paso: Actualizar docker-compose.yml para usar estas imágenes"
echo ""
