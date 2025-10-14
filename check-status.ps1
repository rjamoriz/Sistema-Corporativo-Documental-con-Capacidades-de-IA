# Quick Deployment Status Check

Write-Host "Deployment Status Check" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

# Check if deployment is running
Write-Host "Checking deployment progress..." -ForegroundColor Yellow
Write-Host ""

# Check container status
Write-Host "[1/3] Container Status:" -ForegroundColor Yellow
wsl bash -c "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo 'No containers running yet'"

Write-Host ""
Write-Host "[2/3] Recent Backend Logs:" -ForegroundColor Yellow
wsl bash -c "docker logs financia_backend_gpu --tail 10 2>/dev/null || echo 'Backend container not started yet'"

Write-Host ""
Write-Host "[3/3] Image Status:" -ForegroundColor Yellow
wsl bash -c "docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}' | grep -E 'REPOSITORY|financia|nvidia|node|postgres|minio|opensearch' || echo 'No images pulled yet'"

Write-Host ""
Write-Host "======================" -ForegroundColor Cyan

# Provide status interpretation
$containerCount = wsl bash -c "docker ps -q 2>/dev/null | wc -l"
if ($containerCount -ge 5) {
    Write-Host "Status: RUNNING - All containers are up!" -ForegroundColor Green
    Write-Host "Access: http://localhost:3000" -ForegroundColor Green
} elseif ($containerCount -gt 0) {
    Write-Host "Status: STARTING - Some containers are up" -ForegroundColor Yellow
    Write-Host "Wait a few more minutes..." -ForegroundColor Yellow
} else {
    Write-Host "Status: IN PROGRESS - Still building/pulling images" -ForegroundColor Yellow
    Write-Host "This can take 25-35 minutes on first run" -ForegroundColor Yellow
}

Write-Host ""
