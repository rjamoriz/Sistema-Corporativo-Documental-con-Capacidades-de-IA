# GPU Deployment Scripts for FinancIA 2030

$separator = "=" * 80

Write-Host "FinancIA 2030 - GPU Deployment" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan

# Verificar Docker
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
docker --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker not found! Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verificar soporte GPU
Write-Host "`nChecking GPU support..." -ForegroundColor Yellow
$gpuTest = docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: GPU not detected or NVIDIA Container Toolkit not installed!" -ForegroundColor Yellow
    Write-Host "Continuing with CPU-only build..." -ForegroundColor Yellow
    $useGpu = $false
} else {
    Write-Host "GPU support confirmed!" -ForegroundColor Green
    $useGpu = $true
}

# Preguntar qué configuración usar
Write-Host "`nSelect deployment configuration:" -ForegroundColor Cyan
Write-Host "1. GPU-accelerated (Dockerfile.backend.gpu)" -ForegroundColor White
Write-Host "2. CPU-only (Dockerfile.backend)" -ForegroundColor White
$choice = Read-Host "Enter choice (1 or 2)"

if ($choice -eq "1") {
    if ($useGpu) {
        Write-Host "`nBuilding with GPU support..." -ForegroundColor Green
        docker-compose -f docker-compose.gpu.yml build
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Build successful!" -ForegroundColor Green
            Write-Host "`nStarting services with GPU..." -ForegroundColor Cyan
            docker-compose -f docker-compose.gpu.yml up -d
        }
    } else {
        Write-Host "`nGPU not available! Building with CPU support instead..." -ForegroundColor Yellow
        docker-compose build
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Build successful!" -ForegroundColor Green
            Write-Host "`nStarting services..." -ForegroundColor Cyan
            docker-compose up -d
        }
    }
} else {
    Write-Host "`nBuilding with CPU support..." -ForegroundColor Yellow
    docker-compose build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build successful!" -ForegroundColor Green
        Write-Host "`nStarting services..." -ForegroundColor Cyan
        docker-compose up -d
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDeployment complete!" -ForegroundColor Green
    Write-Host "`nService URLs:" -ForegroundColor Cyan
    Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "   - Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   - MinIO Console: http://localhost:9001" -ForegroundColor White
    if ($choice -eq "1") {
        Write-Host "`nTip: Run 'docker logs financia_backend_gpu' to check GPU status" -ForegroundColor Yellow
    } else {
        Write-Host "`nTip: Run 'docker logs financia_backend' to check status" -ForegroundColor Yellow
    }
} else {
    Write-Host "`nDeployment failed!" -ForegroundColor Red
    exit 1
}
