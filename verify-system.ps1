# FinancIA 2030 - System Verification Script
# Verifica que todos los servicios estén funcionando correctamente

Write-Host "`n🔍 VERIFICACIÓN DEL SISTEMA FINANCIA 2030" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# 1. Check Docker containers
Write-Host "`n📦 1. Estado de Contenedores Docker:" -ForegroundColor Yellow
wsl bash -c 'docker ps --filter "name=financia" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# 2. Check GPU in backend
Write-Host "`n🎮 2. Verificación de GPU en Backend:" -ForegroundColor Yellow
Write-Host "Últimas 30 líneas de logs del backend..." -ForegroundColor Gray
wsl bash -c 'docker logs financia_backend_gpu --tail 30 2>&1 | grep -E "GPU|CUDA|RTX|ERROR|✅|⚠️" || echo "Backend no disponible"'

# 3. Test Backend API
Write-Host "`n🌐 3. Prueba de API del Backend:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Backend API respondiendo: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend API no responde" -ForegroundColor Red
}

# 4. Test Frontend
Write-Host "`n🎨 4. Prueba de Frontend:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Frontend respondiendo: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend no responde" -ForegroundColor Red
}

# 5. Check Database
Write-Host "`n💾 5. Estado de Base de Datos:" -ForegroundColor Yellow
wsl bash -c 'docker exec financia_postgres pg_isready -U postgres 2>&1' 

# 6. Check Storage (MinIO)
Write-Host "`n📁 6. Estado de Almacenamiento (MinIO):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ MinIO respondiendo: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ MinIO no responde" -ForegroundColor Red
}

# 7. Check Search (OpenSearch)
Write-Host "`n🔎 7. Estado de Motor de Búsqueda (OpenSearch):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200/_cluster/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ OpenSearch respondiendo: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ OpenSearch no responde" -ForegroundColor Red
}

# 8. Check Redis
Write-Host "`n⚡ 8. Estado de Caché (Redis):" -ForegroundColor Yellow
wsl bash -c 'docker exec financia_redis redis-cli ping 2>&1'

# Summary
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "📊 RESUMEN DE VERIFICACIÓN" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`n✅ Accesos al Sistema:" -ForegroundColor Green
Write-Host "   • Frontend:           http://localhost:3000" -ForegroundColor White
Write-Host "   • Backend API:        http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • MinIO Console:      http://localhost:9001" -ForegroundColor White
Write-Host "   • OpenSearch:         http://localhost:9200" -ForegroundColor White

Write-Host "`n💡 Comandos Útiles:" -ForegroundColor Yellow
Write-Host "   Ver logs backend:     wsl bash -c 'docker logs financia_backend_gpu --tail 50'" -ForegroundColor Gray
Write-Host "   Ver logs frontend:    wsl bash -c 'docker logs financia_frontend --tail 50'" -ForegroundColor Gray
Write-Host "   Reiniciar sistema:    .\stop-system.ps1 && .\start-system.ps1" -ForegroundColor Gray

Write-Host "`n✨ Sistema FinancIA 2030 con GPU RTX 4070" -ForegroundColor Cyan
Write-Host ""
