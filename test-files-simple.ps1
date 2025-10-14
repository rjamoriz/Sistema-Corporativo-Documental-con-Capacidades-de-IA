# Script simplificado para probar endpoint de archivos
$API_URL = "http://localhost:8000"
$TASK_ID = "d4102037-ed53-49ee-a574-41cc794108c5"

Write-Host "Probando endpoint de archivos..." -ForegroundColor Cyan

# Login
$loginBody = '{"username":"admin@demo.documental.com","password":"Demo2025!"}'
$loginResponse = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
$token = $loginResponse.access_token

Write-Host "Token obtenido" -ForegroundColor Green

# Obtener status
$headers = @{"Authorization" = "Bearer $token"}
$status = Invoke-RestMethod -Uri "$API_URL/api/v1/synthetic/status/$TASK_ID" -Headers $headers
Write-Host "Status: $($status.status)" -ForegroundColor Cyan
Write-Host "Output: $($status.output_path)" -ForegroundColor Cyan

# Obtener archivos
try {
    $files = Invoke-RestMethod -Uri "$API_URL/api/v1/synthetic/tasks/$TASK_ID/files" -Headers $headers
    Write-Host "Archivos encontrados: $($files.total_files)" -ForegroundColor Green
    $files.files | ForEach-Object { Write-Host "  - $($_.filename)" }
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "Detalles: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
}
