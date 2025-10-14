# Script para probar la generación real de documentos sintéticos
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🧪 TEST: Generación Real de Documentos" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$API_URL = "http://localhost:8000"
$USERNAME = "admin@demo.documental.com"
$PASSWORD = "Demo2025!"

Write-Host "📝 Paso 1: Obtener token de autenticación..." -ForegroundColor Yellow
$loginBody = @{
    username = $USERNAME
    password = $PASSWORD
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/login" `
    -Method POST `
    -Body $loginBody `
    -ContentType "application/json"

$token = $loginResponse.access_token
Write-Host "✅ Token obtenido: $($token.Substring(0, 20))..." -ForegroundColor Green
Write-Host ""

# Headers con token
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host "📋 Paso 2: Verificar templates disponibles..." -ForegroundColor Yellow
$templates = Invoke-RestMethod -Uri "$API_URL/api/v1/synthetic/templates" `
    -Method GET `
    -Headers $headers

Write-Host "✅ Templates disponibles:" -ForegroundColor Green
foreach ($template in $templates) {
    Write-Host "  - $($template.id): $($template.name)" -ForegroundColor White
}
Write-Host ""

Write-Host "🚀 Paso 3: Generar 10 documentos sintéticos..." -ForegroundColor Yellow
$generateBody = @{
    total_documents = 10
    template_id = "default"
    auto_upload = $false
} | ConvertTo-Json

$generateResponse = Invoke-RestMethod -Uri "$API_URL/api/v1/synthetic/generate" `
    -Method POST `
    -Body $generateBody `
    -Headers $headers

$taskId = $generateResponse.task_id
Write-Host "✅ Generación iniciada!" -ForegroundColor Green
Write-Host "   Task ID: $taskId" -ForegroundColor White
Write-Host "   Documentos: $($generateResponse.total_documents)" -ForegroundColor White
Write-Host "   Tiempo estimado: $($generateResponse.estimated_time_seconds)s" -ForegroundColor White
Write-Host ""

Write-Host "⏳ Paso 4: Monitoreando progreso..." -ForegroundColor Yellow
$completed = $false
$attempts = 0
$maxAttempts = 30

while (-not $completed -and $attempts -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    $attempts++
    
    try {
        $status = Invoke-RestMethod -Uri "$API_URL/api/v1/synthetic/status/$taskId" `
            -Method GET `
            -Headers $headers
        
        $progress = $status.progress
        $statusText = $status.status
        $docsGenerated = $status.documents_generated
        
        Write-Host "   [$attempts] Estado: $statusText | Progreso: $progress% | Docs: $docsGenerated/$($generateResponse.total_documents)" -ForegroundColor Cyan
        
        if ($statusText -eq "completed") {
            $completed = $true
            Write-Host ""
            Write-Host "✅ Generación completada!" -ForegroundColor Green
            Write-Host "   Documentos generados: $docsGenerated" -ForegroundColor White
            Write-Host "   Directorio: $($status.output_path)" -ForegroundColor White
        } elseif ($statusText -eq "failed") {
            Write-Host ""
            Write-Host "❌ Error en generación: $($status.error)" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "   [!] Error consultando estado: $_" -ForegroundColor Yellow
    }
}

if (-not $completed) {
    Write-Host ""
    Write-Host "⚠️ Timeout esperando generación" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📁 Paso 5: Listar archivos generados..." -ForegroundColor Yellow
try {
    $files = Invoke-RestMethod -Uri "$API_URL/api/v1/synthetic/tasks/$taskId/files" `
        -Method GET `
        -Headers $headers
    
    Write-Host "✅ Archivos encontrados: $($files.total_files)" -ForegroundColor Green
    Write-Host ""
    
    foreach ($file in $files.files) {
        Write-Host "   📄 $($file.filename)" -ForegroundColor White
        Write-Host "      Categoría: $($file.category)" -ForegroundColor Gray
        Write-Host "      Tamaño: $([math]::Round($file.size / 1024, 2)) KB" -ForegroundColor Gray
        Write-Host "      Risk: $($file.metadata.risk_level)" -ForegroundColor Gray
        Write-Host "      Preview: $($file.preview_text.Substring(0, [Math]::Min(100, $file.preview_text.Length)))..." -ForegroundColor Gray
        Write-Host ""
    }
    
    # Descargar el primer archivo como ejemplo
    if ($files.files.Count -gt 0) {
        $firstFile = $files.files[0]
        Write-Host "⬇️ Descargando archivo de ejemplo: $($firstFile.filename)" -ForegroundColor Yellow
        
        $downloadUrl = "$API_URL/api/v1/synthetic/tasks/$taskId/files/$($firstFile.filename)"
        $outputPath = ".\$($firstFile.filename)"
        
        Invoke-WebRequest -Uri $downloadUrl `
            -Headers $headers `
            -OutFile $outputPath
        
        Write-Host "✅ Archivo descargado: $outputPath" -ForegroundColor Green
        Write-Host ""
    }
    
} catch {
    Write-Host "❌ Error listando archivos: $_" -ForegroundColor Red
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ TEST COMPLETADO" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Resumen:" -ForegroundColor Yellow
Write-Host "  - Task ID: $taskId" -ForegroundColor White
Write-Host "  - Documentos generados: $docsGenerated" -ForegroundColor White
Write-Host "  - Archivos disponibles: $($files.total_files)" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Accede al frontend para ver más detalles:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host ""
