# Script para probar upload de documentos
Write-Host "=== PRUEBA DE UPLOAD DE DOCUMENTOS ===" -ForegroundColor Cyan

# 1. Login
Write-Host "`n[1] Obteniendo token de autenticacion..." -ForegroundColor Yellow
$loginBody = "username=admin@demo.documental.com&password=Demo2025!"
try {
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $loginBody
    $token = ($loginResponse.Content | ConvertFrom-Json).access_token
    Write-Host "✓ Token obtenido" -ForegroundColor Green
} catch {
    Write-Host "✗ Error en login: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Preparar archivo
Write-Host "`n[2] Preparando archivo para upload..." -ForegroundColor Yellow
$filePath = "test_document.txt"
if (-not (Test-Path $filePath)) {
    Write-Host "✗ Archivo no encontrado: $filePath" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Archivo encontrado: $filePath" -ForegroundColor Green

# 3. Upload usando curl (más simple que PowerShell multipart)
Write-Host "`n[3] Subiendo documento..." -ForegroundColor Yellow
$curlCommand = "curl -X POST `"http://localhost:8000/api/v1/documents/upload`" -H `"Authorization: Bearer $token`" -F `"file=@$filePath`" -F `"title=Documento de Prueba`" -F `"department=IT`""
Write-Host "Ejecutando: $curlCommand" -ForegroundColor Gray

try {
    $uploadResult = Invoke-Expression $curlCommand | ConvertFrom-Json
    Write-Host "✓ Upload exitoso!" -ForegroundColor Green
    Write-Host "`nRespuesta del servidor:" -ForegroundColor Cyan
    $uploadResult | Format-List
    
    # Guardar document_id para uso posterior
    $global:lastDocumentId = $uploadResult.document_id
    Write-Host "`nDocument ID: $global:lastDocumentId" -ForegroundColor Yellow
    
} catch {
    Write-Host "✗ Error en upload: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 4. Verificar en base de datos
Write-Host "`n[4] Verificando documento en base de datos..." -ForegroundColor Yellow
$dbCheck = docker exec financia_postgres psql -U financia -d financia_db -c "SELECT id, title, mime_type, file_size_bytes, status FROM documents ORDER BY created_at DESC LIMIT 1;" 2>&1
Write-Host $dbCheck

Write-Host "`n=== PRUEBA COMPLETADA ===" -ForegroundColor Green
Write-Host "El documento se ha subido correctamente al sistema." -ForegroundColor Green
