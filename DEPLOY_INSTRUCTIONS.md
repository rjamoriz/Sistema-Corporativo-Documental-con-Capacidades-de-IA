# 🚀 Instrucciones de Despliegue - FinancIA 2030 con GPU

## ✅ Scripts Corregidos y Listos

Todos los scripts PowerShell han sido limpiados y ya NO tienen problemas de sintaxis.

---

## 📋 Scripts Disponibles

### 1. deploy-auto.ps1 ⭐ (RECOMENDADO)
**Descripción:** Detecta automáticamente GPU y despliega sin preguntas

**Uso:**
```powershell
.\deploy-auto.ps1
```

**Características:**
- ✅ Sin emojis problemáticos
- ✅ Sintaxis PowerShell limpia
- ✅ Detección automática de GPU
- ✅ Sin interacción requerida

---

### 2. deploy-gpu.ps1 (Interactivo)
**Descripción:** Te pregunta qué configuración usar

**Uso:**
```powershell
.\deploy-gpu.ps1
# Elegir: 1 para GPU, 2 para CPU
```

**Características:**
- ✅ Sin emojis problemáticos
- ✅ Sintaxis PowerShell limpia
- ✅ Control manual de la configuración

---

### 3. test-gpu.ps1
**Descripción:** Verifica que GPU funciona

**Uso:**
```powershell
.\test-gpu.ps1
```

---

## 🔧 Si PowerShell Bloquea los Scripts

```powershell
# Permitir ejecución temporalmente
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Luego ejecutar
.\deploy-auto.ps1
```

---

## 🚀 Despliegue Paso a Paso

### Paso 1: Abrir PowerShell como Administrador
```
Win + X → Windows PowerShell (Admin)
```

### Paso 2: Navegar al directorio
```powershell
cd "C:\Users\rjamo\OneDrive\Desktop\IA GEN PROJECTS\Sistema Corporativo Documentacion AI-GPU boosted\Sistema-Corporativo-Documental-con-Capacidades-de-IA"
```

### Paso 3: Ejecutar script
```powershell
# Opción más fácil (automático)
.\deploy-auto.ps1

# O interactivo
.\deploy-gpu.ps1
```

### Paso 4: Esperar build
- Primera vez: 10-15 minutos
- Siguientes veces: 2-5 minutos

### Paso 5: Verificar
```powershell
# Ver logs
docker logs financia_backend_gpu

# Test GPU
.\test-gpu.ps1
```

### Paso 6: Acceder
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000/docs
- **Login**: `admin.demo` / `Demo2025!`

---

## 🐳 Alternativa: Docker Compose Manual

Si los scripts siguen dando problemas, usa Docker Compose directamente:

### Con GPU:
```powershell
docker-compose -f docker-compose.gpu.yml build
docker-compose -f docker-compose.gpu.yml up -d
```

### Sin GPU:
```powershell
docker-compose build
docker-compose up -d
```

---

## 🔍 Verificar Estado

```powershell
# Ver containers corriendo
docker ps

# Ver logs en tiempo real
docker logs -f financia_backend_gpu

# Ver solo mensajes de GPU
docker logs financia_backend_gpu | Select-String "GPU"

# Estado de servicios
docker-compose ps
```

---

## 🛑 Detener Servicios

```powershell
# Con GPU
docker-compose -f docker-compose.gpu.yml down

# Sin GPU
docker-compose down

# Limpiar todo
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Problema: Script no se ejecuta
**Solución:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\deploy-auto.ps1
```

### Problema: GPU no detectada
**Solución:**
```powershell
# Verificar en Windows
nvidia-smi

# Reiniciar Docker Desktop
# Menú de Docker Desktop → Restart
```

### Problema: Puerto ocupado
**Solución:**
```powershell
# Ver qué usa el puerto
netstat -ano | findstr :8000

# Detener servicios existentes
docker-compose down
```

### Problema: Build muy lento
**Solución:**
```powershell
# Limpiar caché de Docker
docker system prune -a

# Reiniciar Docker Desktop
```

---

## ⚡ Mejoras de Performance Esperadas

Con GPU funcionando:
- **Embeddings**: 7.5x más rápido
- **Clasificación**: 6x más rápido
- **OCR**: 3x más rápido

---

## 📚 Documentación Completa

- **START_HERE.md** - Inicio rápido
- **GPU_QUICKSTART.md** - Guía rápida GPU
- **GPU_ACCELERATION_GUIDE.md** - Guía completa
- **GPU_COMMANDS.md** - Comandos útiles
- **POWERSHELL_FIX.md** - Solución de errores

---

## ✅ Checklist Pre-Deploy

- [ ] Docker Desktop instalado y corriendo
- [ ] NVIDIA GPU disponible (nvidia-smi funciona)
- [ ] PowerShell abierto como Administrador
- [ ] Navegado al directorio del proyecto
- [ ] Execution Policy configurado si es necesario

---

## 🎉 ¡Listo para Desplegar!

**Comando recomendado:**
```powershell
.\deploy-auto.ps1
```

Este script:
1. ✅ Verifica Docker
2. ✅ Detecta GPU automáticamente
3. ✅ Elige la configuración adecuada
4. ✅ Hace build y deploy
5. ✅ Muestra URLs al terminar

**Tiempo estimado:** 10-15 minutos primera vez

---

## 💡 Tips

- Usa `deploy-auto.ps1` para evitar preguntas
- Usa `test-gpu.ps1` para verificar después
- Monitorea con `docker logs -f financia_backend_gpu`
- Accede a los docs en http://localhost:8000/docs

---

**¿Listo?** Ejecuta: `.\deploy-auto.ps1` 🚀
