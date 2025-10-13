# 🚀 Guía de Setup Local con Docker Desktop

## 📋 Requisitos Previos

### Requerimientos del Sistema:
- **RAM:** 16 GB (mínimo 12 GB)
- **Disco:** 30 GB libres
- **CPU:** 4 cores (recomendado)
- **OS:** Windows 10/11, macOS 10.15+, o Linux

### Software Necesario:
1. **Docker Desktop** - [Descargar](https://www.docker.com/products/docker-desktop)
2. **Git** - [Descargar](https://git-scm.com/downloads)
3. **(Opcional) Visual Studio Code** - [Descargar](https://code.visualstudio.com/)

---

## 🏁 Setup Paso a Paso

### Paso 1: Clonar el Repositorio

```bash
# En tu máquina local
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA.git

cd Sistema-Corporativo-Documental-con-Capacidades-de-IA
```

### Paso 2: Configurar Docker Desktop

**Windows/macOS:**
1. Abrir Docker Desktop
2. Ir a Settings → Resources
3. Configurar:
   - **Memory:** 8 GB (o más)
   - **CPUs:** 4 (o más)
   - **Swap:** 2 GB
   - **Disk:** 50 GB

**Linux:**
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Paso 3: Crear archivo de variables de entorno

```bash
# Copiar el ejemplo
cp .env.example .env

# Editar con tus valores
nano .env  # o usar tu editor favorito
```

**Variables importantes:**
```env
# Base de datos
DATABASE_URL=postgresql+asyncpg://financia:financia2030@postgres:5432/financia_db

# OpenAI (para vectorización)
OPENAI_API_KEY=tu-api-key-aqui

# Redis
REDIS_URL=redis://redis:6379/0

# MinIO
MINIO_HOST=minio
MINIO_PORT=9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### Paso 4: Construir las imágenes

```bash
# Construir todas las imágenes (puede tardar 10-15 minutos primera vez)
docker-compose build

# O construir con caché limpia
docker-compose build --no-cache
```

### Paso 5: Iniciar los servicios

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
```

### Paso 6: Verificar que todo funcione

```bash
# Ver estado de los contenedores
docker-compose ps

# Deberías ver algo como:
# NAME                  STATUS      PORTS
# financia_backend      Up          0.0.0.0:8000->8000/tcp
# financia_frontend     Up          0.0.0.0:3000->3000/tcp
# financia_postgres     Up          0.0.0.0:5432->5432/tcp
# financia_redis        Up          0.0.0.0:6379->6379/tcp
# financia_minio        Up          0.0.0.0:9000-9001->9000-9001/tcp
```

### Paso 7: Acceder a las aplicaciones

**URLs disponibles:**
- 🌐 **Frontend:** http://localhost:3000
- 🔧 **Backend API:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs
- 🗄️ **MinIO Console:** http://localhost:9001 (admin/admin)

**Credenciales de prueba:**
- Usuario: `admin.demo`
- Password: `Demo2025!`

---

## 🔧 Comandos Útiles

### Gestión de Contenedores:

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (limpieza completa)
docker-compose down -v

# Reiniciar un servicio específico
docker-compose restart backend

# Ver logs
docker-compose logs -f backend

# Ejecutar comando en un contenedor
docker-compose exec backend bash
docker-compose exec postgres psql -U financia -d financia_db
```

### Desarrollo:

```bash
# Reconstruir después de cambios en código
docker-compose up -d --build

# Solo reconstruir backend
docker-compose up -d --build backend

# Ver uso de recursos
docker stats
```

### Base de Datos:

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U financia -d financia_db

# Backup de la base de datos
docker-compose exec postgres pg_dump -U financia financia_db > backup.sql

# Restaurar base de datos
docker-compose exec -T postgres psql -U financia financia_db < backup.sql

# Ver tablas
docker-compose exec postgres psql -U financia -d financia_db -c "\dt"
```

### Limpieza:

```bash
# Limpiar contenedores detenidos
docker container prune

# Limpiar imágenes no usadas
docker image prune

# Limpiar todo (cuidado!)
docker system prune -a --volumes
```

---

## 📊 Monitoreo

### Ver métricas de recursos:

```bash
# Uso de CPU/RAM por contenedor
docker stats

# Uso de espacio en disco
docker system df
```

### Health checks:

```bash
# Ver estado de salud de los servicios
docker-compose ps

# Verificar backend
curl http://localhost:8000/

# Verificar PostgreSQL
docker-compose exec postgres pg_isready -U financia
```

---

## 🐛 Troubleshooting

### Problema: Backend no inicia

**Síntomas:**
```
backend | ImportError: No module named 'xxx'
```

**Solución:**
```bash
# Reconstruir con caché limpia
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Problema: Puerto ya en uso

**Síntomas:**
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solución:**
```bash
# Ver qué proceso usa el puerto
# Windows:
netstat -ano | findstr :8000

# macOS/Linux:
lsof -i :8000

# Matar el proceso o cambiar puerto en docker-compose.yml
```

### Problema: Modelos ML tardan en cargar

**Síntomas:**
Backend inicia pero responde lento las primeras veces.

**Solución:**
Esto es normal. Los modelos cargan bajo demanda:
- Primera generación sintética: 2-3 minutos
- Siguientes generaciones: < 1 segundo

Para pre-cargar:
```bash
docker-compose exec backend python -c "
from ml.embeddings import embedding_model
from ml.ner_model import ner_model
embedding_model.encode(['test'])
ner_model.extract_entities('test')
"
```

### Problema: Falta espacio en disco

**Síntomas:**
```
no space left on device
```

**Solución:**
```bash
# Limpiar imágenes y contenedores viejos
docker system prune -a

# Ver uso de espacio
docker system df

# Limpiar volúmenes no usados
docker volume prune
```

---

## 🚀 Optimizaciones de Rendimiento

### 1. Aumentar memoria para Docker:

**Docker Desktop → Settings → Resources:**
- Memory: 12-16 GB
- CPUs: 6-8 cores
- Swap: 4 GB

### 2. Usar volúmenes con cache de modelos:

Los modelos ML se guardan en volumen persistente `model_cache`, así que solo se descargan una vez.

### 3. Pre-construir imágenes:

```bash
# Construir todas las imágenes en paralelo
docker-compose build --parallel
```

### 4. Modo producción:

Para producción, usar build optimizado:
```bash
# Build de producción
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📝 Notas Importantes

### Persistencia de Datos:

Los datos se guardan en volúmenes Docker:
- `postgres_data` - Base de datos
- `redis_data` - Cache
- `minio_data` - Archivos
- `model_cache` - Modelos ML (importante!)

**Para eliminar todo:**
```bash
docker-compose down -v  # CUIDADO: Borra todos los datos
```

### Desarrollo vs Producción:

**Desarrollo (actual):**
- Hot reload activado
- Logs verbosos
- Sin optimizaciones

**Producción:**
- Build optimizado
- Workers múltiples
- Reverse proxy (nginx)
- SSL/TLS
- Monitoreo

---

## 🎯 Checklist de Verificación

Después del setup, verifica:

- [ ] Backend responde en http://localhost:8000
- [ ] Frontend carga en http://localhost:3000
- [ ] Login funciona (admin.demo / Demo2025!)
- [ ] Puedes navegar entre páginas
- [ ] Base de datos conectada
- [ ] Redis funcionando
- [ ] MinIO accesible

**Test completo:**
```bash
# 1. Backend health
curl http://localhost:8000/

# 2. Frontend health  
curl http://localhost:3000/

# 3. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin.demo","password":"Demo2025!"}'

# 4. Ver logs
docker-compose logs --tail=50
```

---

## 🆘 Soporte

Si tienes problemas:

1. **Ver logs:**
   ```bash
   docker-compose logs -f
   ```

2. **Revisar estado:**
   ```bash
   docker-compose ps
   docker stats
   ```

3. **Reiniciar limpio:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Limpiar y reconstruir:**
   ```bash
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up -d
   ```

---

## 🎉 ¡Listo!

Una vez todo funcionando:

1. ✅ Navega a http://localhost:3000
2. ✅ Login con admin.demo / Demo2025!
3. ✅ Explora las funcionalidades
4. ✅ Genera datos sintéticos
5. ✅ Prueba la vectorización con OpenAI

**Disfruta desarrollando sin límites de recursos!** 🚀

---

**Última actualización:** 13 Octubre 2025  
**Versión:** 1.0  
**Estado:** ✅ Production Ready
