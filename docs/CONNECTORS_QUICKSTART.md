# 🔌 Enterprise Connectors - Guía de Inicio Rápido

## Conectores Disponibles

### ✅ SharePoint Online/On-Premises
Sincroniza documentos desde Microsoft SharePoint.

### ✅ SAP DMS
Integra con SAP Document Management Service.

### 🔜 Alfresco (Futuro)
Conector para Alfresco ECM.

### 🔜 Microsoft Exchange (Futuro)
Ingesta de emails como documentos.

---

## 📋 Configuración Rápida

### 1. SharePoint Connector

#### Paso 1: Registrar aplicación en Azure AD

1. Ir a [Azure Portal](https://portal.azure.com)
2. Azure Active Directory → App registrations → New registration
3. Nombre: "FinancIA DMS SharePoint Connector"
4. Supported account types: "Single tenant"
5. Redirect URI: (dejar vacío para app-to-app)
6. **Registrar**

#### Paso 2: Configurar permisos

1. API permissions → Add a permission → Microsoft Graph
2. Application permissions → Sites:
   - `Sites.Read.All` (Leer sitios)
   - `Files.ReadWrite.All` (Leer/escribir archivos)
3. **Grant admin consent**

#### Paso 3: Crear Client Secret

1. Certificates & secrets → New client secret
2. Description: "FinancIA Connector Secret"
3. Expires: 24 months
4. **Copiar el Value (secret)** ⚠️ Solo se muestra una vez

#### Paso 4: Obtener IDs

- **Tenant ID**: Overview → Directory (tenant) ID
- **Client ID**: Overview → Application (client) ID
- **Client Secret**: El value copiado en Paso 3

#### Paso 5: Configurar variables de entorno

```bash
# .env
SHAREPOINT_TENANT_ID=your-tenant-id-here
SHAREPOINT_CLIENT_ID=your-client-id-here
SHAREPOINT_CLIENT_SECRET=your-secret-here
```

#### Paso 6: Configurar sitios en `config/connectors.yaml`

```yaml
sharepoint:
  enabled: true
  sites:
    - name: "Corporate Documents"
      site_id: "yourcompany.sharepoint.com,abc123-def456"
      libraries:
        - "Shared Documents"
        - "Contracts"
```

#### Paso 7: Obtener Site ID

```python
# Script para obtener site IDs
from backend.connectors.sharepoint_connector import SharePointConnector, SharePointConfig

config = SharePointConfig(
    enabled=True,
    name="SharePoint",
    type="sharepoint",
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-secret"
)

async def list_sites():
    async with SharePointConnector(config) as connector:
        sites = await connector.list_repositories()
        for site in sites:
            print(f"Name: {site['name']}")
            print(f"ID: {site['id']}")
            print(f"URL: {site['url']}")
            print("---")

# Run
import asyncio
asyncio.run(list_sites())
```

---

### 2. SAP DMS Connector

#### Paso 1: Obtener credenciales SAP

Contactar al administrador SAP para obtener:
- **URL** del servicio SAP DMS
- **Username** con permisos de lectura de documentos
- **Password**
- **Client** (típicamente "100" o "200")

#### Paso 2: Configurar variables

```bash
# .env
SAP_DMS_URL=https://sap-dms.company.com
SAP_USERNAME=dms_readonly_user
SAP_PASSWORD=your-sap-password
SAP_CLIENT=100
```

#### Paso 3: Configurar repositorios en `config/connectors.yaml`

```yaml
sap_dms:
  enabled: true
  repositories:
    - id: "FI_DOCUMENTS"
      name: "Financial Documents"
      sync_filters:
        status: ["active", "approved"]
```

---

## 🚀 Uso Básico

### Listar Sitios/Repositorios

```python
from backend.connectors import SharePointConnector, SharePointConfig

config = SharePointConfig(...)

async with SharePointConnector(config) as connector:
    repos = await connector.list_repositories()
    for repo in repos:
        print(f"{repo['name']}: {repo['id']}")
```

### Listar Documentos

```python
async with SharePointConnector(config) as connector:
    docs = await connector.list_documents(
        repository_id="site-123",
        path="Shared Documents",
        filters={"file_types": [".pdf", ".docx"]}
    )
    
    for doc in docs:
        print(f"{doc.name} ({doc.size} bytes)")
```

### Descargar Documento

```python
async with SharePointConnector(config) as connector:
    content = await connector.download_document(
        document_id="site-123|drive-456|item-789"
    )
    
    with open("downloaded.pdf", "wb") as f:
        f.write(content)
```

### Sincronizar a FinancIA

```python
async with SharePointConnector(config) as connector:
    stats = await connector.sync_to_financia(
        repository_id="site-123",
        filters={"file_types": [".pdf"]}
    )
    
    print(f"Synced: {stats['synced']}/{stats['total_documents']}")
    print(f"Errors: {stats['errors']}")
```

---

## 🧪 Testing

### Ejecutar tests

```bash
# Todos los tests de conectores
pytest tests/connectors/ -v

# Solo SharePoint
pytest tests/connectors/test_sharepoint_connector.py -v

# Tests de integración (requiere credenciales reales)
SHAREPOINT_TENANT_ID=xxx pytest tests/connectors/test_sharepoint_connector.py::TestSharePointConnectorIntegration -v
```

### Tests disponibles

- ✅ `test_initialization`: Inicialización del conector
- ✅ `test_authenticate_success`: Autenticación exitosa
- ✅ `test_authenticate_failure`: Manejo de errores de auth
- ✅ `test_test_connection`: Test de conexión
- ✅ `test_list_repositories`: Listar sitios
- ✅ `test_list_documents`: Listar documentos
- ✅ `test_list_documents_with_filters`: Filtros de búsqueda
- ✅ `test_get_document`: Obtener documento específico
- ✅ `test_download_document`: Descargar contenido
- ✅ `test_map_metadata`: Mapeo de metadata
- ✅ `test_not_authenticated_raises_error`: Validación de auth

---

## 📊 Monitoreo

### Logs

Los conectores generan logs estructurados:

```python
import logging

logging.getLogger("backend.connectors").setLevel(logging.DEBUG)
```

Ejemplo de log:
```
INFO: Authenticating with Microsoft Graph API
INFO: Authentication successful
INFO: Listing SharePoint sites
INFO: Found 5 sites
INFO: Starting sync from site-123
INFO: Synced document: contract-2024.pdf
INFO: Sync completed: 42/45 documents
```

### Métricas Prometheus

Los conectores exponen métricas:

```
# Documentos sincronizados
connector_documents_synced_total{connector="sharepoint"} 1250

# Errores de sincronización
connector_sync_errors_total{connector="sharepoint"} 3

# Duración de sincronización
connector_sync_duration_seconds{connector="sharepoint"} 45.2

# Estado de conexión
connector_connection_status{connector="sharepoint"} 1
```

---

## 🔄 Sincronización Automática

### Scheduler de Sincronización

Configurar en `config/connectors.yaml`:

```yaml
sharepoint:
  sync_schedule: "0 */6 * * *"  # Cada 6 horas
  
sap_dms:
  sync_schedule: "0 2 * * *"    # Diario a las 2 AM
```

Formato cron:
- `*/30 * * * *` - Cada 30 minutos
- `0 * * * *` - Cada hora
- `0 */6 * * *` - Cada 6 horas
- `0 2 * * *` - Diario a las 2 AM
- `0 0 * * 0` - Semanal (domingos a medianoche)

### Webhooks (SharePoint)

Para sincronización en tiempo real:

```yaml
sharepoint:
  webhook_enabled: true
  webhook_expiration_days: 30
```

SharePoint enviará notificaciones cuando:
- Se cree un nuevo documento
- Se modifique un documento
- Se elimine un documento

---

## 🐛 Troubleshooting

### Error: "Not authenticated"

**Causa:** No se llamó a `authenticate()` o el token expiró.

**Solución:**
```python
# Usar context manager (recomendado)
async with SharePointConnector(config) as connector:
    # Automáticamente autentica
    await connector.list_repositories()

# O autenticar manualmente
connector = SharePointConnector(config)
await connector.authenticate()
```

### Error: "Invalid client credentials"

**Causa:** Client ID o Client Secret incorrectos.

**Solución:**
1. Verificar que copiaste el secret correctamente
2. Verificar que el secret no haya expirado
3. Generar nuevo secret en Azure Portal

### Error: "Insufficient privileges"

**Causa:** La aplicación no tiene los permisos correctos.

**Solución:**
1. Ir a Azure AD → App registrations → Tu app
2. API permissions → Verificar que tenga:
   - `Sites.Read.All`
   - `Files.ReadWrite.All`
3. **Grant admin consent** (botón azul)

### Error: "Site not found"

**Causa:** Site ID incorrecto.

**Solución:**
1. Ejecutar script para listar sites (ver arriba)
2. Copiar el ID exacto
3. Actualizar `config/connectors.yaml`

### Performance lento

**Optimizaciones:**
```yaml
sharepoint:
  batch_size: 50        # Reducir si hay timeouts
  timeout_seconds: 600  # Aumentar para sitios grandes
  
  # Filtrar por biblioteca específica
  sites:
    - site_id: "xxx"
      libraries: ["Shared Documents"]  # Solo esta biblioteca
```

---

## 📚 Documentación Adicional

- [Microsoft Graph API Docs](https://learn.microsoft.com/en-us/graph/)
- [SharePoint REST API](https://learn.microsoft.com/en-us/sharepoint/dev/)
- [SAP DMS Documentation](https://help.sap.com/docs/DMS)
- [Azure AD App Registration](https://learn.microsoft.com/en-us/azure/active-directory/develop/)

---

## 🤝 Soporte

**Issues:** Crear issue en GitHub con:
- Logs del conector
- Configuración (sin secrets)
- Versión de Python y dependencias

**Email:** support@financia.com

---

**Última actualización:** 10 de octubre de 2025
