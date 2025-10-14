# 🔧 Network Troubleshooting - Docker Build Timeout

## ❌ Error Recibido

```
net/http: TLS handshake timeout
failed to do request: Head "https://registry-1.docker.io/..."
```

Este error indica problemas de conectividad entre Docker y Docker Hub.

---

## ✅ Soluciones (en orden de efectividad)

### **Solución 1: Usar WSL (MÁS EFECTIVO)** ⭐

WSL tiene mejor conectividad con Docker Hub en Windows:

```bash
# Abrir WSL
wsl

# Navegar al directorio del proyecto
cd "/mnt/c/Users/rjamo/OneDrive/Desktop/IA GEN PROJECTS/Sistema Corporativo Documentacion AI-GPU boosted/Sistema-Corporativo-Documental-con-Capacidades-de-IA"

# Hacer ejecutables
chmod +x deploy-gpu.sh test-gpu.sh

# Desplegar
./deploy-gpu.sh
```

**Ventajas:**
- ✅ Mejor conectividad de red
- ✅ Sin problemas de TLS handshake
- ✅ Más rápido generalmente
- ✅ Mejor integración con Docker

---

### **Solución 2: Configurar DNS de Docker**

Configurar DNS más confiables en Docker Desktop:

1. **Abrir Docker Desktop**
2. **Settings → Docker Engine**
3. **Agregar configuración DNS:**

```json
{
  "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]
}
```

4. **Apply & Restart**
5. **Reintentar:**
```powershell
.\deploy-auto.ps1
```

---

### **Solución 3: Reiniciar Servicios de Red**

En PowerShell como Administrador:

```powershell
# Reiniciar Docker Desktop
Restart-Service docker

# O manualmente: Docker Desktop → Restart

# Limpiar DNS de Windows
ipconfig /flushdns

# Reintentar
.\deploy-auto.ps1
```

---

### **Solución 4: Usar VPN o cambiar Red**

Si estás en una red corporativa/universitaria:

- Cambiar a red móvil (hotspot)
- Usar VPN diferente
- Desactivar VPN si está activa
- Cambiar de WiFi a Ethernet o viceversa

---

### **Solución 5: Descargar Imágenes Manualmente**

Descargar solo las imágenes que funcionaron y usar local builds:

```powershell
# Ya tienes estas imágenes:
# ✅ pgvector/pgvector:pg16
# ✅ redis:7-alpine
# ✅ opensearchproject/opensearch:2.11.1

# Intentar descargar las faltantes una por una con retries
docker pull nvidia/cuda:12.6.0-runtime-ubuntu22.04
docker pull node:20-alpine

# Si siguen fallando, usar versiones alternativas
docker pull nvidia/cuda:12.1.0-runtime-ubuntu22.04  # Versión anterior
docker pull node:18-alpine  # Versión LTS anterior
```

---

### **Solución 6: Modificar Dockerfiles para usar imágenes locales**

Si algunas imágenes no se descargan, usar alternativas:

**Para Backend (Dockerfile.backend.gpu):**

```dockerfile
# Si nvidia/cuda:12.6.0 falla, usar:
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04
# o
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
```

**Para Frontend (Dockerfile.frontend):**

```dockerfile
# Si node:20-alpine falla, usar:
FROM node:18-alpine
# o
FROM node:20-slim
```

---

### **Solución 7: Usar Docker Mirror (China/Asia)**

Si estás en Asia o tienes problemas con Docker Hub:

En Docker Desktop → Settings → Docker Engine:

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

---

### **Solución 8: Aumentar Timeout del Sistema**

En PowerShell:

```powershell
# Variables de entorno
$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_HTTP_TIMEOUT = "600"
$env:DOCKER_CLIENT_TIMEOUT = "600"

# Reintentar
.\deploy-with-timeout.ps1
```

---

### **Solución 9: Desactivar Temporalmente Firewall/Antivirus**

Algunos firewall/antivirus bloquean TLS handshakes de Docker:

1. Desactivar temporalmente Windows Defender Firewall
2. Desactivar antivirus de terceros
3. Reintentar build
4. Reactivar después

---

### **Solución 10: Modo Offline (Usar imágenes existentes)**

Si ya tienes imágenes locales, podemos construir sin pull:

```powershell
# Ver imágenes locales
docker images

# Build solo con imágenes locales
docker-compose -f docker-compose.yml build --no-cache
```

---

## 🎯 **Recomendación Actual**

**Dado tu caso específico, te recomiendo:**

### **Opción A: WSL (Ya en ejecución)**

El deploy desde WSL ya está corriendo. Espera a que termine y verifica:

```bash
# Ver si está corriendo
docker ps

# Ver logs
docker logs financia_backend_gpu
```

### **Opción B: Si WSL también falla**

1. **Cambiar a red móvil** (hotspot de teléfono)
2. **Configurar DNS en Docker** (8.8.8.8, 8.8.4.4)
3. **Reintentar desde WSL:**

```bash
wsl
cd "/mnt/c/Users/rjamo/OneDrive/Desktop/IA GEN PROJECTS/Sistema Corporativo Documentacion AI-GPU boosted/Sistema-Corporativo-Documental-con-Capacidades-de-IA"
./deploy-gpu.sh
```

---

## 📊 **Status de Imágenes**

| Imagen | Estado | Acción |
|--------|--------|--------|
| pgvector/pgvector:pg16 | ✅ Descargada | OK |
| redis:7-alpine | ✅ Descargada | OK |
| opensearchproject/opensearch:2.11.1 | ✅ Descargada | OK |
| nvidia/cuda:12.6.0-runtime-ubuntu22.04 | ❌ Timeout | Usar WSL o VPN |
| node:20-alpine | ❌ Timeout | Usar WSL o VPN |
| minio:RELEASE.2024-10-02 | ❌ Timeout | Usar WSL o VPN |

---

## 🔍 **Diagnóstico de Red**

Para verificar conectividad:

```powershell
# Test Docker Hub
Test-NetConnection registry-1.docker.io -Port 443

# Test DNS
nslookup registry-1.docker.io

# Test ping
ping registry-1.docker.io
```

---

## ✅ **Próximos Pasos**

1. ✅ **WSL Deploy en ejecución** - Esperar resultado
2. Si falla, cambiar a red móvil y reintentar desde WSL
3. Si persiste, configurar DNS en Docker y reintentar
4. Como última opción, usar versiones alternativas de imágenes

---

## 📞 **Contacto de Soporte**

Si ninguna solución funciona:
- Verificar con tu ISP/red corporativa
- Probar desde otra red
- Considerar usar Docker images pre-descargadas (USB/compartición)

---

**Status actual:** Deploy corriendo desde WSL - Verificar progreso con:
```bash
docker ps
docker logs financia_backend_gpu
```
