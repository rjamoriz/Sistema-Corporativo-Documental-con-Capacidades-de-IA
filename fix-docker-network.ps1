# Fix Docker Network Issues - PowerShell Script
# Resolves TLS handshake timeout and Docker Hub connection issues

Write-Host "Docker Network Fix Script" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking Docker Desktop status..." -ForegroundColor Yellow

# Check if Docker Desktop is running
$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if ($null -eq $dockerProcess) {
    Write-Host "Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and wait for it to fully initialize." -ForegroundColor Yellow
    Write-Host "Then run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "Docker Desktop is running" -ForegroundColor Green
Write-Host ""

# Step 1: Restart Docker in WSL
Write-Host "Step 1: Restarting Docker service in WSL..." -ForegroundColor Yellow
wsl bash -c "sudo service docker restart"
Start-Sleep -Seconds 5

# Step 2: Test Docker connection
Write-Host ""
Write-Host "Step 2: Testing Docker connection..." -ForegroundColor Yellow
wsl bash -c "docker info > /dev/null 2>&1 && echo 'Docker is responding' || echo 'Docker not responding'"

# Step 3: Test network connectivity
Write-Host ""
Write-Host "Step 3: Testing Docker Hub connectivity..." -ForegroundColor Yellow
wsl bash -c "curl -I https://registry-1.docker.io 2>&1 | head -n 1"

# Step 4: Configure DNS (if needed)
Write-Host ""
Write-Host "Step 4: Configuring Docker DNS..." -ForegroundColor Yellow
wsl bash -c "sudo mkdir -p /etc/docker"
wsl bash -c 'echo ''{"dns": ["8.8.8.8", "8.8.4.4"]}'' | sudo tee /etc/docker/daemon.json > /dev/null'
wsl bash -c "sudo service docker restart"
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Network configuration updated!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Wait 10 seconds for Docker to fully restart" -ForegroundColor White
Write-Host "2. Run: .\deploy-gpu.ps1" -ForegroundColor White
Write-Host "3. If it still fails, restart Docker Desktop from Windows" -ForegroundColor White
Write-Host ""
