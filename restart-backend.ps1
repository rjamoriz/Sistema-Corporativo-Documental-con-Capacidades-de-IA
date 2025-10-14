# Script to restart backend with full synthetic data service
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Restarting Backend with Full Synthetic Data Service" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Stop backend container
Write-Host "Stopping backend container..." -ForegroundColor Yellow
docker-compose stop backend

# Rebuild backend (optional - uncomment if you want to rebuild)
# Write-Host "Rebuilding backend..." -ForegroundColor Yellow
# docker-compose build backend

# Start backend
Write-Host "Starting backend..." -ForegroundColor Green
docker-compose up -d backend

# Wait a few seconds for the container to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Show logs
Write-Host ""
Write-Host "Backend logs (press Ctrl+C to stop):" -ForegroundColor Cyan
docker-compose logs -f backend
