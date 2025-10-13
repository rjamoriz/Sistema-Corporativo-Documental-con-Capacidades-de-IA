# 🚀 Guía Rápida: Cambiar a Backend Completo

## ⚡ Inicio Rápido (1 comando)

```bash
./cambiar_a_backend_completo.sh
```

**Eso es todo!** El script hace todo automáticamente.

---

## 📋 ¿Qué hace el script?

```
1. ❌ Detiene el backend demo (main_demo.py)
2. ✅ Instala sentence-transformers
3. ✅ Instala spacy
4. ✅ Descarga modelo español (es_core_news_md)
5. 🚀 Inicia el backend completo (main.py)
```

**Tiempo estimado:** 2-3 minutos

---

## 🎯 Acceso después del cambio

### Backend Completo:
- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Endpoints:** Todos disponibles (incluye `/synthetic`)

### Frontend:
- **URL:** http://localhost:3000
- **Login:** admin.demo / Demo2025!
- **Página:** Generador de Datos Sintéticos → Todas las tabs funcionarán

---

## 🔍 Verificación

### 1. Verificar backend corriendo:
```bash
curl http://localhost:8000/ | jq '.'
```

**Deberías ver:**
```json
{
  "message": "FinancIA 2030 API",  ← Ya no dice "Demo"
  "version": "1.0.0",
  "status": "running"
}
```

### 2. Verificar endpoint synthetic:
```bash
curl -X GET "http://localhost:8000/docs" | grep synthetic
```

**Deberías ver:** Varios endpoints `/api/v1/synthetic/*`

---

## 🎬 Flujo Completo

```
┌─────────────────────────────────────────────────────────┐
│ ANTES (Backend Demo)                                    │
├─────────────────────────────────────────────────────────┤
│ ❌ /api/v1/synthetic/generate → 404 Not Found          │
│ ❌ /api/v1/synthetic/tasks → 404 Not Found             │
│ ❌ Tab de Archivos Sintéticos → Sin datos              │
│ ❌ Tab de Vectorización → Sin datos                    │
└─────────────────────────────────────────────────────────┘

         🔄 ./cambiar_a_backend_completo.sh

┌─────────────────────────────────────────────────────────┐
│ DESPUÉS (Backend Completo)                              │
├─────────────────────────────────────────────────────────┤
│ ✅ /api/v1/synthetic/generate → Funciona              │
│ ✅ /api/v1/synthetic/tasks → Funciona                 │
│ ✅ Tab de Archivos Sintéticos → Muestra archivos      │
│ ✅ Tab de Vectorización → Genera embeddings           │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Probar Funcionalidad Sintética

### Opción 1: Desde el navegador (Recomendado)

1. Abre: http://localhost:3000
2. Login: `admin.demo` / `Demo2025!`
3. Menú lateral → **"Generador de Datos Sintéticos"**
4. Tab **"Generación"**:
   - Categoría: `contract`
   - Cantidad: `5`
   - Click: **"Generar Documentos"**
   - Espera ~30 segundos
5. Click: **"Ver Archivos"** en el historial
6. Deberías ver el **Tab "Archivos Sintéticos"** con:
   - Lista de 5 PDFs generados
   - Metadata (entidades, chunks, risk level)
   - Preview del contenido

### Opción 2: Script automatizado

```bash
./test_synthetic_features.sh
```

Este script hace un test completo E2E.

---

## ❓ Problemas Comunes

### Problema 1: "Address already in use"
**Síntoma:** Error al iniciar backend completo
**Causa:** Backend demo aún corriendo
**Solución:**
```bash
ps aux | grep main_demo.py | grep -v grep | awk '{print $2}' | xargs kill
```

### Problema 2: "ModuleNotFoundError: sentence_transformers"
**Síntoma:** Error al importar dependencias
**Causa:** Dependencias no instaladas
**Solución:**
```bash
pip install sentence-transformers spacy
python -m spacy download es_core_news_md
```

### Problema 3: Frontend muestra "404 Not Found"
**Síntoma:** Tabs de sintéticos no funcionan
**Causa:** Backend demo aún activo
**Solución:**
1. Verifica: `curl http://localhost:8000/` 
2. Debe decir "FinancIA 2030 API" (no "Demo API")
3. Si dice "Demo", ejecuta el script de nuevo

---

## 🔄 Volver al Backend Demo

Si necesitas volver al backend demo:

```bash
# 1. Detener backend completo
ps aux | grep "main.py" | grep -v grep | awk '{print $2}' | xargs kill

# 2. Iniciar backend demo
cd /workspaces/Sistema-Corporativo-Documental-con-Capacidades-de-IA/backend
python main_demo.py &

# 3. Verificar
curl http://localhost:8000/ | jq '.'
# Debe decir: "FinancIA 2030 Demo API"
```

---

## 📊 Comparación

| Característica | Backend Demo | Backend Completo |
|---------------|--------------|------------------|
| Login/Auth | ✅ | ✅ |
| Documents | ✅ | ✅ |
| Search | ✅ | ✅ |
| RAG | ✅ | ✅ |
| Risk Analysis | ✅ | ✅ |
| **Synthetic Data** | ❌ | ✅ |
| **File Listing** | ❌ | ✅ |
| **Vectorization** | ❌ (solo OpenAI) | ✅ |
| Dependencies | Mínimas | Completas |
| Startup Time | ~2 seg | ~10 seg |

---

## 🎯 Siguiente Paso

**Después de cambiar al backend completo:**

1. ✅ Verifica que funciona: `curl http://localhost:8000/`
2. ✅ Abre el frontend: http://localhost:3000
3. ✅ Ve a "Generador de Datos Sintéticos"
4. ✅ Genera tus primeros 5 documentos
5. ✅ Explora las 3 tabs:
   - **Generación** → Crear documentos
   - **Archivos Sintéticos** → Ver estructura
   - **Vectorización OpenAI** → Embeddings

---

## 📞 Ayuda Adicional

**Documentación completa:**
- `INDICE_DOCUMENTACION.md` → Índice maestro
- `GUIA_PRUEBA.md` → Tests detallados
- `RESUMEN_EJECUTIVO_FINAL.md` → Overview completo

**Logs del backend:**
```bash
# Ver logs en tiempo real
cd /workspaces/Sistema-Corporativo-Documental-con-Capacidades-de-IA/backend
tail -f logs/app.log
```

---

## ✅ Checklist de Éxito

Después de ejecutar el script, verifica:

- [ ] Backend completo corriendo en puerto 8000
- [ ] `curl http://localhost:8000/` no dice "Demo"
- [ ] Frontend accesible en puerto 3000
- [ ] Login funciona (admin.demo / Demo2025!)
- [ ] Página "Generador de Datos Sintéticos" carga
- [ ] Tab "Generación" visible
- [ ] Tab "Archivos Sintéticos" visible
- [ ] Tab "Vectorización OpenAI" visible
- [ ] Botón "Generar Documentos" clickeable

**Si todos ✅, estás listo para generar datos sintéticos!** 🎉

---

**Fecha:** 13 Octubre 2025  
**Versión:** 1.0  
**Autor:** FinancIA 2030 Team
