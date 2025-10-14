# Fix Docker Build Timeout
# This script increases Docker build timeout and retries

$separator = "=" * 80

Write-Host "FinancIA 2030 - Build with Extended Timeout" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan

# Set environment variables for Docker build
$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_HTTP_TIMEOUT = "300"
$env:DOCKER_CLIENT_TIMEOUT = "300"

Write-Host "`nConfigured extended timeouts (300s)" -ForegroundColor Green
Write-Host "DOCKER_BUILDKIT=1" -ForegroundColor Yellow
Write-Host "COMPOSE_HTTP_TIMEOUT=300" -ForegroundColor Yellow
Write-Host "DOCKER_CLIENT_TIMEOUT=300" -ForegroundColor Yellow

# Check Docker
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker not found!" -ForegroundColor Red
        exit 1
    }
    Write-Host "Docker found" -ForegroundColor Green
} catch {
    Write-Host "Docker not found!" -ForegroundColor Red
    exit 1
}

# Check GPU
Write-Host "`nChecking GPU support..." -ForegroundColor Yellow
$useGpu = $false
try {
    $output = docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "GPU support detected!" -ForegroundColor Green
        $useGpu = $true
    } else {
        Write-Host "GPU not available" -ForegroundColor Yellow
    }
} catch {
    Write-Host "GPU not available" -ForegroundColor Yellow
}

# Build with extended timeout
if ($useGpu) {
    Write-Host "`nBuilding with GPU support (extended timeout)..." -ForegroundColor Green
    Write-Host "This may take 10-15 minutes on first build..." -ForegroundColor Yellow
    
    docker-compose -f docker-compose.gpu.yml down 2>&1 | Out-Null
    docker-compose -f docker-compose.gpu.yml build --no-cache
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nBuild successful!" -ForegroundColor Green
        Write-Host "Starting services..." -ForegroundColor Cyan
        docker-compose -f docker-compose.gpu.yml up -d
        $containerName = "financia_backend_gpu"
    } else {
        Write-Host "`nBuild failed!" -ForegroundColor Red
        Write-Host "Try restarting Docker Desktop and run again" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "`nBuilding with CPU support (extended timeout)..." -ForegroundColor Yellow
    
    docker-compose down 2>&1 | Out-Null
    docker-compose build --no-cache
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nBuild successful!" -ForegroundColor Green
        Write-Host "Starting services..." -ForegroundColor Cyan
        docker-compose up -d
        $containerName = "financia_backend"
    } else {
        Write-Host "`nBuild failed!" -ForegroundColor Red
        exit 1
    }
}

# Wait and show status
Write-Host "`nWaiting for services..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`nService URLs:" -ForegroundColor Cyan
Write-Host "   - Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "   - Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   - API Docs:    http://localhost:8000/docs" -ForegroundColor White

if ($useGpu) {
    Write-Host "`nGPU Mode Active!" -ForegroundColor Green
    Write-Host "Check logs: docker logs $containerName" -ForegroundColor Yellow
}

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host $separator -ForegroundColor Cyan
