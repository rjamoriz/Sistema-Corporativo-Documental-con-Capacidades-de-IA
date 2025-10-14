# Script para probar el endpoint de archivos directamente
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🧪 TEST: Endpoint de Archivos" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$API_URL = "http://localhost:8000"
$TASK_ID = "d4102037-ed53-49ee-a574-41cc794108c5"  # Última tarea generada

# Paso 1: Login
Write-Host "📝 Paso 1: Obtener token..." -ForegroundColor Yellow
$loginBody = @{
    username = "admin@demo.documental.com"
    password = "Demo2025!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/login" `
        -Method POST `
        -Body $loginBody `
        -ContentType "application/json"
    
    $token = $loginResponse.access_token
    Write-Host "✅ Token obtenido" -ForegroundColor Green
} catch {
    Write-Host "❌ Error en login: $_" -ForegroundColor Red
    exit 1
}

# Paso 2: Obtener status de la tarea
Write-Host ""
Write-Host "📊 Paso 2: Verificar status de tarea..." -ForegroundColor Yellow
Write-Host "   Task ID: $TASK_ID" -ForegroundColor Gray

$headers = @{
    "Authorization" = "Bearer $token"
}

try {
    $status = Invoke-RestMethod -Uri "$API_URL/api/v1/synthetic/status/$TASK_ID" `
        -Method GET `
        -Headers $headers
    
    Write-Host "   Estado: $($status.status)" -ForegroundColor Cyan
    Write-Host "   Progreso: $($status.progress)%" -ForegroundColor Cyan
    Write-Host "   Documentos: $($status.documents_generated)" -ForegroundColor Cyan
    Write-Host "   Output Path: $($status.output_path)" -ForegroundColor Cyan
    
    if ($status.status -ne "completed") {
        Write-Host "⚠️  Tarea no completada" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ Tarea completada" -ForegroundColor Green
} catch {
    Write-Host "❌ Error obteniendo status: $_" -ForegroundColor Red
    Write-Host "   Response: $($_.Exception.Response)" -ForegroundColor Red
    exit 1
}

# Paso 3: Intentar obtener lista de archivos
Write-Host ""
Write-Host "📁 Paso 3: Obtener lista de archivos..." -ForegroundColor Yellow

try {
    $filesUrl = "$API_URL/api/v1/synthetic/tasks/$TASK_ID/files"
    Write-Host "   URL: $filesUrl" -ForegroundColor Gray
    
    $filesResponse = Invoke-RestMethod -Uri $filesUrl `
        -Method GET `
        -Headers $headers
    
    Write-Host "✅ Respuesta recibida" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Archivos encontrados: $($filesResponse.total_files)" -ForegroundColor Cyan
    Write-Host ""
    
    if ($filesResponse.total_files -eq 0) {
        Write-Host "⚠️  No hay archivos en la respuesta" -ForegroundColor Yellow
    } else {
        Write-Host "📄 Listado de archivos:" -ForegroundColor White
        foreach ($file in $filesResponse.files) {
            Write-Host "   - $($file.filename)" -ForegroundColor White
            Write-Host "     Categoría: $($file.category) | Tamaño: $([math]::Round($file.size / 1024, 2)) KB" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Error obteniendo archivos:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails) {
        Write-Host "   Detalles: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ TEST COMPLETADO" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
