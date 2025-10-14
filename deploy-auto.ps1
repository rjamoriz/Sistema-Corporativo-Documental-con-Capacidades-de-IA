# Simple GPU Deployment - Auto mode
# Automatically detects GPU and uses appropriate configuration

$separator = "=" * 80

Write-Host "FinancIA 2030 - Auto GPU Deployment" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan

# Check Docker
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker not found! Please install Docker Desktop." -ForegroundColor Red
        exit 1
    }
    Write-Host "Docker found" -ForegroundColor Green
} catch {
    Write-Host "Docker not found! Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check GPU support
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

# Deploy based on GPU availability
if ($useGpu) {
    Write-Host "`nDeploying with GPU acceleration..." -ForegroundColor Green
    Write-Host "Using: docker-compose.gpu.yml" -ForegroundColor Cyan
    
    docker-compose -f docker-compose.gpu.yml down 2>&1 | Out-Null
    docker-compose -f docker-compose.gpu.yml build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build successful!" -ForegroundColor Green
        docker-compose -f docker-compose.gpu.yml up -d
        $containerName = "financia_backend_gpu"
    } else {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`nDeploying with CPU mode..." -ForegroundColor Yellow
    Write-Host "Using: docker-compose.yml" -ForegroundColor Cyan
    
    docker-compose down 2>&1 | Out-Null
    docker-compose build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build successful!" -ForegroundColor Green
        docker-compose up -d
        $containerName = "financia_backend"
    } else {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
}

# Wait for services to start
Write-Host "`nWaiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Show status
Write-Host "`nDeployment Status:" -ForegroundColor Cyan
docker-compose ps

# Show URLs
Write-Host "`nService URLs:" -ForegroundColor Cyan
Write-Host "   - Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "   - Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   - API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - MinIO:       http://localhost:9001" -ForegroundColor White

# Show GPU status
if ($useGpu) {
    Write-Host "`nGPU Mode Active!" -ForegroundColor Green
    Write-Host "   Check GPU status: docker logs $containerName" -ForegroundColor Yellow
} else {
    Write-Host "`nCPU Mode Active" -ForegroundColor Yellow
}

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host $separator -ForegroundColor Cyan
