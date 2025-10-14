#!/bin/bash
# GPU Deployment Script for FinancIA 2030 (Linux/WSL)

set -e

echo "🚀 FinancIA 2030 - GPU Deployment"
echo "================================================================================"

# Verificar Docker
echo ""
echo "📦 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found! Please install Docker."
    exit 1
fi
docker --version

# Verificar soporte GPU
echo ""
echo "🔍 Checking GPU support..."
if docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo "✅ GPU support confirmed!"
    USE_GPU=true
else
    echo "⚠️  WARNING: GPU not detected or NVIDIA Container Toolkit not installed!"
    echo "Continuing with CPU-only build..."
    USE_GPU=false
fi

# Preguntar qué configuración usar
echo ""
echo "📋 Select deployment configuration:"
echo "1. GPU-accelerated (Dockerfile.backend.gpu)"
echo "2. CPU-only (Dockerfile.backend)"
read -p "Enter choice (1 or 2): " choice

if [[ "$choice" == "1" ]] && [[ "$USE_GPU" == true ]]; then
    echo ""
    echo "🚀 Building with GPU support..."
    docker-compose -f docker-compose.gpu.yml build
    
    echo ""
    echo "🚀 Starting services with GPU..."
    docker-compose -f docker-compose.gpu.yml up -d
    
    CONTAINER_NAME="financia_backend_gpu"
else
    echo ""
    echo "🚀 Building with CPU support..."
    docker-compose build
    
    echo ""
    echo "🚀 Starting services..."
    docker-compose up -d
    
    CONTAINER_NAME="financia_backend"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service URLs:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - MinIO Console: http://localhost:9001"
echo ""
echo "💡 Tip: Run 'docker logs $CONTAINER_NAME' to check GPU status"
echo ""
echo "🔍 Checking backend logs..."
sleep 5
docker logs --tail 50 $CONTAINER_NAME
