# Advanced Docker Network Fix
# Applies multiple network fixes comprehensively

Write-Host "Advanced Docker Network Fix" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will apply multiple network fixes." -ForegroundColor Yellow
Write-Host "You may be prompted for WSL password multiple times." -ForegroundColor Yellow
Write-Host ""

# Fix 1: Update WSL DNS
Write-Host "[1/7] Configuring WSL DNS..." -ForegroundColor Yellow
wsl bash -c @"
echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf > /dev/null
echo 'nameserver 8.8.4.4' | sudo tee -a /etc/resolv.conf > /dev/null
echo 'nameserver 1.1.1.1' | sudo tee -a /etc/resolv.conf > /dev/null
"@
Write-Host "  DNS updated" -ForegroundColor Green

# Fix 2: Prevent resolv.conf from being overwritten
Write-Host ""
Write-Host "[2/7] Protecting DNS configuration..." -ForegroundColor Yellow
wsl bash -c "echo '[network]' | sudo tee /etc/wsl.conf > /dev/null"
wsl bash -c "echo 'generateResolvConf = false' | sudo tee -a /etc/wsl.conf > /dev/null"
Write-Host "  WSL config updated" -ForegroundColor Green

# Fix 3: Configure Docker daemon with multiple DNS servers
Write-Host ""
Write-Host "[3/7] Configuring Docker daemon DNS..." -ForegroundColor Yellow
wsl bash -c @"
echo '{
  \"dns\": [\"8.8.8.8\", \"8.8.4.4\", \"1.1.1.1\"],
  \"registry-mirrors\": [],
  \"insecure-registries\": [],
  \"debug\": false,
  \"experimental\": false
}' | sudo tee /etc/docker/daemon.json > /dev/null
"@
Write-Host "  Docker daemon config updated" -ForegroundColor Green

# Fix 4: Restart Docker in WSL
Write-Host ""
Write-Host "[4/7] Restarting Docker service..." -ForegroundColor Yellow
wsl bash -c "sudo service docker restart"
Start-Sleep -Seconds 5
Write-Host "  Docker restarted" -ForegroundColor Green

# Fix 5: Flush Windows DNS
Write-Host ""
Write-Host "[5/7] Flushing Windows DNS cache..." -ForegroundColor Yellow
ipconfig /flushdns | Out-Null
Write-Host "  Windows DNS flushed" -ForegroundColor Green

# Fix 6: Test connectivity
Write-Host ""
Write-Host "[6/7] Testing connectivity..." -ForegroundColor Yellow
$testResult = wsl bash -c "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://registry-1.docker.io"
if ($testResult -eq "200" -or $testResult -eq "301" -or $testResult -eq "302") {
    Write-Host "  Docker Hub is reachable (HTTP $testResult)" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Docker Hub connectivity issues (HTTP $testResult)" -ForegroundColor Yellow
}

# Fix 7: Quick image pull test
Write-Host ""
Write-Host "[7/7] Testing image pull..." -ForegroundColor Yellow
Write-Host "  Pulling alpine:latest (this may take a moment)..." -ForegroundColor White
$pullTest = wsl bash -c "timeout 45 docker pull alpine:latest 2>&1 | tail -3"
if ($pullTest -match "Downloaded" -or $pullTest -match "up to date" -or $pullTest -match "Status") {
    Write-Host "  Image pull successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "Network fix applied successfully!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: You must restart WSL for changes to take full effect:" -ForegroundColor Yellow
    Write-Host "  1. Close this PowerShell window" -ForegroundColor White
    Write-Host "  2. Run in NEW PowerShell window: wsl --shutdown" -ForegroundColor White
    Write-Host "  3. Wait 10 seconds" -ForegroundColor White
    Write-Host "  4. Run: .\deploy-gpu.ps1" -ForegroundColor White
} else {
    Write-Host "  WARNING: Image pull test failed" -ForegroundColor Yellow
    Write-Host "$pullTest" -ForegroundColor Red
    Write-Host ""
    Write-Host "Additional steps required:" -ForegroundColor Yellow
    Write-Host "1. Disable any VPN or proxy" -ForegroundColor White
    Write-Host "2. Run: wsl --shutdown" -ForegroundColor White
    Write-Host "3. Restart Docker Desktop" -ForegroundColor White
    Write-Host "4. Wait 2 minutes" -ForegroundColor White
    Write-Host "5. Try deployment again" -ForegroundColor White
}

Write-Host ""
