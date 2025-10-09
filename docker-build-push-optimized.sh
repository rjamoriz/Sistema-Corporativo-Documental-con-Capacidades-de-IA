#!/bin/bash

# Script optimizado para construir y hacer push de imágenes Docker
# Limpia después de cada imagen para evitar problemas de espacio

set -e

# Cargar variables de entorno
if [ -f .docker.env ]; then
    source .docker.env
else
    echo "❌ Error: .docker.env no encontrado"
    exit 1
fi

# Login a Docker Hub
echo "🔐 Iniciando sesión en Docker Hub..."
echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USERNAME" --password-stdin
echo "✅ Login exitoso"

# Función para construir, hacer push y limpiar
build_push_clean() {
    local NAME=$1
    local DOCKERFILE=$2
    local CONTEXT=$3
    local IMAGE="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/financia2030-${NAME}:latest"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Procesando: $NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Build
    echo "🏗️  Construyendo imagen..."
    docker build -t "$IMAGE" -f "$DOCKERFILE" "$CONTEXT"
    echo "✅ Build completado"
    
    # Push
    echo "📤 Subiendo a Docker Hub..."
    docker push "$IMAGE"
    echo "✅ Push completado"
    echo "🌐 Disponible en: https://hub.docker.com/r/${DOCKER_NAMESPACE}/financia2030-${NAME}"
    
    # Limpiar para liberar espacio
    echo "🧹 Limpiando espacio..."
    docker rmi "$IMAGE" || true
    docker system prune -f
    echo "✅ Limpieza completada"
}

# Verificar espacio disponible
echo ""
echo "💾 Espacio en disco:"
df -h / | grep -E '(Filesystem|/)'
echo ""

# Construir imágenes una por una
build_push_clean "backend" "infrastructure/docker/backend/Dockerfile" "backend"
build_push_clean "frontend" "infrastructure/docker/frontend/Dockerfile" "frontend"
build_push_clean "worker-ingest" "infrastructure/docker/workers/Dockerfile.ingest" "backend"
build_push_clean "worker-process" "infrastructure/docker/workers/Dockerfile.process" "backend"
build_push_clean "worker-index" "infrastructure/docker/workers/Dockerfile.index" "backend"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                   ║"
echo "║      ✅ TODAS LAS IMÁGENES CONSTRUIDAS Y SUBIDAS EXITOSAMENTE     ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Imágenes disponibles en Docker Hub:"
echo "   • https://hub.docker.com/r/${DOCKER_NAMESPACE}/financia2030-backend"
echo "   • https://hub.docker.com/r/${DOCKER_NAMESPACE}/financia2030-frontend"
echo "   • https://hub.docker.com/r/${DOCKER_NAMESPACE}/financia2030-worker-ingest"
echo "   • https://hub.docker.com/r/${DOCKER_NAMESPACE}/financia2030-worker-process"
echo "   • https://hub.docker.com/r/${DOCKER_NAMESPACE}/financia2030-worker-index"
echo ""
