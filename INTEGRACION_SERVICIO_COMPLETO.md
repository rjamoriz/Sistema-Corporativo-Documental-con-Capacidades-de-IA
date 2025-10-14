# ✅ INTEGRACIÓN SERVICIO COMPLETO DE GENERACIÓN DE DOCUMENTOS SINTÉTICOS

## Cambios Realizados

### 1. Backend - API Endpoints (`backend/api/v1/synthetic.py`)

**Cambio Principal:**
```python
# Antes (servicio mock):
from services.synthetic_data_service_light import synthetic_data_service

# Ahora (servicio completo con generación real):
from services.synthetic_data_service_full import synthetic_data_service
```

**Nuevos Endpoints Agregados:**

1. **`GET /api/v1/synthetic/tasks/{task_id}/files`**
   - Lista archivos PDF generados para una tarea completada
   - Retorna metadata, preview de contenido, entidades detectadas
   - Información de tamaño, categoría, riesgo

2. **`GET /api/v1/synthetic/tasks/{task_id}/files/{filename}`**
   - Descarga archivo PDF individual
   - Validación de seguridad (path traversal prevention)
   - Solo permite descargar PDFs

**Seguridad:**
- Prevención de path traversal attacks
- Validación de tipo de archivo (.pdf)
- Verificación de ownership de tasks
- Solo archivos de tasks completadas

### 2. Backend - Servicio Full (`backend/services/synthetic_data_service_full.py`)

**Nuevos Métodos Agregados:**

```python
async def delete_task(self, task_id: str) -> bool:
    """
    Elimina una tarea y sus archivos asociados
    - Borra directorio completo con archivos generados
    - Limpia entrada del diccionario de tasks
    - Logging de operaciones
    """
```

**Características del Servicio:**
- ✅ Genera documentos PDF reales con contenido sintético
- ✅ 7 categorías de documentos (Legal, Financial, HR, Technical, Marketing, Operations, Compliance)
- ✅ Contenido realista específico por categoría
- ✅ Metadata JSON por documento
- ✅ Text preview (.txt) para búsqueda rápida
- ✅ Almacenamiento en directorio temporal organizado por task_id
- ✅ Tracking de progreso en tiempo real
- ✅ Async processing con background tasks

### 3. Frontend - Ya Configurado

El frontend **ya tiene toda la funcionalidad** necesaria:
- ✅ Función `loadSyntheticFiles()` implementada
- ✅ Botón "📁 Ver Archivos" en tasks completadas
- ✅ Tab de visualización de archivos
- ✅ Preview de metadata y contenido
- ✅ Descarga individual de PDFs

### 4. Dependencias

**Ya incluidas en `requirements.txt`:**
```txt
reportlab==4.0.7  # Generación de PDFs
```

## Cómo Probar

### Paso 1: Reiniciar Backend

```powershell
# Ejecutar script de reinicio
.\restart-backend.ps1
```

O manualmente:
```powershell
docker-compose stop backend
docker-compose up -d backend
docker-compose logs -f backend
```

### Paso 2: Generar Documentos Sintéticos

1. **Login al sistema** (usuario admin)
2. **Ir a "Datos Sintéticos"** en el menú
3. **Configurar generación:**
   - Cantidad: 20-50 documentos (para prueba rápida)
   - Template: "default" o "financial"
   - Auto-upload: activado/desactivado según preferencia

4. **Iniciar generación** (botón "🚀 Generar")
5. **Observar progreso** en tiempo real
6. **Cuando complete:**
   - Click en "📁 Ver Archivos"
   - Se abre la pestaña de archivos
   - Lista todos los PDFs generados

### Paso 3: Explorar Archivos Generados

En la pestaña "Archivos":
- **Lista de archivos** (izquierda): todos los PDFs generados
- **Visualizador** (derecha):
  - Metadata (tamaño, fecha, categoría)
  - Risk level y chunks
  - Entidades detectadas
  - Preview del contenido (primeros 1000 caracteres)
  - Botón de descarga

### Paso 4: Descargar PDFs

Click en **"⬇️ Descargar PDF"** para obtener el archivo

## Endpoints API Disponibles

```
POST   /api/v1/synthetic/generate
       → Inicia generación de documentos
       
GET    /api/v1/synthetic/status/{task_id}
       → Estado y progreso de tarea
       
GET    /api/v1/synthetic/tasks
       → Lista todas las tareas del usuario
       
GET    /api/v1/synthetic/tasks/{task_id}/files
       → Lista archivos generados (✨ NUEVO)
       
GET    /api/v1/synthetic/tasks/{task_id}/files/{filename}
       → Descarga archivo PDF (✨ NUEVO)
       
DELETE /api/v1/synthetic/tasks/{task_id}
       → Elimina tarea y archivos
       
GET    /api/v1/synthetic/templates
       → Lista templates disponibles
```

## Estructura de Archivos Generados

```
/tmp/synthetic_data_{task_id}/
├── synthetic_legal_001.pdf          # Documento PDF
├── synthetic_legal_001.json         # Metadata
├── synthetic_legal_001.txt          # Text preview
├── synthetic_financial_001.pdf
├── synthetic_financial_001.json
├── synthetic_financial_001.txt
└── ... (más documentos según cantidad)
```

## Metadata JSON Ejemplo

```json
{
  "title": "Contrato de Servicios Profesionales #001",
  "category": "Legal",
  "file_size": 45678,
  "entities": ["FinancIA 2030 S.L.", "Madrid", "CIF B-12345678"],
  "risk_level": "medium",
  "chunks": 12,
  "created_at": "2024-01-15T10:30:00Z",
  "contract_number": "CTR-000001",
  "contract_type": "Servicios Profesionales",
  "metadata": {
    "parties": 2,
    "value": 85000,
    "duration_months": 12
  }
}
```

## Contenido de Documentos por Categoría

### Legal
- Contratos de servicios profesionales
- Acuerdos de confidencialidad
- Términos y condiciones
- Contratos de arrendamiento
- Clausulado completo y realista

### Financial
- Informes financieros trimestrales
- Estados de resultados
- Balance general
- Análisis de costos
- Proyecciones financieras

### HR
- Políticas de recursos humanos
- Manuales de empleados
- Descripciones de puestos
- Evaluaciones de desempeño
- Programas de capacitación

### Technical
- Especificaciones técnicas
- Documentación de arquitectura
- Manuales de usuario
- Procedimientos de despliegue
- Guías de integración

### Marketing
- Planes de marketing
- Estrategias de contenido
- Análisis de mercado
- Campañas publicitarias
- Estudios de marca

### Operations
- Procedimientos operativos
- Manuales de operación
- Planes de contingencia
- Reportes de incidentes
- Protocolos de calidad

### Compliance
- Políticas de compliance
- Auditorías internas
- Reportes regulatorios
- Planes de acción
- Evaluaciones de riesgo

## Diferencias con Servicio Mock

| Aspecto | Servicio Mock (anterior) | Servicio Full (nuevo) |
|---------|--------------------------|------------------------|
| Archivos | ❌ No genera archivos reales | ✅ PDFs reales con ReportLab |
| Contenido | ❌ Solo metadata simulada | ✅ Contenido realista por categoría |
| Almacenamiento | ❌ Solo en memoria | ✅ Sistema de archivos |
| Descarga | ❌ No disponible | ✅ Endpoint de descarga |
| Metadata | ❌ Básica | ✅ Completa con JSON |
| Preview | ❌ No disponible | ✅ Archivo .txt con contenido |
| Tiempo de generación | Instantáneo | ~0.5s por documento |

## Verificación de Funcionamiento

### Logs a Observar

```log
INFO: Synthetic data generation started: task_id=abc123, documents=50
INFO: Generating 50 documents in background...
INFO: Generated Legal document 1/50
INFO: Generated Financial document 2/50
...
INFO: Task abc123 completed: 50 documents generated
```

### Archivos a Verificar

```bash
# Verificar que se crearon los archivos
ls /tmp/synthetic_data_*

# Ver contenido de un metadata
cat /tmp/synthetic_data_abc123/synthetic_legal_001.json

# Ver preview de texto
cat /tmp/synthetic_data_abc123/synthetic_legal_001.txt
```

## Próximos Pasos Opcionales

### 1. Integración con MinIO
- Subir PDFs generados a MinIO
- Obtener URLs permanentes
- Integrarse con sistema de documentos principal

### 2. Registro en Base de Datos
- Crear tabla `synthetic_documents`
- Registrar metadata en PostgreSQL
- Habilitar búsqueda avanzada

### 3. Vectorización Automática
- Generar embeddings con OpenAI
- Almacenar en ChromaDB/Qdrant
- Habilitar búsqueda semántica

### 4. Enriquecimiento con IA
- Usar GPT-4 para contenido más realista
- Generar documentos basados en plantillas
- Crear relaciones entre documentos

## Troubleshooting

### "No se encontraron archivos para esta tarea"

**Posibles causas:**
1. Tarea aún no completada → esperar
2. Error en generación → revisar logs
3. Directorio borrado → regenerar
4. Permisos de escritura → verificar /tmp

**Solución:**
```bash
# Verificar estado de la tarea
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/synthetic/status/{task_id}

# Verificar logs del backend
docker-compose logs backend | grep synthetic
```

### "Error al descargar archivo"

**Verificar:**
1. Archivo existe en el servidor
2. Token válido y no expirado
3. Usuario tiene permisos de admin
4. Endpoint correcto (task_id y filename)

### "Generación muy lenta"

**Optimizaciones:**
- Reducir cantidad de documentos
- Usar template con menos categorías
- Verificar recursos del sistema
- Revisar logs de errores

## Estado del Sistema

✅ Backend actualizado con servicio completo  
✅ Endpoints de archivos implementados  
✅ Seguridad y validaciones agregadas  
✅ Frontend ya soporta visualización  
✅ Dependencias instaladas (reportlab)  
⏳ Pendiente: reiniciar backend y probar  

## Comandos Útiles

```powershell
# Reiniciar backend
.\restart-backend.ps1

# Ver logs en tiempo real
docker-compose logs -f backend

# Ver tareas activas
docker-compose ps

# Entrar al contenedor
docker-compose exec backend bash

# Verificar archivos generados
docker-compose exec backend ls -la /tmp/synthetic_data_*
```

---

**✨ CAMBIO COMPLETADO - LISTO PARA PRUEBAS ✨**
