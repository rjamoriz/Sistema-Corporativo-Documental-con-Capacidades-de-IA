#!/bin/bash
# Script de verificación completa del despliegue con GPU

echo "=========================================="
echo "🔍 VERIFICACIÓN DEL DESPLIEGUE FINANCIA 2030"
echo "=========================================="
echo ""

# 1. Verificar contenedores
echo "📦 1. Estado de los contenedores:"
echo "-----------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep financia
echo ""

# 2. Verificar salud de servicios
echo "🏥 2. Health checks:"
echo "-----------------------------------"
for service in postgres redis opensearch minio; do
    container="financia_${service}"
    if docker ps --filter "name=$container" --filter "status=running" | grep -q $container; then
        health=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "no healthcheck")
        echo "  ✅ $service: $health"
    else
        echo "  ❌ $service: NOT RUNNING"
    fi
done
echo ""

# 3. Verificar logs del backend (últimas 30 líneas)
echo "📋 3. Logs del Backend (últimas 30 líneas):"
echo "-----------------------------------"
if docker ps --filter "name=financia_backend" --filter "status=running" | grep -q financia_backend; then
    docker logs financia_backend --tail 30
else
    echo "❌ Backend no está ejecutándose"
fi
echo ""

# 4. Verificar GPU en el backend
echo "🎮 4. Verificación de GPU:"
echo "-----------------------------------"
if docker ps --filter "name=financia_backend" --filter "status=running" | grep -q financia_backend; then
    echo "Buscando información de GPU en logs..."
    docker logs financia_backend 2>&1 | grep -E "(GPU|CUDA|cuda)" | tail -10
else
    echo "❌ Backend no está ejecutándose"
fi
echo ""

# 5. Test de conectividad
echo "🌐 5. Conectividad de servicios:"
echo "-----------------------------------"
# Backend
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo "  ✅ Backend API: http://localhost:8000 - OK"
else
    echo "  ⚠️  Backend API: http://localhost:8000 - NO RESPONDE"
fi

# Frontend
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "  ✅ Frontend: http://localhost:3000 - OK"
else
    echo "  ⚠️  Frontend: http://localhost:3000 - NO RESPONDE"
fi

# MinIO
if curl -s -o /dev/null -w "%{http_code}" http://localhost:9001 | grep -q "200"; then
    echo "  ✅ MinIO Console: http://localhost:9001 - OK"
else
    echo "  ⚠️  MinIO Console: http://localhost:9001 - NO RESPONDE"
fi
echo ""

# 6. Resumen
echo "=========================================="
echo "📊 RESUMEN"
echo "=========================================="
running=$(docker ps --filter "name=financia_" | wc -l)
expected=6  # backend, frontend, postgres, redis, opensearch, minio
if [ $((running - 1)) -eq $expected ]; then
    echo "✅ Todos los servicios están ejecutándose ($((running - 1))/$expected)"
else
    echo "⚠️  Servicios ejecutándose: $((running - 1))/$expected"
fi

echo ""
echo "📝 URLs de acceso:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000/docs"
echo "  - MinIO Console: http://localhost:9001"
echo ""
echo "🔑 Credenciales por defecto:"
echo "  - Usuario: admin.demo"
echo "  - Password: Demo2025!"
echo ""
echo "=========================================="
