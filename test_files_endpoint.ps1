# Script de Prueba de Visualización de Archivos
# Ejecutar: .\test_files_endpoint.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$Token = ""
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Test de Visualización de Archivos     " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Si no se proporcionó token, pedir al usuario
if ([string]::IsNullOrEmpty($Token)) {
    Write-Host "INSTRUCCIONES PARA OBTENER TOKEN:" -ForegroundColor Yellow
    Write-Host "1. Ve a: http://localhost:3000" -ForegroundColor White
    Write-Host "2. Login: admin@demo.documental.com / admin123" -ForegroundColor White
    Write-Host "3. Abre consola del navegador (F12)" -ForegroundColor White
    Write-Host "4. Ejecuta: localStorage.getItem('auth_token')" -ForegroundColor White
    Write-Host "5. Copia el token" -ForegroundColor White
    Write-Host ""
    $Token = Read-Host "Pega tu token aqui"
}

if ([string]::IsNullOrEmpty($Token)) {
    Write-Host "Error: Token no proporcionado" -ForegroundColor Red
    exit 1
}

Write-Host "Token recibido (primeros 20 caracteres): $($Token.Substring(0, [Math]::Min(20, $Token.Length)))..." -ForegroundColor Green
Write-Host ""

# Headers
$headers = @{
    Authorization = "Bearer $Token"
}

# Tareas disponibles para probar
$taskIds = @(
    "74d481a4-4178-4f43-b767-60953f5dde34",
    "220fc082-a45b-4dda-80da-186fbb32d733",
    "d4102037-ed53-49ee-a574-41cc794108c5",
    "b3254709-7ea0-4168-a5de-7d9492fc81ce",
    "18ed4bea-153c-4eb1-b22b-5574f98d1505",
    "beb0efef-5378-47d3-a5e5-f8eec7c92d01"
)

Write-Host "Probando endpoints de visualizacion..." -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($taskId in $taskIds) {
    Write-Host "Tarea: $taskId" -ForegroundColor Cyan
    
    try {
        $url = "http://localhost:8000/api/v1/synthetic/tasks/$taskId/files"
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get -ErrorAction Stop
        
        Write-Host "  Status: SUCCESS" -ForegroundColor Green
        Write-Host "  Total archivos: $($response.total_files)" -ForegroundColor White
        
        if ($response.total_files -gt 0) {
            Write-Host "  Primer archivo:" -ForegroundColor Gray
            Write-Host "    - Nombre: $($response.files[0].filename)" -ForegroundColor Gray
            Write-Host "    - Categoria: $($response.files[0].category)" -ForegroundColor Gray
            Write-Host "    - Tamano: $([math]::Round($response.files[0].size/1024, 2)) KB" -ForegroundColor Gray
            $successCount++
        }
        
    } catch {
        Write-Host "  Status: FAILED" -ForegroundColor Red
        $statusCode = $_.Exception.Response.StatusCode.Value__
        Write-Host "  Error: $statusCode - $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
    
    Write-Host ""
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "RESUMEN:" -ForegroundColor Yellow
Write-Host "  Tareas probadas: $($taskIds.Count)" -ForegroundColor White
Write-Host "  Exitosas: $successCount" -ForegroundColor Green
Write-Host "  Fallidas: $failCount" -ForegroundColor Red
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if ($successCount -gt 0) {
    Write-Host "FIX FUNCIONANDO!" -ForegroundColor Green
    Write-Host "Ahora puedes probar en el frontend (http://localhost:3000)" -ForegroundColor White
} else {
    Write-Host "Revisa el token o el estado del backend" -ForegroundColor Yellow
    Write-Host "Comando: docker-compose logs backend --tail 20" -ForegroundColor Gray
}
