# 🧪 Generador de Datos Sintéticos - Documentación de Uso

**Fecha**: 9 de Octubre 2025  
**Feature**: Generación de datos sint éticos desde la UI  
**Versión**: 1.0

---

## 📋 Descripción

Esta funcionalidad permite a los administradores generar documentos sintéticos directamente desde la aplicación web, sin necesidad de ejecutar scripts manualmente.

### ✨ Características

- ✅ **Generación async en background** - No bloquea la interfaz
- ✅ **Progreso en tiempo real** - Tracking de generación con barra de progreso
- ✅ **4 templates predefinidos** - Distribuciones balanceadas para diferentes casos de uso
- ✅ **Auto-upload opcional** - Documentos se suben automáticamente a la aplicación
- ✅ **Historial de tareas** - Ver generaciones anteriores
- ✅ **Seguridad** - Solo admins, bloqueado en producción

---

## 🚀 Uso

### Acceso

1. Iniciar sesión como **administrador**
2. Navegar a: **Admin → Generador Sintético** (o `/admin/synthetic`)
3. Solo disponible en entornos **dev/staging** (bloqueado en production)

### Generar Documentos

1. **Seleccionar cantidad**: 10-500 documentos (slider)
2. **Elegir template**: 
   - `default`: Distribución balanceada
   - `financial_heavy`: Enfoque financiero (40% financial)
   - `legal_compliance`: Legal y compliance (30% legal, 25% compliance)
   - `demo_mode`: Variado para demos
3. **Auto-upload**: Activar si quieres que se suban automáticamente
4. **Click "Generar Documentos"**
5. **Monitorear progreso**: Barra de progreso en tiempo real
6. **Resultado**: Alerta cuando finaliza + documentos en historial

### Vista Previa

Antes de generar, puedes ver:
- **Distribución exacta** por categoría
- **Porcentajes** de cada tipo
- **Tiempo estimado** de generación

---

## 🔌 API Endpoints

### POST `/api/v1/synthetic/generate`

Inicia generación de documentos.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body**:
```json
{
  "total_documents": 50,
  "template_id": "default",
  "auto_upload": true
}
```

**Response**:
```json
{
  "message": "Synthetic data generation started successfully",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "estimated_time_seconds": 25,
  "total_documents": 50,
  "status_endpoint": "/api/v1/synthetic/status/550e8400..."
}
```

---

### GET `/api/v1/synthetic/status/{task_id}`

Obtiene estado de una tarea.

**Response**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 45,
  "documents_generated": 22,
  "total_documents": 50,
  "created_at": "2025-10-09T14:30:00",
  "output_path": "/tmp/financia_synthetic/550e8400..."
}
```

**Estados**:
- `pending`: Tarea creada, esperando ejecución
- `running`: Generación en progreso
- `completed`: Finalizada exitosamente
- `failed`: Error durante generación

---

### GET `/api/v1/synthetic/tasks`

Lista todas las tareas del usuario.

**Response**:
```json
[
  {
    "task_id": "550e8400...",
    "status": "completed",
    "progress": 100,
    "documents_generated": 50,
    "total_documents": 50,
    "created_at": "2025-10-09T14:30:00",
    "documents_uploaded": 50
  },
  ...
]
```

---

### DELETE `/api/v1/synthetic/tasks/{task_id}`

Elimina una tarea y sus archivos.

**Response**:
```json
{
  "message": "Task 550e8400... deleted successfully",
  "task_id": "550e8400..."
}
```

---

### GET `/api/v1/synthetic/templates`

Lista templates disponibles.

**Response**:
```json
[
  {
    "id": "default",
    "name": "Distribución Balanceada",
    "description": "Distribución equilibrada entre todas las categorías",
    "categories": {
      "legal": "15%",
      "financial": "17.5%",
      "hr": "12.5%",
      ...
    }
  },
  ...
]
```

---

### POST `/api/v1/synthetic/preview-distribution`

Preview de distribución sin generar.

**Query Params**:
- `template_id`: ID del template
- `total_documents`: Cantidad total

**Response**:
```json
{
  "template_id": "default",
  "total_documents": 50,
  "distribution": {
    "legal": 8,
    "financial": 9,
    "hr": 6,
    ...
  },
  "percentages": {
    "legal": "16.0%",
    "financial": "18.0%",
    ...
  }
}
```

---

## 🔒 Seguridad

### Restricciones

1. **Solo administradores**: Requiere rol `admin`
2. **Bloqueado en producción**: `settings.ENVIRONMENT != "production"`
3. **Límites**: Máximo 500 documentos por request

### Validaciones

```python
# En backend/api/v1/synthetic.py

async def verify_synthetic_permissions(
    current_user: User = Depends(get_current_active_user)
) -> User:
    # Verificar rol admin
    if current_user.role != "admin":
        raise HTTPException(403, "Only administrators...")
    
    # Bloquear en producción
    if settings.ENVIRONMENT == "production":
        raise HTTPException(403, "Not allowed in production")
    
    return current_user
```

---

## 🏗️ Arquitectura Técnica

### Backend

```
backend/
├── services/
│   └── synthetic_data_service.py    # Lógica de generación async
├── api/v1/
│   └── synthetic.py                 # Router FastAPI
└── main.py                          # Registro de router
```

### Frontend

```
frontend/src/
└── pages/
    └── AdminSyntheticData.tsx       # UI Component
```

### Flujo de Generación

```
1. Usuario hace clic "Generar"
2. Frontend → POST /api/v1/synthetic/generate
3. Backend crea tarea async
4. SyntheticDataService genera documentos en background
5. Frontend poll /api/v1/synthetic/status/{task_id} cada 2s
6. Actualiza barra de progreso
7. Si auto_upload=true → sube documentos a app
8. Task status → "completed"
9. Frontend muestra alert de éxito
```

---

## 📊 Templates Disponibles

### 1. Default (Balanceado)

```
Legal:      15%  (8 docs de 50)
Financial:  17.5% (9 docs)
HR:         12.5% (6 docs)
Technical:  12.5% (6 docs)
Marketing:  10%  (5 docs)
Operations: 10%  (5 docs)
Compliance: 12.5% (6 docs)
Multimedia: 10%  (5 docs)
```

### 2. Financial Heavy

```
Financial:  40%  (20 docs de 50)
Legal:      10%  (5 docs)
Compliance: 15%  (8 docs)
Operations: 10%  (5 docs)
HR:         10%  (5 docs)
Technical:  5%   (3 docs)
Marketing:  5%   (2 docs)
Multimedia: 5%   (2 docs)
```

### 3. Legal & Compliance

```
Legal:      30%  (15 docs de 50)
Compliance: 25%  (13 docs)
Financial:  15%  (8 docs)
HR:         10%  (5 docs)
Operations: 10%  (5 docs)
Technical:  5%   (2 docs)
Marketing:  5%   (2 docs)
Multimedia: 0%   (0 docs)
```

### 4. Demo Mode

```
Legal:      20%  (10 docs de 50)
Financial:  20%  (10 docs)
HR:         15%  (8 docs)
Technical:  15%  (7 docs)
Operations: 10%  (5 docs)
Marketing:  10%  (5 docs)
Compliance: 10%  (5 docs)
Multimedia: 0%   (0 docs)
```

---

## 🧪 Testing

### Test Manual

1. Iniciar backend en modo dev:
```bash
ENVIRONMENT=development uvicorn backend.main:app --reload
```

2. Abrir UI admin: `http://localhost:3000/admin/synthetic`

3. Generar 20 documentos con template "default"

4. Verificar:
   - ✅ Progreso actualiza correctamente
   - ✅ Documentos generados en `/tmp/financia_synthetic/<task_id>`
   - ✅ Si auto_upload=true, documentos aparecen en la app
   - ✅ Historial muestra tarea completada

### Test de Seguridad

```bash
# Intentar en producción (debe fallar)
export ENVIRONMENT=production
curl -X POST http://localhost:8000/api/v1/synthetic/generate \
  -H "Authorization: Bearer <admin_token>" \
  -d '{"total_documents": 50}'

# Response esperado:
{
  "detail": "Synthetic data generation is not allowed in production environment"
}
```

### Test de Permisos

```bash
# Intentar como usuario no-admin (debe fallar)
curl -X POST http://localhost:8000/api/v1/synthetic/generate \
  -H "Authorization: Bearer <user_token>" \
  -d '{"total_documents": 50}'

# Response esperado:
{
  "detail": "Only administrators can generate synthetic data"
}
```

---

## 🐛 Troubleshooting

### Error: "Module 'scripts.generate_synthetic_data' not found"

**Causa**: El generador sintético no está instalado correctamente.

**Solución**:
```bash
# Verificar que el script existe
ls scripts/generate_synthetic_data.py

# Instalar dependencias
pip install faker reportlab python-docx openpyxl Pillow
```

### Error: "Task not found"

**Causa**: La tarea fue eliminada o expiró.

**Solución**: Generar una nueva tarea.

### Progreso se queda en 0%

**Causa**: El worker async no está ejecutándose.

**Solución**:
```python
# Verificar logs del backend
# Debe aparecer: "Task <task_id> created by user <user_id>"
# Luego: "Task <task_id>: Generating X documents..."
```

### Auto-upload no funciona

**Causa**: Servicio de ingest no disponible.

**Solución**:
```bash
# Verificar que el servicio ingest está funcionando
curl http://localhost:8000/api/v1/documents/

# Si falla, reiniciar backend
```

---

## 📈 Métricas

### Performance

| Cantidad | Tiempo (estimado) | Tiempo (real) |
|----------|-------------------|---------------|
| 10 docs  | 5s                | 4-6s          |
| 50 docs  | 25s               | 20-30s        |
| 100 docs | 50s               | 40-60s        |
| 500 docs | 250s (4min)       | 200-300s      |

*Nota: Tiempo real depende de hardware y carga del sistema*

### Tamaño de Archivos

| Tipo      | Tamaño medio | 50 docs |
|-----------|--------------|---------|
| PDF       | 30 KB        | 1.5 MB  |
| DOCX      | 25 KB        | 1.3 MB  |
| XLSX      | 15 KB        | 750 KB  |
| PNG       | 300 KB       | 15 MB   |
| **TOTAL** | -            | **~18 MB** |

---

## 🔄 Roadmap Futuro

### v1.1 (Próximo sprint)
- [ ] Descarga de archivos generados (ZIP)
- [ ] Templates personalizados por usuario
- [ ] Generar documentos específicos (solo facturas, solo contratos)

### v1.2 (2 sprints)
- [ ] Distribución personalizada con slider por categoría
- [ ] Preview de documentos antes de subir
- [ ] Scheduled generation (cron jobs)

### v2.0 (6 sprints)
- [ ] Templates basados en ontología formal
- [ ] Generación a partir de templates reales (subir plantilla)
- [ ] Datos relacionados entre documentos (expedientes completos)

---

## 📚 Referencias

- **Servicio Backend**: `backend/services/synthetic_data_service.py`
- **API Router**: `backend/api/v1/synthetic.py`
- **Frontend Component**: `frontend/src/pages/AdminSyntheticData.tsx`
- **Generador Original**: `scripts/generate_synthetic_data.py`
- **Guía Completa**: `docs/SYNTHETIC_DATA_GUIDE.md`

---

**Última actualización**: 9 de Octubre 2025  
**Mantenedor**: Equipo FinancIA 2030
