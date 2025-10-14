# Test Dashboard Stats Endpoint
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Testing Dashboard Stats Endpoint" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login
Write-Host "Step 1: Logging in..." -ForegroundColor Yellow
$loginBody = "username=admin@demo.documental.com&password=Demo2025!"

try {
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -ContentType "application/x-www-form-urlencoded" -Body $loginBody
    $token = ($loginResponse.Content | ConvertFrom-Json).access_token
    Write-Host "Login successful" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "Login failed: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Get Dashboard Stats
Write-Host "Step 2: Getting dashboard stats..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/stats" -Method GET -Headers @{"Authorization"="Bearer $token"}
    Write-Host "Dashboard stats retrieved successfully" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Dashboard Statistics:" -ForegroundColor Cyan
    Write-Host "--------------------" -ForegroundColor Cyan
    Write-Host "Total Documents: $($stats.total_documents)" -ForegroundColor White
    Write-Host "Total Chunks: $($stats.total_chunks)" -ForegroundColor White
    Write-Host "Total Entities: $($stats.total_entities)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Documents by Status:" -ForegroundColor Cyan
    $stats.documents_by_status.PSObject.Properties | ForEach-Object {
        Write-Host "  $($_.Name): $($_.Value)" -ForegroundColor White
    }
    Write-Host ""
    
    Write-Host "Documents by Category:" -ForegroundColor Cyan
    $stats.documents_by_category.PSObject.Properties | ForEach-Object {
        Write-Host "  $($_.Name): $($_.Value)" -ForegroundColor White
    }
    Write-Host ""
    
    Write-Host "Recent Uploads:" -ForegroundColor Cyan
    if ($stats.recent_uploads.Count -gt 0) {
        $stats.recent_uploads | ForEach-Object {
            Write-Host "  - $($_.filename) ($($_.status))" -ForegroundColor White
            Write-Host "    Created: $($_.created_at)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  No recent uploads" -ForegroundColor Gray
    }
    Write-Host ""
    
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "All tests passed!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Cyan
    
} catch {
    Write-Host "Failed to get dashboard stats: $_" -ForegroundColor Red
    Write-Host "Error Details:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
