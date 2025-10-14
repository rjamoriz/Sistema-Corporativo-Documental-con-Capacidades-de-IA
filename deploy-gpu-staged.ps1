# Deploy with Pre-pulled Images
# This method pulls images first, then builds, avoiding timeout during build

Write-Host "FinancIA 2030 - Staged GPU Deployment" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This method pulls base images first to avoid timeouts during build." -ForegroundColor Yellow
Write-Host ""

# Step 1: Pre-pull base images
Write-Host "Stage 1: Pre-pulling base images..." -ForegroundColor Yellow
Write-Host "This may take 10-15 minutes depending on your connection." -ForegroundColor White
Write-Host ""

$images = @(
    "nvidia/cuda:12.6.0-runtime-ubuntu22.04",
    "node:20-alpine",
    "postgres:15-alpine",
    "minio/minio:latest",
    "opensearchproject/opensearch:2.11.0"
)

$pullSuccess = $true
$imageNum = 1
foreach ($image in $images) {
    Write-Host "[$imageNum/$($images.Count)] Pulling $image..." -ForegroundColor Cyan
    
    # Use longer timeout and retry logic
    $maxRetries = 3
    $retry = 0
    $pulled = $false
    
    while (-not $pulled -and $retry -lt $maxRetries) {
        if ($retry -gt 0) {
            Write-Host "  Retry $retry/$maxRetries..." -ForegroundColor Yellow
        }
        
        $result = wsl bash -c "timeout 300 docker pull $image 2>&1"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Success!" -ForegroundColor Green
            $pulled = $true
        } else {
            $retry++
            if ($retry -lt $maxRetries) {
                Write-Host "  Failed, retrying in 10 seconds..." -ForegroundColor Yellow
                Start-Sleep -Seconds 10
            }
        }
    }
    
    if (-not $pulled) {
        Write-Host "  FAILED after $maxRetries attempts" -ForegroundColor Red
        $pullSuccess = $false
    }
    
    $imageNum++
    Write-Host ""
}

if (-not $pullSuccess) {
    Write-Host "================================" -ForegroundColor Red
    Write-Host "Image pull failed!" -ForegroundColor Red
    Write-Host "================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try these solutions:" -ForegroundColor Yellow
    Write-Host "1. Check your internet connection" -ForegroundColor White
    Write-Host "2. Disable VPN/Proxy" -ForegroundColor White
    Write-Host "3. Run: .\fix-docker-network-advanced.ps1" -ForegroundColor White
    Write-Host "4. Run: wsl --shutdown" -ForegroundColor White
    Write-Host "5. Restart Docker Desktop" -ForegroundColor White
    Write-Host "6. Try this script again" -ForegroundColor White
    exit 1
}

# Step 2: Build images
Write-Host "Stage 2: Building application images..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Building backend with GPU support..." -ForegroundColor Cyan
$buildCmd = "cd '/mnt/c/Users/rjamo/OneDrive/Desktop/IA GEN PROJECTS/Sistema Corporativo Documentacion AI-GPU boosted/Sistema-Corporativo-Documental-con-Capacidades-de-IA' && docker-compose -f docker-compose.gpu.yml build --no-cache backend"
wsl bash -c $buildCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Building frontend..." -ForegroundColor Cyan
$buildCmd = "cd '/mnt/c/Users/rjamo/OneDrive/Desktop/IA GEN PROJECTS/Sistema Corporativo Documentacion AI-GPU boosted/Sistema-Corporativo-Documental-con-Capacidades-de-IA' && docker-compose -f docker-compose.gpu.yml build --no-cache frontend"
wsl bash -c $buildCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Start services
Write-Host ""
Write-Host "Stage 3: Starting services..." -ForegroundColor Yellow
$startCmd = "cd '/mnt/c/Users/rjamo/OneDrive/Desktop/IA GEN PROJECTS/Sistema Corporativo Documentacion AI-GPU boosted/Sistema-Corporativo-Documental-con-Capacidades-de-IA' && docker-compose -f docker-compose.gpu.yml up -d"
wsl bash -c $startCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "Deployment successful!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Services are starting up..." -ForegroundColor Yellow
    Write-Host "Wait 2-3 minutes for initialization." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Access your application:" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend:  http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "Default credentials:" -ForegroundColor Cyan
    Write-Host "  Username: admin.demo" -ForegroundColor White
    Write-Host "  Password: Demo2025!" -ForegroundColor White
    Write-Host ""
    Write-Host "Check logs:" -ForegroundColor Cyan
    Write-Host "  wsl bash -c 'docker logs financia_backend_gpu --tail 50'" -ForegroundColor White
} else {
    Write-Host "Service startup failed!" -ForegroundColor Red
    exit 1
}
