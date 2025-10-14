# Pre-pull Docker images before build
# This downloads images separately with better error handling

$separator = "=" * 80

Write-Host "FinancIA 2030 - Pre-pull Docker Images" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan

# Images needed
$images = @(
    "nvidia/cuda:12.6.0-runtime-ubuntu22.04",
    "node:20-alpine",
    "pgvector/pgvector:pg16",
    "redis:7-alpine",
    "opensearchproject/opensearch:2.11.1",
    "quay.io/minio/minio:RELEASE.2024-10-02T17-50-41Z"
)

Write-Host "`nPulling required Docker images..." -ForegroundColor Yellow
Write-Host "This may take 10-15 minutes depending on your connection" -ForegroundColor Cyan

$success = $true
foreach ($image in $images) {
    Write-Host "`nPulling: $image" -ForegroundColor Cyan
    docker pull $image
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to pull $image" -ForegroundColor Red
        $success = $false
    } else {
        Write-Host "Successfully pulled $image" -ForegroundColor Green
    }
}

if ($success) {
    Write-Host "`n$separator" -ForegroundColor Green
    Write-Host "All images pulled successfully!" -ForegroundColor Green
    Write-Host "Now you can run: .\deploy-auto.ps1" -ForegroundColor Yellow
    Write-Host $separator -ForegroundColor Green
} else {
    Write-Host "`n$separator" -ForegroundColor Red
    Write-Host "Some images failed to pull" -ForegroundColor Red
    Write-Host "Check your internet connection and try again" -ForegroundColor Yellow
    Write-Host $separator -ForegroundColor Red
    exit 1
}
