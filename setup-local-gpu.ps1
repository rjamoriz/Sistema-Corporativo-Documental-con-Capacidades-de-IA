# FinancIA 2030 - Setup Automático con Docker Desktop + GPU
# Script para Windows PowerShell

Write-Host "🚀 FinancIA 2030 - Setup Automático con GPU" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Verificar que estamos en el directorio correcto
if (!(Test-Path "docker-compose.yml")) {
    Write-Host "❌ Error: No se encuentra docker-compose.yml" -ForegroundColor Red
    Write-Host "💡 Ejecuta este script desde la raíz del proyecto" -ForegroundColor Yellow
    exit 1
}

# Función para verificar comandos
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Verificar prerrequisitos
Write-Host "🔍 Verificando prerrequisitos..." -ForegroundColor Cyan

# Docker
if (!(Test-Command "docker")) {
    Write-Host "❌ Docker no está instalado" -ForegroundColor Red
    Write-Host "💡 Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Docker encontrado" -ForegroundColor Green
docker --version

# Docker Compose
if (!(Test-Command "docker-compose")) {
    Write-Host "❌ Docker Compose no está disponible" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker Compose encontrado" -ForegroundColor Green
docker-compose --version

# Verificar GPU NVIDIA
Write-Host "`n🎮 Verificando GPU NVIDIA..." -ForegroundColor Cyan
if (Test-Command "nvidia-smi") {
    Write-Host "✅ NVIDIA GPU detectada" -ForegroundColor Green
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits
} else {
    Write-Host "⚠️ nvidia-smi no encontrado. GPU no será usada." -ForegroundColor Yellow
}

# Verificar archivo .env
Write-Host "`n⚙️ Configurando variables de entorno..." -ForegroundColor Cyan
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "📄 Copiando .env.example a .env..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Archivo .env creado" -ForegroundColor Green
        Write-Host "💡 IMPORTANTE: Edita el archivo .env con tus configuraciones" -ForegroundColor Yellow
        Write-Host "   - OPENAI_API_KEY=tu-clave-aqui" -ForegroundColor Yellow
        Write-Host "   - Otros settings según necesites" -ForegroundColor Yellow
    } else {
        Write-Host "❌ No se encuentra .env.example" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Archivo .env encontrado" -ForegroundColor Green
}

# Configurar Docker Desktop para performance
Write-Host "`n🐳 Configuración de Docker Desktop..." -ForegroundColor Cyan
Write-Host "💡 Asegúrate de que Docker Desktop tenga configurado:" -ForegroundColor Yellow
Write-Host "   - Memory: 12 GB (mínimo 8 GB)" -ForegroundColor Yellow
Write-Host "   - CPUs: 4 (mínimo 2)" -ForegroundColor Yellow
Write-Host "   - Swap: 2 GB" -ForegroundColor Yellow

# Preguntar si continuar
$continuar = Read-Host "`n¿Continuar con el setup? (s/N)"
if ($continuar -ne "s" -and $continuar -ne "S") {
    Write-Host "❌ Setup cancelado" -ForegroundColor Red
    exit 0
}

# Limpiar contenedores anteriores
Write-Host "`n🧹 Limpiando contenedores anteriores..." -ForegroundColor Cyan
docker-compose down -v --remove-orphans 2>$null
docker system prune -f 2>$null

# Construir e iniciar servicios
Write-Host "`n🔨 Construyendo e iniciando servicios..." -ForegroundColor Cyan
Write-Host "⏳ Esto puede tomar 10-15 minutos la primera vez..." -ForegroundColor Yellow

$build_start = Get-Date
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    $build_end = Get-Date
    $build_time = ($build_end - $build_start).TotalMinutes
    Write-Host "✅ Servicios iniciados exitosamente en $([math]::Round($build_time, 1)) minutos" -ForegroundColor Green
} else {
    Write-Host "❌ Error iniciando servicios" -ForegroundColor Red
    Write-Host "💡 Revisa los logs con: docker-compose logs" -ForegroundColor Yellow
    exit 1
}

# Esperar a que los servicios estén listos
Write-Host "`n⏳ Esperando a que los servicios estén listos..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Verificar estado de servicios
Write-Host "`n📋 Estado de los servicios:" -ForegroundColor Cyan
docker-compose ps

# Verificar health checks
Write-Host "`n🏥 Verificando health checks..." -ForegroundColor Cyan
$services = @("postgres", "redis", "backend", "frontend", "minio")
$all_healthy = $true

foreach ($service in $services) {
    $health = docker-compose ps --format json | ConvertFrom-Json | Where-Object { $_.Service -eq $service } | Select-Object -ExpandProperty State
    if ($health -like "*healthy*" -or $health -like "*running*") {
        Write-Host "✅ $service - OK" -ForegroundColor Green
    } else {
        Write-Host "❌ $service - $health" -ForegroundColor Red
        $all_healthy = $false
    }
}

if ($all_healthy) {
    Write-Host "`n🎉 ¡Setup completado exitosamente!" -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host "🌐 Accesos:" -ForegroundColor Cyan
    Write-Host "   Frontend:      http://localhost:3000" -ForegroundColor White
    Write-Host "   Backend API:   http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   MinIO Console: http://localhost:9001" -ForegroundColor White
    Write-Host "   GPU Monitor:   http://localhost:8000/docs#/Machine%20Learning" -ForegroundColor White
    
    Write-Host "`n📊 Credenciales de prueba:" -ForegroundColor Cyan
    Write-Host "   Usuario: admin.demo" -ForegroundColor White
    Write-Host "   Password: Demo2025!" -ForegroundColor White
    
    Write-Host "`n🔧 Comandos útiles:" -ForegroundColor Cyan
    Write-Host "   Ver logs:      docker-compose logs -f" -ForegroundColor White
    Write-Host "   Parar todo:    docker-compose down" -ForegroundColor White
    Write-Host "   Reiniciar:     docker-compose restart" -ForegroundColor White
    Write-Host "   GPU test:      docker-compose exec backend python -c 'import torch; print(torch.cuda.is_available())'" -ForegroundColor White
    
} else {
    Write-Host "`n⚠️ Algunos servicios no están funcionando correctamente" -ForegroundColor Yellow
    Write-Host "💡 Revisa los logs: docker-compose logs [servicio]" -ForegroundColor Yellow
}

Write-Host "`n🚀 ¡Listo para usar FinancIA 2030!" -ForegroundColor Green
