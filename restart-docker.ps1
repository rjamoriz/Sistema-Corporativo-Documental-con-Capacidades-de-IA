# Simple Docker Desktop Restart Script
# This resolves most network issues

Write-Host "Restarting Docker Desktop..." -ForegroundColor Cyan
Write-Host ""

# Stop Docker Desktop
Write-Host "Stopping Docker Desktop..." -ForegroundColor Yellow
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# Wait for processes to fully stop
$maxAttempts = 10
$attempt = 0
while ((Get-Process "Docker Desktop" -ErrorAction SilentlyContinue) -and ($attempt -lt $maxAttempts)) {
    Write-Host "Waiting for Docker to stop..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    $attempt++
}

# Start Docker Desktop
Write-Host ""
Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

Write-Host ""
Write-Host "Docker Desktop is starting..." -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT:" -ForegroundColor Yellow
Write-Host "Wait for Docker Desktop to fully initialize (30-60 seconds)" -ForegroundColor White
Write-Host "Look for the Docker icon in system tray to turn steady green" -ForegroundColor White
Write-Host ""
Write-Host "Then run: .\deploy-gpu.ps1" -ForegroundColor Cyan
Write-Host ""
