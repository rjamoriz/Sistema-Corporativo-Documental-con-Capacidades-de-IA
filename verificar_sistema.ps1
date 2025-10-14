# Script de Verificación del Sistema
# Ejecutar: .\verificar_sistema.ps1

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Sistema Corporativo Documental - Verificación  " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Función para mostrar resultado
function Show-Result {
    param($test, $result)
    if ($result) {
        Write-Host "✅ $test" -ForegroundColor Green
    } else {
        Write-Host "❌ $test" -ForegroundColor Red
    }
}

# 1. Verificar Docker Compose
Write-Host "Verificando contenedores Docker..." -ForegroundColor Yellow
$containers = docker-compose ps --format json 2>$null | ConvertFrom-Json
$backend_running = $containers | Where-Object { $_.Service -eq "backend" -and $_.State -eq "running" }
$frontend_running = $containers | Where-Object { $_.Service -eq "frontend" -and $_.State -eq "running" }
$postgres_running = $containers | Where-Object { $_.Service -eq "postgres" -and $_.State -eq "running" }
$redis_running = $containers | Where-Object { $_.Service -eq "redis" -and $_.State -eq "running" }
$minio_running = $containers | Where-Object { $_.Service -eq "minio" -and $_.State -eq "running" }
$opensearch_running = $containers | Where-Object { $_.Service -eq "opensearch" -and $_.State -eq "running" }

Show-Result "Backend container" ($backend_running -ne $null)
Show-Result "Frontend container" ($frontend_running -ne $null)
Show-Result "PostgreSQL container" ($postgres_running -ne $null)
Show-Result "Redis container" ($redis_running -ne $null)
Show-Result "MinIO container" ($minio_running -ne $null)
Show-Result "OpenSearch container" ($opensearch_running -ne $null)
Write-Host ""

# 2. Verificar endpoints de Backend
Write-Host "Verificando endpoints del Backend..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -ErrorAction Stop
    Show-Result "Backend health endpoint" ($healthResponse.StatusCode -eq 200)
} catch {
    Show-Result "Backend health endpoint" $false
}

try {
    $docsResponse = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -ErrorAction Stop
    Show-Result "API documentation" ($docsResponse.StatusCode -eq 200)
} catch {
    Show-Result "API documentation" $false
}
Write-Host ""

# 3. Verificar Frontend
Write-Host "Verificando Frontend..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -ErrorAction Stop
    Show-Result "Frontend accessible" ($frontendResponse.StatusCode -eq 200)
} catch {
    Show-Result "Frontend accessible" $false
}
Write-Host ""

# 4. Verificar archivos sinteticos
Write-Host "Verificando documentos sinteticos..." -ForegroundColor Yellow
$syntheticDirs = docker exec financia_backend sh -c "ls -d /tmp/synthetic_documents/*/ 2>/dev/null | wc -l" 2>$null
if ($syntheticDirs) {
    $count = [int]$syntheticDirs.Trim()
    Show-Result "Tareas de generación encontradas ($count)" ($count -gt 0)
    
    if ($count -gt 0) {
        # Obtener la última tarea
        $lastTask = docker exec financia_backend sh -c "ls -td /tmp/synthetic_documents/*/ | head -1" 2>$null
        if ($lastTask) {
            $taskId = ($lastTask.Trim() -split '/')[-2]
            $pdfCount = docker exec financia_backend sh -c "ls /tmp/synthetic_documents/$taskId/*.pdf 2>/dev/null | wc -l" 2>$null
            if ($pdfCount) {
                $pdfCountInt = [int]$pdfCount.Trim()
                Show-Result "PDFs generados en última tarea ($pdfCountInt)" ($pdfCountInt -gt 0)
            }
        }
    }
} else {
    Show-Result "Directorio de sintéticos" $false
}
Write-Host ""

# 5. Verificar logs del backend
Write-Host "Verificando logs del Backend (ultimas 10 lineas)..." -ForegroundColor Yellow
$logs = docker-compose logs backend --tail 10 2>$null
if ($logs -match "ERROR|Exception|Traceback") {
    Write-Host "Se encontraron errores en los logs" -ForegroundColor Yellow
    Write-Host $logs -ForegroundColor Gray
} else {
    Write-Host "No hay errores recientes en los logs" -ForegroundColor Green
}
Write-Host ""

# 6. Verificar servicios auxiliares
Write-Host "Verificando servicios auxiliares..." -ForegroundColor Yellow

# MinIO
try {
    $minioResponse = Invoke-WebRequest -Uri "http://localhost:9001" -Method GET -ErrorAction Stop
    Show-Result "MinIO console" ($minioResponse.StatusCode -eq 200)
} catch {
    Show-Result "MinIO console" $false
}

# OpenSearch
try {
    $osResponse = Invoke-WebRequest -Uri "http://localhost:9200" -Method GET -SkipCertificateCheck -ErrorAction Stop
    Show-Result "OpenSearch API" ($osResponse.StatusCode -eq 200)
} catch {
    Show-Result "OpenSearch API" $false
}
Write-Host ""

# Resumen final
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "           Verificación Completada               " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Acceso al Sistema:" -ForegroundColor Yellow
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "   MinIO:       http://localhost:9001" -ForegroundColor White
Write-Host ""
Write-Host "Credenciales de prueba:" -ForegroundColor Yellow
Write-Host "   Usuario: admin@example.com" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Documentacion adicional:" -ForegroundColor Yellow
Write-Host "   - SISTEMA_VERIFICADO.md" -ForegroundColor White
Write-Host "   - GUIA_TESTING_USUARIO.md" -ForegroundColor White
Write-Host "   - QUICKSTART.md" -ForegroundColor White
Write-Host ""
