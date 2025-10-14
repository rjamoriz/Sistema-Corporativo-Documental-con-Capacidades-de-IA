# Fix Docker Cache Issues - PowerShell Script
# This script resolves Docker build cache corruption

Write-Host "Docker Cache Fix Script" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop all containers
Write-Host "Step 1: Stopping all containers..." -ForegroundColor Yellow
wsl bash -c "cd '/mnt/c/Users/rjamo/OneDrive/Desktop/IA GEN PROJECTS/Sistema Corporativo Documentacion AI-GPU boosted/Sistema-Corporativo-Documental-con-Capacidades-de-IA' && docker-compose down"

# Step 2: Clean Docker builder cache
Write-Host ""
Write-Host "Step 2: Cleaning Docker builder cache..." -ForegroundColor Yellow
wsl bash -c "docker builder prune -a -f"

# Step 3: Remove dangling images
Write-Host ""
Write-Host "Step 3: Removing dangling images..." -ForegroundColor Yellow
wsl bash -c "docker image prune -f"

# Step 4: Clean system
Write-Host ""
Write-Host "Step 4: Cleaning Docker system..." -ForegroundColor Yellow
wsl bash -c "docker system prune -f"

Write-Host ""
Write-Host "Docker cache cleaned successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Run deploy-gpu.ps1" -ForegroundColor White
Write-Host "2. Choose option 1 for GPU acceleration" -ForegroundColor White
Write-Host ""
