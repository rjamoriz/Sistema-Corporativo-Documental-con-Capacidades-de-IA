# Quick GPU test script (PowerShell)

$separator = "=" * 40

Write-Host "Quick GPU Test for FinancIA 2030" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan

# Test 1: Docker GPU access
Write-Host "`nTest 1: Docker GPU Access" -ForegroundColor Yellow
Write-Host "-------------------------" -ForegroundColor Yellow
docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi

if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker can access GPU" -ForegroundColor Green
} else {
    Write-Host "Docker cannot access GPU" -ForegroundColor Red
    exit 1
}

# Test 2: Check if backend container is running
Write-Host "`nTest 2: Backend Container Status" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
$container = docker ps --filter "name=financia_backend" --format "{{.Names}}"

if ($container) {
    Write-Host "Backend container running: $container" -ForegroundColor Green
    
    # Test 3: GPU verification inside container
    Write-Host "`nTest 3: GPU Status Inside Container" -ForegroundColor Yellow
    Write-Host "-----------------------------------" -ForegroundColor Yellow
    docker exec $container python check_gpu.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "GPU working inside container" -ForegroundColor Green
    } else {
        Write-Host "GPU not detected inside container" -ForegroundColor Yellow
    }
} else {
    Write-Host "Backend container not running" -ForegroundColor Yellow
    Write-Host "Run: docker-compose up -d" -ForegroundColor White
}

Write-Host "`n$separator" -ForegroundColor Cyan
Write-Host "Test complete!" -ForegroundColor Green
