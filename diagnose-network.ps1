# Deep Network Diagnostics and Fix
# This script performs comprehensive network troubleshooting

Write-Host "Docker Network Deep Diagnostics" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check Docker is running
Write-Host "[1/8] Checking Docker status..." -ForegroundColor Yellow
$dockerRunning = wsl bash -c "docker info > /dev/null 2>&1 && echo 'OK' || echo 'FAIL'"
if ($dockerRunning -match "FAIL") {
    Write-Host "  Docker is not responding properly!" -ForegroundColor Red
    Write-Host "  Please restart Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}
Write-Host "  Docker is running" -ForegroundColor Green

# Test 2: Check basic connectivity
Write-Host ""
Write-Host "[2/8] Testing basic internet connectivity..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName 8.8.8.8 -Count 2 -Quiet
if ($pingResult) {
    Write-Host "  Internet connection: OK" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Cannot reach internet" -ForegroundColor Red
}

# Test 3: Test Docker Hub connectivity from Windows
Write-Host ""
Write-Host "[3/8] Testing Docker Hub from Windows..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://registry-1.docker.io" -TimeoutSec 5 -UseBasicParsing
    Write-Host "  Docker Hub accessible from Windows" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Cannot reach Docker Hub from Windows" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 4: Test Docker Hub from WSL
Write-Host ""
Write-Host "[4/8] Testing Docker Hub from WSL..." -ForegroundColor Yellow
$wslCurl = wsl bash -c "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://registry-1.docker.io 2>&1"
Write-Host "  WSL curl result: $wslCurl" -ForegroundColor White

# Test 5: Check WSL DNS
Write-Host ""
Write-Host "[5/8] Checking WSL DNS configuration..." -ForegroundColor Yellow
wsl bash -c "cat /etc/resolv.conf | grep nameserver"

# Test 6: Check if VPN is active
Write-Host ""
Write-Host "[6/8] Checking for active VPN..." -ForegroundColor Yellow
$vpnConnections = Get-VpnConnection -AllUserConnection -ErrorAction SilentlyContinue
if ($vpnConnections) {
    Write-Host "  VPN connections found - this may cause issues" -ForegroundColor Yellow
    $vpnConnections | ForEach-Object { Write-Host "    - $($_.Name): $($_.ConnectionStatus)" -ForegroundColor White }
} else {
    Write-Host "  No VPN detected" -ForegroundColor Green
}

# Test 7: Check Docker daemon configuration
Write-Host ""
Write-Host "[7/8] Checking Docker daemon config..." -ForegroundColor Yellow
$daemonConfig = wsl bash -c "test -f /etc/docker/daemon.json && cat /etc/docker/daemon.json || echo 'No config found'"
Write-Host "  $daemonConfig" -ForegroundColor White

# Test 8: Test pulling a small image
Write-Host ""
Write-Host "[8/8] Testing actual image pull (this may take a moment)..." -ForegroundColor Yellow
Write-Host "  Attempting to pull alpine:latest..." -ForegroundColor White
$pullResult = wsl bash -c "timeout 30 docker pull alpine:latest 2>&1 | tail -5"
Write-Host "$pullResult" -ForegroundColor White

Write-Host ""
Write-Host "===============================" -ForegroundColor Cyan
Write-Host "Diagnostics Complete" -ForegroundColor Cyan
Write-Host ""

# Provide recommendations
Write-Host "RECOMMENDATIONS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "If tests failed, try these solutions in order:" -ForegroundColor White
Write-Host "1. Disable VPN/Proxy temporarily" -ForegroundColor White
Write-Host "2. Run: .\fix-docker-network-advanced.ps1" -ForegroundColor White
Write-Host "3. Restart your computer" -ForegroundColor White
Write-Host "4. Use offline/cached deployment method" -ForegroundColor White
Write-Host ""
