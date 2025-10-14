# 🎮 Comandos Esenciales - GPU Setup

## 🚀 Despliegue

### Linux/WSL
```bash
# Desplegar con GPU
./deploy-gpu.sh

# Desplegar sin GPU (fallback)
docker-compose up -d
```

### PowerShell
```powershell
# Desplegar con GPU
.\deploy-gpu.ps1

# Desplegar sin GPU (fallback)
docker-compose up -d
```

---

## 🔍 Verificación

```bash
# Test rápido GPU
./test-gpu.sh                    # Linux/WSL
.\test-gpu.ps1                   # PowerShell

# Verificar GPU en host
nvidia-smi

# Verificar GPU en Docker
docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi

# Ver logs del backend
docker logs financia_backend_gpu

# Ver solo mensajes de GPU
docker logs financia_backend_gpu | grep -i gpu

# Verificar GPU desde dentro del container
docker exec -it financia_backend_gpu python check_gpu.py
```

---

## 📊 Monitoreo

```bash
# Monitoreo continuo de GPU
watch -n 1 nvidia-smi

# Ver logs en tiempo real
docker logs -f financia_backend_gpu

# Ver estadísticas del container
docker stats financia_backend_gpu

# Listar containers
docker ps
```

---

## 🛑 Control de Servicios

```bash
# Detener servicios (GPU)
docker-compose -f docker-compose.gpu.yml down

# Detener servicios (normal)
docker-compose down

# Reiniciar backend GPU
docker-compose -f docker-compose.gpu.yml restart backend

# Ver estado de servicios
docker-compose ps
```

---

## 🔧 Troubleshooting

```bash
# Reiniciar Docker
sudo systemctl restart docker           # Linux
# En Windows: Restart Docker Desktop

# Limpiar y reconstruir
docker-compose -f docker-compose.gpu.yml down -v
docker-compose -f docker-compose.gpu.yml build --no-cache
docker-compose -f docker-compose.gpu.yml up -d

# Ver logs de errores
docker logs financia_backend_gpu 2>&1 | grep -i error

# Inspeccionar container
docker inspect financia_backend_gpu

# Entrar al container
docker exec -it financia_backend_gpu bash
```

---

## 🧪 Testing

```bash
# Test de GPU
docker exec financia_backend_gpu python check_gpu.py

# Test de la API
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Test de clasificación (ejemplo)
curl -X POST http://localhost:8000/api/v1/documents/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Factura de compra"}'
```

---

## 📦 Build & Push (DockerHub)

```bash
# Build imagen GPU
docker build -t tuusuario/financia-backend-gpu:latest -f Dockerfile.backend.gpu .

# Tag
docker tag tuusuario/financia-backend-gpu:latest tuusuario/financia-backend-gpu:1.0-gpu

# Push
docker push tuusuario/financia-backend-gpu:latest
docker push tuusuario/financia-backend-gpu:1.0-gpu
```

---

## 🌐 Acceso URLs

```bash
# Abrir en navegador
# Frontend
start http://localhost:3000              # Windows
xdg-open http://localhost:3000           # Linux

# Backend API Docs
start http://localhost:8000/docs         # Windows
xdg-open http://localhost:8000/docs      # Linux

# MinIO Console
start http://localhost:9001              # Windows
xdg-open http://localhost:9001           # Linux
```

---

## 📝 Logs

```bash
# Ver logs de todos los servicios
docker-compose -f docker-compose.gpu.yml logs

# Ver logs de un servicio específico
docker-compose -f docker-compose.gpu.yml logs backend

# Últimas 100 líneas
docker logs financia_backend_gpu --tail 100

# Logs desde hace 10 minutos
docker logs financia_backend_gpu --since 10m
```

---

## 🧹 Limpieza

```bash
# Limpiar containers detenidos
docker container prune

# Limpiar imágenes no usadas
docker image prune

# Limpiar volúmenes no usados
docker volume prune

# Limpiar todo (cuidado!)
docker system prune -a --volumes
```

---

## ⚙️ Variables de Entorno

```bash
# Editar .env
nano backend/.env                        # Linux
notepad backend/.env                     # Windows

# Variables importantes:
USE_GPU=true
CUDA_VISIBLE_DEVICES=0
OPENAI_API_KEY=tu_key_aqui
```

---

## 🎯 Quick Reference

| Acción | Comando |
|--------|---------|
| Deploy GPU | `./deploy-gpu.sh` |
| Test GPU | `./test-gpu.sh` |
| Ver GPU | `nvidia-smi` |
| Logs backend | `docker logs financia_backend_gpu` |
| Stop | `docker-compose down` |
| Restart | `docker-compose restart backend` |

---

## 💡 Tips

```bash
# Crear alias útiles (añadir a ~/.bashrc o ~/.zshrc)
alias dps='docker ps'
alias dlogs='docker logs -f financia_backend_gpu'
alias dgpu='nvidia-smi'
alias dtest='./test-gpu.sh'
alias ddeploy='./deploy-gpu.sh'

# Recargar shell
source ~/.bashrc
```

---

## 📚 Más Ayuda

- Ver `GPU_QUICKSTART.md` - Inicio rápido
- Ver `GPU_ACCELERATION_GUIDE.md` - Guía completa
- Ver `GPU_SETUP_SUMMARY.md` - Resumen técnico
