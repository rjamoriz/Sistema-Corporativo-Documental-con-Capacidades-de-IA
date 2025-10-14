# 🎯 GUÍA DE PRUEBA: GENERACIÓN REAL DE DOCUMENTOS SINTÉTICOS

## ✅ Implementación Completada

Se ha implementado exitosamente el servicio completo de generación de documentos sintéticos que:
- ✅ Genera PDFs reales con contenido realista
- ✅ 7 categorías diferentes de documentos
- ✅ Metadata JSON por documento
- ✅ Preview de texto para búsqueda rápida
- ✅ Descarga individual de archivos
- ✅ Visualización en el frontend

## 🚀 Cómo Probar (Método Frontend - Recomendado)

### Paso 1: Acceder al Sistema

1. **Abrir el frontend**: http://localhost:3000
2. **Login con credenciales admin**:
   - Usuario: `admin@demo.documental.com`
   - Password: `Demo2025!`

### Paso 2: Ir a Datos Sintéticos

1. En el menú lateral, buscar **"Datos Sintéticos"** o **"Synthetic Data"**
2. Verás una interfaz con 3 tabs:
   - 🚀 Generación
   - 📁 Archivos Sintéticos
   - 🧬 Vectorización OpenAI

### Paso 3: Configurar Generación

En la tab **Generación**:

1. **Cantidad de documentos**: 
   - Usar el slider para seleccionar (ej: 20 documentos)
   - Para prueba rápida: 10-20 documentos
   - Para prueba completa: 50-100 documentos

2. **Template de Distribución**:
   - `default`: Distribución balanceada (recomendado)
   - `financial`: Enfocado en finanzas
   - `contracts`: Enfocado en legal/compliance

3. **Auto-upload**: 
   - Dejar activado si quieres que se suban automáticamente al sistema
   - Desactivar para solo generar archivos locales

4. **Preview de distribución**:
   - El sistema mostrará cómo se distribuirán los documentos por categoría
   - Ej: Legal 25%, Financial 20%, HR 15%, etc.

### Paso 4: Generar Documentos

1. Click en **"🚀 Generar Datos Sintéticos"**
2. El sistema creará una tarea de generación
3. Verás la tarea en "Tareas de Generación" con:
   - Estado actual (pending → running → completed)
   - Barra de progreso (0-100%)
   - Tiempo estimado
   - Documentos generados

### Paso 5: Monitorear Progreso

El sistema actualiza el progreso cada 2 segundos:
- **🟡 Pending**: Tarea creada, esperando ejecución
- **🔵 Running**: Generando documentos (verás el progreso)
- **🟢 Completed**: ¡Listo! Documentos generados
- **🔴 Failed**: Error (ver detalles en la tarea)

### Paso 6: Ver Archivos Generados

Cuando la tarea esté **Completed**:

1. Click en **"📁 Ver Archivos"** en la tarea completada
2. Te llevará automáticamente a la tab **"Archivos Sintéticos"**
3. Verás:
   - **Lista de archivos** (lado izquierdo): todos los PDFs generados
   - **Visualizador** (lado derecho): detalles del archivo seleccionado

### Paso 7: Explorar Archivos

En el visualizador de archivos:

**Información disponible:**
- 📄 Nombre del archivo
- 🏷️ Categoría (Legal, Financial, HR, etc.)
- 📊 Tamaño en KB
- ⚠️ Nivel de riesgo (low/medium/high)
- 🧩 Chunks (para vectorización)
- 🔍 Entidades detectadas
- 📝 Preview del contenido (primeros 1000 caracteres)

**Acciones:**
- Click en cualquier archivo para ver su preview
- **"⬇️ Descargar PDF"**: Descarga el archivo a tu computadora
- **"🗑️ Eliminar"** (en la tarea): Elimina todos los archivos

## 📋 Tipos de Documentos Generados

### Legal (25%)
- Contratos de servicios profesionales
- Acuerdos de confidencialidad
- Términos y condiciones
- Contratos de arrendamiento

### Financial (20%)
- Informes financieros trimestrales
- Estados de resultados
- Balance general
- Análisis de costos

### HR (15%)
- Políticas de recursos humanos
- Manuales de empleados
- Descripciones de puestos
- Evaluaciones de desempeño

### Technical (15%)
- Especificaciones técnicas
- Documentación de arquitectura
- Manuales de usuario
- Guías de integración

### Marketing (10%)
- Planes de marketing
- Estrategias de contenido
- Análisis de mercado
- Campañas publicitarias

### Operations (10%)
- Procedimientos operativos
- Manuales de operación
- Planes de contingencia
- Protocolos de calidad

### Compliance (5%)
- Políticas de compliance
- Auditorías internas
- Reportes regulatorios
- Evaluaciones de riesgo

## 🔍 Verificación de Archivos

### En el Sistema de Archivos (Docker)

```powershell
# Ver contenedor backend
docker-compose ps backend

# Listar archivos generados
docker-compose exec backend ls -la /tmp/synthetic_data_*

# Ver contenido de un directorio específico (reemplaza TASK_ID)
docker-compose exec backend ls -la /tmp/synthetic_data_<TASK_ID>/

# Ver metadata de un archivo
docker-compose exec backend cat /tmp/synthetic_data_<TASK_ID>/synthetic_legal_001.json

# Ver preview de texto
docker-compose exec backend cat /tmp/synthetic_data_<TASK_ID>/synthetic_legal_001.txt
```

### Estructura de Archivos

```
/tmp/synthetic_data_<task_id>/
├── synthetic_legal_001.pdf      # PDF real
├── synthetic_legal_001.json     # Metadata
├── synthetic_legal_001.txt      # Text preview
├── synthetic_legal_002.pdf
├── synthetic_legal_002.json
├── synthetic_legal_002.txt
├── synthetic_financial_001.pdf
├── synthetic_financial_001.json
├── synthetic_financial_001.txt
└── ... (más archivos)
```

## 🧪 Pruebas Recomendadas

### Prueba 1: Generación Rápida (5 minutos)
```
Documentos: 10
Template: default
Auto-upload: false
Resultado esperado: 10 PDFs en ~5 segundos
```

### Prueba 2: Generación Media (10 minutos)
```
Documentos: 50
Template: financial
Auto-upload: false
Resultado esperado: 50 PDFs en ~25 segundos
```

### Prueba 3: Generación Completa (30 minutos)
```
Documentos: 200
Template: default
Auto-upload: true
Resultado esperado: 200 PDFs en ~100 segundos + integración
```

## 🐛 Troubleshooting

### Problema: "Could not validate credentials"

**Solución:**
1. Cerrar sesión en el frontend
2. Volver a hacer login
3. Verificar que el token se guardó correctamente en localStorage
4. Refrescar la página

### Problema: "No se encontraron archivos para esta tarea"

**Posibles causas:**
- Tarea aún no completada → esperar más tiempo
- Error en la generación → revisar logs del backend
- Directorio eliminado → regenerar documentos

**Verificar:**
```powershell
docker-compose logs backend | Select-String "synthetic"
```

### Problema: Generación muy lenta

**Optimizaciones:**
- Reducir cantidad de documentos
- Verificar uso de CPU/RAM del contenedor
- Revisar logs para errores

**Verificar recursos:**
```powershell
docker stats financia_backend
```

### Problema: Error al descargar PDF

**Verificar:**
1. Archivo existe en el contenedor
2. Token válido (no expirado)
3. Permisos de descarga en el navegador

## 📊 Logs Importantes

### Backend - Generación Exitosa
```log
INFO: Synthetic data generation started: task_id=abc123, documents=50
INFO: Generating 50 documents in background...
INFO: Generated Legal document 1/50
INFO: Generated Financial document 2/50
...
INFO: Task abc123 completed: 50 documents generated
```

### Backend - Ver Logs en Tiempo Real
```powershell
# Ver logs completos
docker-compose logs -f backend

# Filtrar solo synthetic data
docker-compose logs -f backend | Select-String "synthetic"

# Últimas 100 líneas
docker-compose logs backend --tail=100
```

## 🎨 Características del Frontend

### Tab Generación
- ✅ Configuración visual intuitiva
- ✅ Preview de distribución
- ✅ Lista de tareas con progreso
- ✅ Actualización en tiempo real
- ✅ Gestión de tareas (eliminar)

### Tab Archivos
- ✅ Lista de archivos generados
- ✅ Visualizador de metadata
- ✅ Preview de contenido
- ✅ Descarga individual
- ✅ Información detallada por archivo

### Tab Vectorización
- ✅ API Key de OpenAI configurable
- ✅ Prueba de embeddings
- ✅ Visualización de dimensiones
- ✅ Integración futura con búsqueda

## 🔄 Ciclo Completo de Uso

```
1. Login → 2. Configurar → 3. Generar → 4. Monitorear → 5. Explorar → 6. Descargar
```

### 1. Login
- Credenciales admin
- Token almacenado automáticamente

### 2. Configurar
- Seleccionar cantidad
- Elegir template
- Configurar auto-upload

### 3. Generar
- Click en "Generar"
- Task creada instantáneamente

### 4. Monitorear
- Ver progreso en tiempo real
- Estado actualizado cada 2s
- Logs en backend

### 5. Explorar
- Ver archivos generados
- Leer metadata
- Preview de contenido

### 6. Descargar
- Descargar PDFs individuales
- O acceder directamente en el contenedor

## 📈 Métricas de Rendimiento

### Tiempos Esperados
- Generación por documento: ~0.5 segundos
- 10 documentos: ~5 segundos
- 50 documentos: ~25 segundos
- 100 documentos: ~50 segundos
- 500 documentos: ~250 segundos (4 minutos)

### Tamaños de Archivos
- PDF promedio: 30-50 KB
- Metadata JSON: 1-3 KB
- Text preview: 2-10 KB
- Total por documento: ~35-65 KB

### Categorías Generadas (template "default")
- Legal: 25% (ej: 12-13 de 50)
- Financial: 20% (ej: 10 de 50)
- HR: 15% (ej: 7-8 de 50)
- Technical: 15% (ej: 7-8 de 50)
- Marketing: 10% (ej: 5 de 50)
- Operations: 10% (ej: 5 de 50)
- Compliance: 5% (ej: 2-3 de 50)

## ✨ Próximos Pasos

### Inmediato (Ya Funcional)
- ✅ Generar documentos sintéticos
- ✅ Visualizar en el frontend
- ✅ Descargar PDFs
- ✅ Ver metadata

### Corto Plazo (Opcional)
- [ ] Integración con MinIO
- [ ] Registro en base de datos
- [ ] Búsqueda por contenido
- [ ] Tags y categorización avanzada

### Largo Plazo (Futuro)
- [ ] Vectorización automática
- [ ] Búsqueda semántica
- [ ] Generación con GPT-4
- [ ] Relaciones entre documentos
- [ ] Análisis de contenido con IA

## 🎯 Estado Actual

```
✅ Backend actualizado con servicio completo
✅ Endpoints de generación funcionando
✅ Endpoints de descarga implementados
✅ Frontend con visualización completa
✅ Integración frontend-backend operativa
✅ Generación real de PDFs con ReportLab
✅ Metadata y previews generados
⏳ Listo para pruebas del usuario
```

## 📞 Soporte

Si encuentras problemas:

1. **Revisar logs**: `docker-compose logs backend`
2. **Estado de contenedores**: `docker-compose ps`
3. **Reiniciar backend**: `docker-compose restart backend`
4. **Ver esta guía**: `GUIA_PRUEBA_GENERACION_REAL.md`

---

**¡Listo para probar! 🚀**

Accede a http://localhost:3000 y comienza a generar documentos sintéticos reales.
