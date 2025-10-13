# 📡 API Reference - Sistema de Validación
## FinancIA DMS - Validation Endpoints

---

## 📋 Índice

1. [Autenticación](#autenticación)
2. [Endpoints de Validación](#endpoints-de-validación)
3. [Endpoints de Dashboard](#endpoints-de-dashboard)
4. [Endpoints de Scheduler](#endpoints-de-scheduler)
5. [Endpoints de Notificaciones](#endpoints-de-notificaciones)
6. [WebSocket](#websocket)
7. [Schemas](#schemas)
8. [Rate Limiting](#rate-limiting)
9. [Códigos de Error](#códigos-de-error)

---

## 🔐 Autenticación

Todos los endpoints requieren autenticación mediante **JWT Bearer Token**.

### Obtener Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@financia.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Usar Token

```http
GET /api/validation/results/123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🔍 Endpoints de Validación

### 1. Validar Entidad Individual

Valida una entidad contra listas de sanciones.

```http
POST /api/validation/check-sanctions
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "entity_name": "Acme Corporation",
  "entity_type": "COMPANY",
  "sources": ["OFAC", "EU_SANCTIONS", "WORLD_BANK"]
}
```

**Response:** `200 OK`
```json
{
  "entity_name": "Acme Corporation",
  "entity_type": "COMPANY",
  "is_flagged": false,
  "confidence": 0.0,
  "results": [
    {
      "source": "OFAC",
      "matched": false,
      "confidence": 0.0,
      "checked_at": "2024-11-01T10:30:00Z"
    },
    {
      "source": "EU_SANCTIONS",
      "matched": false,
      "confidence": 0.0,
      "checked_at": "2024-11-01T10:30:01Z"
    },
    {
      "source": "WORLD_BANK",
      "matched": false,
      "confidence": 0.0,
      "checked_at": "2024-11-01T10:30:01Z"
    }
  ],
  "checked_at": "2024-11-01T10:30:00Z"
}
```

**Ejemplo con entidad flagged:**
```json
{
  "entity_name": "Rosneft Oil Company",
  "entity_type": "COMPANY",
  "is_flagged": true,
  "confidence": 0.96,
  "results": [
    {
      "source": "OFAC",
      "matched": true,
      "confidence": 0.96,
      "match_details": {
        "list_entry": "Rosneft Oil Company",
        "program": "Ukraine-Related Sanctions",
        "country": "Russia",
        "added_date": "2022-02-24"
      },
      "checked_at": "2024-11-01T10:30:00Z"
    }
  ],
  "checked_at": "2024-11-01T10:30:00Z"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/validation/check-sanctions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "Acme Corporation",
    "entity_type": "COMPANY",
    "sources": ["OFAC", "EU_SANCTIONS"]
  }'
```

---

### 2. Validación en Bulk

Valida múltiples entidades en una sola llamada.

```http
POST /api/validation/bulk-validate
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "entities": [
    {
      "name": "Acme Corporation",
      "type": "COMPANY"
    },
    {
      "name": "John Smith",
      "type": "PERSON"
    },
    {
      "name": "XYZ Industries",
      "type": "COMPANY"
    }
  ],
  "sources": ["OFAC", "EU_SANCTIONS"]
}
```

**Response:** `200 OK`
```json
{
  "total_entities": 3,
  "flagged_count": 0,
  "results": [
    {
      "entity_name": "Acme Corporation",
      "is_flagged": false,
      "confidence": 0.0
    },
    {
      "entity_name": "John Smith",
      "is_flagged": false,
      "confidence": 0.0
    },
    {
      "entity_name": "XYZ Industries",
      "is_flagged": false,
      "confidence": 0.0
    }
  ],
  "processing_time_seconds": 2.3
}
```

**Rate Limit:** 100 entidades por request

---

### 3. Verificar Registro Empresarial

Valida la existencia legal de una empresa.

```http
POST /api/validation/check-business-registry
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "company_name": "Acme Corporation S.A.",
  "country": "ES",
  "tax_id": "A12345678"
}
```

**Response:** `200 OK`
```json
{
  "company_name": "Acme Corporation S.A.",
  "exists": true,
  "legal_status": "ACTIVE",
  "registration_number": "A12345678",
  "registration_date": "2010-05-15",
  "directors": [
    {
      "name": "María García",
      "role": "CEO",
      "appointed_date": "2015-01-01"
    }
  ],
  "beneficial_owners": [
    {
      "name": "Juan Pérez",
      "ownership_percentage": 51.0
    }
  ],
  "checked_at": "2024-11-01T10:30:00Z"
}
```

---

### 4. Obtener Score ESG

Obtiene rating ESG de una empresa.

```http
POST /api/validation/check-esg
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "company_name": "Acme Corporation",
  "country": "US"
}
```

**Response:** `200 OK`
```json
{
  "company_name": "Acme Corporation",
  "esg_score": 72.5,
  "rating": "B",
  "breakdown": {
    "environmental": 68.0,
    "social": 75.0,
    "governance": 75.0
  },
  "controversies": [
    {
      "title": "Labor dispute in 2023",
      "severity": "MEDIUM",
      "date": "2023-06-15"
    }
  ],
  "last_updated": "2024-10-01T00:00:00Z"
}
```

---

### 5. Obtener Resultados de Validación

Obtiene los resultados de validación de un documento.

```http
GET /api/validation/results/{document_id}
Authorization: Bearer {token}
```

**Path Parameters:**
- `document_id` (string, required): ID del documento

**Response:** `200 OK`
```json
{
  "document_id": "abc123-def456-ghi789",
  "filename": "contrato_proveedor_2024.pdf",
  "validation_completed": true,
  "validation_date": "2024-11-01T10:30:00Z",
  "total_entities": 5,
  "flagged_entities": 0,
  "results": [
    {
      "entity_name": "Acme Corporation",
      "entity_type": "COMPANY",
      "is_flagged": false,
      "confidence": 0.0,
      "sources_checked": ["OFAC", "EU_SANCTIONS", "WORLD_BANK"]
    },
    {
      "entity_name": "John Smith",
      "entity_type": "PERSON",
      "is_flagged": false,
      "confidence": 0.0,
      "sources_checked": ["OFAC", "EU_SANCTIONS"]
    }
  ]
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Document not found"
}
```

---

### 6. Historial de Validaciones

Obtiene el historial de validaciones con filtros.

```http
GET /api/validation/history
Authorization: Bearer {token}
```

**Query Parameters:**
- `days` (integer, optional): Días hacia atrás (default: 7, max: 90)
- `entity_type` (string, optional): COMPANY | PERSON
- `source` (string, optional): OFAC | EU_SANCTIONS | WORLD_BANK
- `flagged_only` (boolean, optional): Solo entidades flagged (default: false)
- `limit` (integer, optional): Límite de resultados (default: 100, max: 1000)
- `offset` (integer, optional): Offset para paginación (default: 0)

**Example Request:**
```http
GET /api/validation/history?days=30&flagged_only=true&limit=50
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "total": 18,
  "limit": 50,
  "offset": 0,
  "results": [
    {
      "id": 1234,
      "entity_name": "Rosneft Oil Company",
      "entity_type": "COMPANY",
      "source": "OFAC",
      "is_flagged": true,
      "confidence": 0.96,
      "document_id": "abc123",
      "document_filename": "contrato_suministro_2024.pdf",
      "created_at": "2024-11-01T10:30:00Z"
    }
  ]
}
```

---

### 7. Sincronizar Listas de Sanciones

Fuerza sincronización manual de listas.

```http
GET /api/sanctions/sync
Authorization: Bearer {token}
```

**Query Parameters:**
- `source` (string, optional): OFAC | EU_SANCTIONS | WORLD_BANK | ALL (default: ALL)

**Response:** `200 OK`
```json
{
  "status": "success",
  "sources_synced": ["OFAC", "EU_SANCTIONS", "WORLD_BANK"],
  "total_entries": 1247,
  "updated_at": "2024-11-01T10:30:00Z",
  "processing_time_seconds": 15.3
}
```

**Note:** Esta operación puede tardar 10-30 segundos dependiendo del tamaño de las listas.

---

### 8. Listar Entradas de Listas

Obtiene entradas de listas de sanciones.

```http
GET /api/sanctions/lists
Authorization: Bearer {token}
```

**Query Parameters:**
- `source` (string, optional): OFAC | EU_SANCTIONS | WORLD_BANK
- `entity_type` (string, optional): COMPANY | PERSON
- `country` (string, optional): Código ISO país (e.g., "RU", "SY")
- `search` (string, optional): Búsqueda por nombre
- `limit` (integer, optional): Límite (default: 100, max: 1000)
- `offset` (integer, optional): Offset (default: 0)

**Example Request:**
```http
GET /api/sanctions/lists?source=OFAC&country=RU&limit=20
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "total": 156,
  "limit": 20,
  "offset": 0,
  "entries": [
    {
      "id": 1,
      "name": "Rosneft Oil Company",
      "entity_type": "COMPANY",
      "source": "OFAC",
      "country": "Russia",
      "program": "Ukraine-Related Sanctions",
      "added_date": "2022-02-24",
      "last_updated": "2024-11-01T00:00:00Z"
    }
  ]
}
```

---

## 📊 Endpoints de Dashboard

### 1. Estadísticas Generales

Obtiene KPIs del dashboard.

```http
GET /api/validation/dashboard/stats
Authorization: Bearer {token}
```

**Query Parameters:**
- `days` (integer, optional): Período en días (default: 30, max: 90)

**Response:** `200 OK`
```json
{
  "period_days": 30,
  "total_validations": 1250,
  "flagged_entities": 18,
  "flagged_percentage": 1.44,
  "documents_processed": 342,
  "compliance_rate": 98.56,
  "avg_validation_time_seconds": 2.1,
  "sources_breakdown": {
    "OFAC": 750,
    "EU_SANCTIONS": 375,
    "WORLD_BANK": 125
  },
  "entity_types_breakdown": {
    "COMPANY": 950,
    "PERSON": 300
  },
  "generated_at": "2024-11-01T10:30:00Z"
}
```

---

### 2. Tendencias Diarias

Obtiene datos para gráfico de tendencias.

```http
GET /api/validation/dashboard/trends
Authorization: Bearer {token}
```

**Query Parameters:**
- `days` (integer, optional): Período (default: 30, max: 90)

**Response:** `200 OK`
```json
{
  "period_days": 30,
  "data_points": [
    {
      "date": "2024-10-01",
      "total_validations": 45,
      "flagged_count": 1,
      "avg_confidence": 0.12
    },
    {
      "date": "2024-10-02",
      "total_validations": 52,
      "flagged_count": 0,
      "avg_confidence": 0.08
    }
  ]
}
```

---

### 3. Entidades Flagged

Lista de entidades detectadas en listas.

```http
GET /api/validation/dashboard/flagged
Authorization: Bearer {token}
```

**Query Parameters:**
- `days` (integer, optional): Período (default: 30)
- `min_confidence` (float, optional): Confianza mínima (0.0-1.0, default: 0.7)
- `limit` (integer, optional): Límite (default: 100)

**Response:** `200 OK`
```json
{
  "total": 18,
  "flagged_entities": [
    {
      "id": 1234,
      "entity_name": "Rosneft Oil Company",
      "entity_type": "COMPANY",
      "source": "OFAC",
      "confidence": 0.96,
      "program": "Ukraine-Related Sanctions",
      "country": "Russia",
      "document_id": "abc123",
      "document_filename": "contrato_suministro_2024.pdf",
      "uploaded_by": "maria.garcia@financia.com",
      "created_at": "2024-11-01T10:30:00Z",
      "status": "PENDING_REVIEW",
      "priority": "CRITICAL"
    }
  ]
}
```

---

## ⏰ Endpoints de Scheduler

### 1. Listar Jobs

Lista todos los jobs configurados.

```http
GET /api/scheduler/jobs
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "jobs": [
    {
      "id": "sync_sanctions",
      "name": "Sync Sanctions Lists",
      "trigger": "cron",
      "schedule": "0 2 * * *",
      "next_run": "2024-11-02T02:00:00Z",
      "last_run": "2024-11-01T02:00:00Z",
      "status": "SCHEDULED",
      "enabled": true
    },
    {
      "id": "revalidate_active",
      "name": "Revalidate Active Documents",
      "trigger": "cron",
      "schedule": "0 3 * * 1",
      "next_run": "2024-11-04T03:00:00Z",
      "last_run": "2024-10-28T03:00:00Z",
      "status": "SCHEDULED",
      "enabled": true
    }
  ]
}
```

---

### 2. Ejecutar Job Manualmente

Fuerza la ejecución de un job.

```http
POST /api/scheduler/trigger/{job_id}
Authorization: Bearer {token}
```

**Path Parameters:**
- `job_id` (string, required): ID del job

**Response:** `202 Accepted`
```json
{
  "job_id": "sync_sanctions",
  "status": "triggered",
  "message": "Job queued for execution",
  "estimated_duration_seconds": 30
}
```

---

### 3. Historial de Ejecuciones

Obtiene historial de ejecuciones de un job.

```http
GET /api/scheduler/jobs/{job_id}/history
Authorization: Bearer {token}
```

**Query Parameters:**
- `limit` (integer, optional): Límite (default: 50, max: 200)

**Response:** `200 OK`
```json
{
  "job_id": "sync_sanctions",
  "executions": [
    {
      "execution_id": "exec_12345",
      "started_at": "2024-11-01T02:00:00Z",
      "completed_at": "2024-11-01T02:00:15Z",
      "duration_seconds": 15.3,
      "status": "SUCCESS",
      "result": {
        "entries_synced": 1247,
        "sources": ["OFAC", "EU_SANCTIONS", "WORLD_BANK"]
      }
    },
    {
      "execution_id": "exec_12344",
      "started_at": "2024-10-31T02:00:00Z",
      "completed_at": "2024-10-31T02:00:18Z",
      "duration_seconds": 18.1,
      "status": "SUCCESS",
      "result": {
        "entries_synced": 1245,
        "sources": ["OFAC", "EU_SANCTIONS", "WORLD_BANK"]
      }
    }
  ]
}
```

---

## 📧 Endpoints de Notificaciones

### 1. Enviar Notificación Manual

Envía una notificación de prueba.

```http
POST /api/notifications/send
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "level": "HIGH",
  "message": "Test notification",
  "details": {
    "entity_name": "Test Entity",
    "confidence": 0.95
  },
  "channels": ["EMAIL", "SLACK"],
  "recipients": {
    "email": ["compliance@financia.com"],
    "slack": ["#compliance-alerts"]
  }
}
```

**Response:** `200 OK`
```json
{
  "notification_id": "notif_12345",
  "status": "sent",
  "channels_sent": ["EMAIL", "SLACK"],
  "sent_at": "2024-11-01T10:30:00Z"
}
```

---

### 2. Configurar Preferencias

Configura preferencias de notificación para un usuario.

```http
PUT /api/notifications/preferences
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "channels": {
    "email": true,
    "slack": true,
    "sms": false
  },
  "priority_threshold": "HIGH",
  "quiet_hours": {
    "enabled": true,
    "start": "22:00",
    "end": "08:00",
    "timezone": "Europe/Madrid"
  }
}
```

**Response:** `200 OK`
```json
{
  "user_id": "user_123",
  "preferences": {
    "channels": {
      "email": true,
      "slack": true,
      "sms": false
    },
    "priority_threshold": "HIGH",
    "quiet_hours": {
      "enabled": true,
      "start": "22:00",
      "end": "08:00",
      "timezone": "Europe/Madrid"
    }
  },
  "updated_at": "2024-11-01T10:30:00Z"
}
```

---

## 🔌 WebSocket

### Conectar al WebSocket

Recibe actualizaciones en tiempo real de validaciones.

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/validation?token=YOUR_JWT_TOKEN');

ws.onopen = () => {
  console.log('Connected to validation WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New validation:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket connection closed');
};
```

### Mensajes Recibidos

**Validación Completada:**
```json
{
  "type": "validation_completed",
  "data": {
    "document_id": "abc123",
    "filename": "contrato_2024.pdf",
    "total_entities": 5,
    "flagged_entities": 0,
    "timestamp": "2024-11-01T10:30:00Z"
  }
}
```

**Entidad Flagged:**
```json
{
  "type": "entity_flagged",
  "data": {
    "entity_name": "Rosneft Oil Company",
    "entity_type": "COMPANY",
    "source": "OFAC",
    "confidence": 0.96,
    "document_id": "abc123",
    "priority": "CRITICAL",
    "timestamp": "2024-11-01T10:30:00Z"
  }
}
```

---

## 📋 Schemas

### ValidationRequest

```typescript
interface ValidationRequest {
  entity_name: string;          // Nombre de la entidad
  entity_type: "COMPANY" | "PERSON";
  sources?: string[];           // ["OFAC", "EU_SANCTIONS", "WORLD_BANK"]
}
```

### ValidationResult

```typescript
interface ValidationResult {
  entity_name: string;
  entity_type: "COMPANY" | "PERSON";
  is_flagged: boolean;
  confidence: number;           // 0.0 - 1.0
  results: SourceResult[];
  checked_at: string;           // ISO 8601 timestamp
}

interface SourceResult {
  source: "OFAC" | "EU_SANCTIONS" | "WORLD_BANK";
  matched: boolean;
  confidence: number;
  match_details?: MatchDetails;
  checked_at: string;
}

interface MatchDetails {
  list_entry: string;
  program: string;
  country: string;
  added_date: string;
}
```

### BulkValidationRequest

```typescript
interface BulkValidationRequest {
  entities: {
    name: string;
    type: "COMPANY" | "PERSON";
  }[];
  sources?: string[];
}
```

### DashboardStats

```typescript
interface DashboardStats {
  period_days: number;
  total_validations: number;
  flagged_entities: number;
  flagged_percentage: number;
  documents_processed: number;
  compliance_rate: number;
  avg_validation_time_seconds: number;
  sources_breakdown: Record<string, number>;
  entity_types_breakdown: Record<string, number>;
  generated_at: string;
}
```

---

## ⏱️ Rate Limiting

### Límites por Endpoint

| Endpoint | Rate Limit | Ventana |
|----------|------------|---------|
| `/validation/check-sanctions` | 1000 req/min | Por usuario |
| `/validation/bulk-validate` | 100 req/min | Por usuario |
| `/validation/results/*` | 2000 req/min | Por usuario |
| `/validation/history` | 500 req/min | Por usuario |
| `/dashboard/*` | 1000 req/min | Por usuario |
| `/scheduler/*` | 100 req/min | Por usuario |

### Headers de Rate Limit

Cada respuesta incluye headers de rate limit:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1698854400
```

### Response cuando se excede el límite

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "detail": "Rate limit exceeded",
  "limit": 1000,
  "window_seconds": 60,
  "retry_after": 45
}
```

---

## ❌ Códigos de Error

### Códigos HTTP

| Código | Significado | Descripción |
|--------|-------------|-------------|
| 200 | OK | Solicitud exitosa |
| 201 | Created | Recurso creado exitosamente |
| 202 | Accepted | Solicitud aceptada para procesamiento asíncrono |
| 400 | Bad Request | Parámetros inválidos |
| 401 | Unauthorized | Token inválido o expirado |
| 403 | Forbidden | Sin permisos suficientes |
| 404 | Not Found | Recurso no encontrado |
| 422 | Unprocessable Entity | Error de validación de datos |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Error del servidor |
| 503 | Service Unavailable | Servicio temporalmente no disponible |

### Formato de Error

```json
{
  "detail": "Description of the error",
  "error_code": "VALIDATION_001",
  "timestamp": "2024-11-01T10:30:00Z",
  "request_id": "req_abc123"
}
```

### Códigos de Error Específicos

| Código | Descripción |
|--------|-------------|
| `VALIDATION_001` | Entity name is required |
| `VALIDATION_002` | Invalid entity type |
| `VALIDATION_003` | Invalid source specified |
| `VALIDATION_004` | Too many entities in bulk request (max 100) |
| `AUTH_001` | Invalid or expired token |
| `AUTH_002` | Insufficient permissions |
| `RATE_LIMIT_001` | Rate limit exceeded |
| `EXTERNAL_API_001` | External API unavailable |
| `EXTERNAL_API_002` | External API timeout |

---

## 📝 Ejemplos Completos

### Ejemplo 1: Validar y Obtener Resultados

```bash
# 1. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@financia.com","password":"SecurePass123!"}' \
  | jq -r '.access_token')

# 2. Validar entidad
curl -X POST "http://localhost:8000/api/validation/check-sanctions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "Acme Corporation",
    "entity_type": "COMPANY",
    "sources": ["OFAC", "EU_SANCTIONS"]
  }' | jq .

# 3. Obtener estadísticas del dashboard
curl -X GET "http://localhost:8000/api/validation/dashboard/stats?days=30" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Ejemplo 2: Validación en Bulk con Manejo de Errores

```python
import requests
import time

API_BASE = "http://localhost:8000/api"
TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Preparar entidades para validar
entities = [
    {"name": "Acme Corp", "type": "COMPANY"},
    {"name": "John Smith", "type": "PERSON"},
    {"name": "XYZ Industries", "type": "COMPANY"},
]

# Validar en bulk con retry
max_retries = 3
for attempt in range(max_retries):
    try:
        response = requests.post(
            f"{API_BASE}/validation/bulk-validate",
            headers=headers,
            json={
                "entities": entities,
                "sources": ["OFAC", "EU_SANCTIONS"]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Validación exitosa: {results['total_entities']} entidades")
            print(f"🚨 Flagged: {results['flagged_count']}")
            break
        elif response.status_code == 429:
            # Rate limit - esperar y reintentar
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"⏰ Rate limit - esperando {retry_after}s...")
            time.sleep(retry_after)
        else:
            print(f"❌ Error: {response.status_code} - {response.json()}")
            break
            
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout - reintento {attempt + 1}/{max_retries}")
        time.sleep(5)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        break
```

### Ejemplo 3: WebSocket con Reconexión

```javascript
class ValidationWebSocket {
  constructor(token) {
    this.token = token;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.connect();
  }

  connect() {
    this.ws = new WebSocket(
      `ws://localhost:8000/ws/validation?token=${this.token}`
    );

    this.ws.onopen = () => {
      console.log('✅ Connected to validation WebSocket');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('🔌 WebSocket connection closed');
      this.reconnect();
    };
  }

  handleMessage(data) {
    switch (data.type) {
      case 'validation_completed':
        console.log('✅ Validation completed:', data.data);
        // Update UI
        break;
      case 'entity_flagged':
        console.log('🚨 Entity flagged:', data.data);
        // Show alert
        break;
      default:
        console.log('📨 Unknown message type:', data.type);
    }
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      console.log(`🔄 Reconnecting in ${delay/1000}s... (attempt ${this.reconnectAttempts})`);
      setTimeout(() => this.connect(), delay);
    } else {
      console.error('❌ Max reconnection attempts reached');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Uso
const ws = new ValidationWebSocket('your_jwt_token_here');
```

---

## 🔗 Enlaces Relacionados

- [USER_GUIDE.md](./USER_GUIDE.md) - Guía para usuarios finales
- [ADMIN_GUIDE.md](./ADMIN_GUIDE.md) - Guía para administradores
- [SPRINT6_COMPLETE.md](./SPRINT6_COMPLETE.md) - Documentación completa Sprint 6
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Guía de despliegue

---

**Versión:** 1.0  
**Última actualización:** Noviembre 2024  
**Mantenido por:** Equipo FinancIA DMS
