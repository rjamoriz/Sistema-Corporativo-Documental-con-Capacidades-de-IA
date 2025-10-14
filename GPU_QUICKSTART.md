# 🚀 Quick Start - GPU Accelerated

## ⚡ TL;DR - Start in 3 steps

```bash
# 1. Deploy con GPU
./deploy-gpu.sh

# 2. Verificar GPU
./test-gpu.sh

# 3. Acceder
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

---

## 📋 Prerequisitos

✅ Tu sistema YA TIENE todo configurado:
- GPU: NVIDIA GeForce RTX 4070 ✅
- CUDA: 12.8 ✅
- Docker: GPU support ✅
- WSL2: Configurado ✅

---

## 🎯 Opción 1: Despliegue Completo (Recomendado)

### En WSL/Linux:
```bash
# Hacer ejecutable (solo primera vez)
chmod +x deploy-gpu.sh test-gpu.sh

# Desplegar
./deploy-gpu.sh

# El script te preguntará:
# 1. GPU-accelerated (Dockerfile.backend.gpu)  ← Elige esta
# 2. CPU-only (Dockerfile.backend)
```

### En PowerShell (Windows):
```powershell
# Ejecutar
.\deploy-gpu.ps1

# Elegir opción 1 cuando pregunte
```

---

## 🧪 Opción 2: Test Rápido

```bash
# Solo verificar que GPU funciona
./test-gpu.sh  # o .\test-gpu.ps1

# Verás:
# ✅ Docker can access GPU
# ✅ Backend container running
# ✅ GPU working inside container
```

---

## 🐳 Opción 3: Docker Compose Manual

```bash
# Con GPU (Recomendado)
docker-compose -f docker-compose.gpu.yml build
docker-compose -f docker-compose.gpu.yml up -d

# Verificar logs
docker logs financia_backend_gpu

# Deberías ver:
# ✅ GPU detected: NVIDIA GeForce RTX 4070 (7.79GB)
# ✅ CUDA available: True
```

---

## 📊 Verificación Post-Deploy

### 1. Ver logs del backend
```bash
docker logs financia_backend_gpu
```

Busca estas líneas:
```
🔍 GPU VERIFICATION FOR FINANCIA 2030
✅ PyTorch version: 2.1.0+cu121
✅ CUDA available: True
✅ GPU device: NVIDIA GeForce RTX 4070
```

### 2. Monitorear GPU en tiempo real
```bash
# En otra terminal
watch -n 1 nvidia-smi
```

### 3. Test de la API
```bash
# Health check
curl http://localhost:8000/health

# Docs interactivos
# Abrir navegador: http://localhost:8000/docs
```

---

## 🎯 URLs de Acceso

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Frontend** | http://localhost:3000 | admin.demo / Demo2025! |
| **Backend API** | http://localhost:8000/docs | - |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **OpenSearch** | http://localhost:9200 | - |

---

## ⚡ Performance Esperado

Con GPU activada verás estas mejoras:

| Operación | Tiempo (GPU) | vs CPU |
|-----------|--------------|--------|
| Embeddings 100 docs | ~6s | 7.5x más rápido |
| Clasificación batch | ~2s | 6x más rápido |
| OCR 20 páginas | ~10s | 3x más rápido |

---

## 🛑 Detener Servicios

```bash
# Con GPU
docker-compose -f docker-compose.gpu.yml down

# Sin GPU
docker-compose down

# Detener y limpiar volúmenes
docker-compose -f docker-compose.gpu.yml down -v
```

---

## 🐛 Si algo falla

### GPU no detectada
```bash
# Verificar en host
nvidia-smi

# Verificar Docker
docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi

# Si falla, reiniciar Docker
# En Windows: Restart Docker Desktop
# En Linux: sudo systemctl restart docker
```

### Container no inicia
```bash
# Ver logs completos
docker logs financia_backend_gpu --tail 100

# Ver errores específicos
docker logs financia_backend_gpu 2>&1 | grep -i error
```

### Puerto ocupado
```bash
# Ver qué usa el puerto 8000
lsof -i :8000  # Linux
netstat -ano | findstr :8000  # Windows

# Cambiar puerto en docker-compose.gpu.yml
ports:
  - "8001:8000"  # Usar 8001 en host
```

---

## 📚 Más Información

- 📖 [`GPU_ACCELERATION_GUIDE.md`](./GPU_ACCELERATION_GUIDE.md) - Guía completa
- 📋 [`GPU_SETUP_SUMMARY.md`](./GPU_SETUP_SUMMARY.md) - Resumen técnico
- 🐳 [`DOCKER_SETUP_LOCAL.md`](./DOCKER_SETUP_LOCAL.md) - Setup Docker
- 🚀 [`QUICKSTART.md`](./QUICKSTART.md) - Guía general

---

## ✅ Checklist

- [ ] Ejecutar `./deploy-gpu.sh` o `.\deploy-gpu.ps1`
- [ ] Verificar logs: `docker logs financia_backend_gpu`
- [ ] Confirmar GPU detectada en logs
- [ ] Acceder a frontend: http://localhost:3000
- [ ] Login con admin.demo / Demo2025!
- [ ] Subir documento de prueba
- [ ] Verificar clasificación rápida (GPU working!)

---

## 🎉 ¡Listo!

Tu sistema **FinancIA 2030** con **GPU acceleration** está funcionando.

**Disfruta de la velocidad!** 🚀⚡

¿Preguntas? Revisa [`GPU_ACCELERATION_GUIDE.md`](./GPU_ACCELERATION_GUIDE.md)
