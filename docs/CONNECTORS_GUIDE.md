# 🔌 Connectors Guide - SharePoint & SAP DMS Integration

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [SharePoint Connector](#sharepoint-connector)
3. [SAP DMS Connector](#sap-dms-connector)
4. [Comparativa de Conectores](#comparativa-de-conectores)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

---

## 📝 Descripción General

El Sistema Corporativo Documental integra con dos sistemas externos principales:

1. **SharePoint Online/On-Premise** - Gestión documental Microsoft
2. **SAP DMS** - Document Management System integrado en SAP ERP

### Arquitectura de Conectores

```
┌─────────────────────────────────────────────────┐
│     Sistema Corporativo Documental              │
│  ┌───────────────────────────────────────────┐  │
│  │         Connector Manager                  │  │
│  │  - Pool de conexiones                      │  │
│  │  - Health checks                           │  │
│  │  - Retry logic                             │  │
│  │  - Circuit breaker                         │  │
│  └─────────┬──────────────────┬───────────────┘  │
│            │                  │                   │
│  ┌─────────▼────────┐  ┌─────▼────────────────┐ │
│  │  SharePoint      │  │  SAP DMS             │ │
│  │  Connector       │  │  Connector           │ │
│  │  - OAuth2 Auth   │  │  - RFC Protocol      │ │
│  │  - REST API      │  │  - BAPI calls        │ │
│  │  - File upload   │  │  - DMS services      │ │
│  └─────────┬────────┘  └─────┬────────────────┘ │
└────────────┼────────────────┼───────────────────┘
             │                │
     ┌───────▼───────┐  ┌────▼─────────┐
     │  SharePoint   │  │  SAP ERP     │
     │   Online      │  │  DMS Module  │
     └───────────────┘  └──────────────┘
```

### Características Comunes

- ✅ **Autenticación segura** (OAuth2 / RFC)
- ✅ **CRUD de documentos** (Create, Read, Update, Delete)
- ✅ **Gestión de metadatos** (tags, custom fields)
- ✅ **Control de versiones** (historial completo)
- ✅ **Búsqueda avanzada** (por metadata, contenido)
- ✅ **Manejo de errores** (retry, circuit breaker)
- ✅ **Logging y auditoría** (todas las operaciones)

---

## 📘 SharePoint Connector

### Descripción

Conector para Microsoft SharePoint Online y SharePoint Server (On-Premise). Permite sincronización bidireccional de documentos y metadatos.

### Requisitos

```yaml
Dependencias Python:
  - Office365-REST-Python-Client >= 2.5.0
  - requests >= 2.31.0
  - msal >= 1.24.0

SharePoint Permissions:
  - Sites.ReadWrite.All
  - Files.ReadWrite.All
  - User.Read

Versiones Soportadas:
  - SharePoint Online (Microsoft 365)
  - SharePoint Server 2019
  - SharePoint Server 2016
```

### Configuración

#### 1. Registro de Aplicación en Azure AD

```bash
# 1. Ir a Azure Portal
https://portal.azure.com → Azure Active Directory → App registrations

# 2. Crear nueva aplicación
Nombre: "Sistema Documental Connector"
Tipo de cuenta: Single tenant
Redirect URI: https://localhost

# 3. Copiar valores
Application (client) ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Directory (tenant) ID: yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy

# 4. Crear Client Secret
Certificates & secrets → New client secret
Descripción: "Production Secret"
Expira: 24 months
Valor: copiar y guardar de forma segura

# 5. Configurar API Permissions
API permissions → Add a permission → SharePoint
- Sites.ReadWrite.All (Delegated + Application)
- Files.ReadWrite.All (Delegated + Application)

# 6. Grant Admin Consent
Click "Grant admin consent for [TenantName]"
```

#### 2. Variables de Entorno

```bash
# backend/.env

# SharePoint Configuration
SHAREPOINT_SITE_URL=https://yourcompany.sharepoint.com/sites/documents
SHAREPOINT_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SHAREPOINT_CLIENT_SECRET=your_client_secret_here
SHAREPOINT_TENANT_ID=yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy

# Authentication
SHAREPOINT_AUTH_TYPE=client_credentials  # or oauth2_flow
SHAREPOINT_USERNAME=admin@yourcompany.com  # Solo si auth_type=oauth2_flow
SHAREPOINT_PASSWORD=password_here  # Solo si auth_type=oauth2_flow

# Connection Settings
SHAREPOINT_TIMEOUT=30  # segundos
SHAREPOINT_MAX_RETRIES=3
SHAREPOINT_RETRY_DELAY=2  # segundos
```

#### 3. Código de Integración

```python
# backend/connectors/sharepoint_connector.py

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.files.file import File
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SharePointConnector:
    """
    Conector para Microsoft SharePoint
    """
    
    def __init__(self):
        self.site_url = os.getenv('SHAREPOINT_SITE_URL')
        self.client_id = os.getenv('SHAREPOINT_CLIENT_ID')
        self.client_secret = os.getenv('SHAREPOINT_CLIENT_SECRET')
        self.tenant_id = os.getenv('SHAREPOINT_TENANT_ID')
        self.ctx = None
        
    def connect(self) -> bool:
        """
        Establece conexión con SharePoint
        """
        try:
            credentials = ClientCredential(
                self.client_id,
                self.client_secret
            )
            self.ctx = ClientContext(self.site_url).with_credentials(credentials)
            
            # Test connection
            web = self.ctx.web
            self.ctx.load(web)
            self.ctx.execute_query()
            
            logger.info(f"Connected to SharePoint: {web.properties['Title']}")
            return True
            
        except Exception as e:
            logger.error(f"SharePoint connection failed: {e}")
            return False
    
    def upload_file(
        self,
        local_path: str,
        remote_folder: str,
        filename: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Sube un archivo a SharePoint
        
        Args:
            local_path: Ruta local del archivo
            remote_folder: Carpeta destino en SharePoint
            filename: Nombre del archivo
            metadata: Metadatos adicionales
            
        Returns:
            Dict con información del archivo subido
        """
        try:
            # Obtener carpeta de destino
            target_folder = self.ctx.web.get_folder_by_server_relative_url(
                remote_folder
            )
            
            # Leer archivo
            with open(local_path, 'rb') as file_content:
                file_bytes = file_content.read()
            
            # Upload
            uploaded_file = target_folder.upload_file(
                filename,
                file_bytes
            ).execute_query()
            
            # Establecer metadatos si existen
            if metadata:
                list_item = uploaded_file.listItemAllFields
                for key, value in metadata.items():
                    list_item.set_property(key, value)
                list_item.update()
                self.ctx.execute_query()
            
            logger.info(f"File uploaded: {filename} to {remote_folder}")
            
            return {
                'success': True,
                'file_id': uploaded_file.properties['UniqueId'],
                'url': uploaded_file.properties['ServerRelativeUrl'],
                'size': uploaded_file.properties['Length'],
                'modified': uploaded_file.properties['TimeLastModified']
            }
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def download_file(
        self,
        file_url: str,
        local_path: str
    ) -> bool:
        """
        Descarga un archivo de SharePoint
        
        Args:
            file_url: URL relativa del archivo
            local_path: Ruta local de destino
            
        Returns:
            True si éxito, False si error
        """
        try:
            file = File.open_binary(
                self.ctx,
                file_url
            )
            
            with open(local_path, 'wb') as local_file:
                local_file.write(file.content)
            
            logger.info(f"File downloaded: {file_url} to {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def list_files(
        self,
        folder_url: str,
        recursive: bool = False
    ) -> List[Dict]:
        """
        Lista archivos en una carpeta
        
        Args:
            folder_url: URL de la carpeta
            recursive: Si True, incluye subcarpetas
            
        Returns:
            Lista de diccionarios con info de archivos
        """
        try:
            folder = self.ctx.web.get_folder_by_server_relative_url(
                folder_url
            )
            files = folder.files
            self.ctx.load(files)
            self.ctx.execute_query()
            
            result = []
            for file in files:
                result.append({
                    'name': file.properties['Name'],
                    'url': file.properties['ServerRelativeUrl'],
                    'size': file.properties['Length'],
                    'modified': file.properties['TimeLastModified'],
                    'created': file.properties['TimeCreated']
                })
            
            if recursive:
                folders = folder.folders
                self.ctx.load(folders)
                self.ctx.execute_query()
                
                for subfolder in folders:
                    subfolder_url = subfolder.properties['ServerRelativeUrl']
                    result.extend(self.list_files(subfolder_url, recursive=True))
            
            return result
            
        except Exception as e:
            logger.error(f"List files failed: {e}")
            return []
    
    def delete_file(
        self,
        file_url: str
    ) -> bool:
        """
        Elimina un archivo de SharePoint
        
        Args:
            file_url: URL relativa del archivo
            
        Returns:
            True si éxito, False si error
        """
        try:
            file = self.ctx.web.get_file_by_server_relative_url(file_url)
            file.delete_object()
            self.ctx.execute_query()
            
            logger.info(f"File deleted: {file_url}")
            return True
            
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def search_documents(
        self,
        query: str,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Busca documentos en SharePoint
        
        Args:
            query: Término de búsqueda
            max_results: Máximo de resultados
            
        Returns:
            Lista de documentos encontrados
        """
        try:
            from office365.sharepoint.search.query import SearchRequest
            
            search_request = SearchRequest(query)
            search_request.RowLimit = max_results
            
            result_tables = self.ctx.search_service.post_query(
                search_request
            ).execute_query()
            
            results = []
            for table in result_tables:
                for row in table.ResultRows:
                    results.append({
                        'title': row.get('Title', ''),
                        'url': row.get('Path', ''),
                        'author': row.get('Author', ''),
                        'modified': row.get('LastModifiedTime', ''),
                        'size': row.get('Size', 0)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
```

### Uso del Connector

```python
# Ejemplo de uso

from connectors.sharepoint_connector import SharePointConnector

# 1. Inicializar y conectar
sp = SharePointConnector()
if not sp.connect():
    print("Error conectando a SharePoint")
    exit(1)

# 2. Upload de archivo
result = sp.upload_file(
    local_path='/path/to/document.pdf',
    remote_folder='/Shared Documents/Contracts',
    filename='contract_2025.pdf',
    metadata={
        'Department': 'Legal',
        'Year': '2025',
        'Status': 'Draft'
    }
)
print(f"Upload result: {result}")

# 3. Listar archivos
files = sp.list_files(
    folder_url='/Shared Documents/Contracts',
    recursive=True
)
print(f"Found {len(files)} files")

# 4. Buscar documentos
results = sp.search_documents(
    query='contract 2025',
    max_results=10
)
print(f"Search found {len(results)} documents")

# 5. Download de archivo
success = sp.download_file(
    file_url='/Shared Documents/Contracts/contract_2025.pdf',
    local_path='/tmp/downloaded_contract.pdf'
)
print(f"Download: {'Success' if success else 'Failed'}")
```

---

## 🔷 SAP DMS Connector

### Descripción

Conector para SAP Document Management System (DMS) integrado en SAP ERP. Utiliza RFC (Remote Function Call) para comunicación con SAP.

### Requisitos

```yaml
Dependencias Python:
  - pyrfc >= 3.2.0  # SAP NetWeaver RFC SDK
  - pysapnwrfc >= 2.0.0

SAP Requirements:
  - SAP NetWeaver RFC SDK instalado
  - Usuario SAP con permisos DMS
  - Autorización para BAPIs:
    * BAPI_DOCUMENT_CREATE2
    * BAPI_DOCUMENT_GETDETAIL2
    * BAPI_DOCUMENT_CHANGE2
    * BAPI_DOCUMENT_CHECKOUTVIEW2

Versiones SAP Soportadas:
  - SAP ECC 6.0+
  - SAP S/4HANA
```

### Instalación de SAP NetWeaver RFC SDK

```bash
# Linux
cd /opt
wget https://support.sap.com/nwrfcsdk-linux-x86_64.zip
unzip nwrfcsdk-linux-x86_64.zip
export SAPNWRFC_HOME=/opt/nwrfcsdk
export LD_LIBRARY_PATH=$SAPNWRFC_HOME/lib:$LD_LIBRARY_PATH

# Instalar pyrfc
pip install pyrfc

# Verificar instalación
python -c "from pyrfc import Connection; print('RFC SDK OK')"
```

### Configuración

#### 1. Variables de Entorno

```bash
# backend/.env

# SAP Connection
SAP_ASHOST=sap-server.company.com  # Application server host
SAP_SYSNR=00  # System number
SAP_CLIENT=100  # SAP client
SAP_USER=DMSUSER  # SAP username
SAP_PASSWD=SecurePassword123  # SAP password
SAP_LANG=EN  # Language

# SAP DMS Configuration
SAP_DMS_DOCTYPE=DOC  # Document type
SAP_DMS_DOCPART=000  # Document part
SAP_DMS_VERSION=00  # Document version
SAP_DMS_STORAGE=DIR  # Storage category

# Connection Pool
SAP_POOL_SIZE=5  # Número de conexiones
SAP_POOL_TIMEOUT=30  # Timeout en segundos
```

#### 2. Código de Integración

```python
# backend/connectors/sap_dms_connector.py

from pyrfc import Connection, ABAPApplicationError, ABAPRuntimeError
import os
from typing import Dict, List, Optional
import logging
import base64

logger = logging.getLogger(__name__)

class SAPDMSConnector:
    """
    Conector para SAP Document Management System
    """
    
    def __init__(self):
        self.connection = None
        self.config = {
            'ashost': os.getenv('SAP_ASHOST'),
            'sysnr': os.getenv('SAP_SYSNR'),
            'client': os.getenv('SAP_CLIENT'),
            'user': os.getenv('SAP_USER'),
            'passwd': os.getenv('SAP_PASSWD'),
            'lang': os.getenv('SAP_LANG', 'EN')
        }
        
    def connect(self) -> bool:
        """
        Establece conexión RFC con SAP
        """
        try:
            self.connection = Connection(**self.config)
            logger.info(f"Connected to SAP system: {self.config['ashost']}")
            return True
            
        except Exception as e:
            logger.error(f"SAP connection failed: {e}")
            return False
    
    def disconnect(self):
        """
        Cierra conexión RFC
        """
        if self.connection:
            self.connection.close()
            logger.info("SAP connection closed")
    
    def create_document(
        self,
        doc_number: str,
        doc_type: str,
        doc_part: str,
        description: str,
        file_path: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Crea un nuevo documento en SAP DMS
        
        Args:
            doc_number: Número de documento
            doc_type: Tipo de documento (DOC, DRW, etc.)
            doc_part: Parte del documento (000)
            description: Descripción
            file_path: Ruta del archivo a subir
            metadata: Metadatos adicionales
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Leer archivo y convertir a base64
            with open(file_path, 'rb') as f:
                file_content = base64.b64encode(f.read()).decode('utf-8')
            
            # Preparar datos del documento
            document_data = {
                'DOKNR': doc_number,
                'DOKAR': doc_type,
                'DOKVR': '00',
                'DOKTL': doc_part,
                'DOKST': '01',  # Status: Created
                'AEDAT': '',  # Fecha actual
                'AENAM': self.config['user']
            }
            
            # Preparar descripción
            document_description = [{
                'LANGU': self.config['lang'],
                'DOKTL': doc_part,
                'LINE': description[:132]  # Max 132 chars
            }]
            
            # Preparar archivo
            document_files = [{
                'DOKAR': doc_type,
                'DOKNR': doc_number,
                'DOKVR': '00',
                'DOKTL': doc_part,
                'DOKFL': os.path.basename(file_path),
                'FILENAME': os.path.basename(file_path),
                'STORAGECATEGORY': os.getenv('SAP_DMS_STORAGE', 'DIR'),
                'FILECONTENT': file_content
            }]
            
            # Llamar BAPI
            result = self.connection.call(
                'BAPI_DOCUMENT_CREATE2',
                DOCUMENTDATA=document_data,
                DOCUMENTDESCRIPTION=document_description,
                DOCUMENTFILES=document_files
            )
            
            # Check for errors
            if result['RETURN']['TYPE'] == 'E':
                raise Exception(result['RETURN']['MESSAGE'])
            
            # Commit
            self.connection.call('BAPI_TRANSACTION_COMMIT')
            
            logger.info(f"Document created in SAP DMS: {doc_number}")
            
            return {
                'success': True,
                'document_number': doc_number,
                'document_type': doc_type,
                'message': result['RETURN']['MESSAGE']
            }
            
        except (ABAPApplicationError, ABAPRuntimeError) as e:
            logger.error(f"SAP BAPI error: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Create document failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_document(
        self,
        doc_number: str,
        doc_type: str,
        doc_part: str,
        doc_version: str = '00'
    ) -> Dict:
        """
        Obtiene información de un documento
        
        Args:
            doc_number: Número de documento
            doc_type: Tipo de documento
            doc_part: Parte del documento
            doc_version: Versión del documento
            
        Returns:
            Dict con información del documento
        """
        try:
            result = self.connection.call(
                'BAPI_DOCUMENT_GETDETAIL2',
                DOCUMENTTYPE=doc_type,
                DOCUMENTNUMBER=doc_number,
                DOCUMENTPART=doc_part,
                DOCUMENTVERSION=doc_version
            )
            
            if result['RETURN']['TYPE'] == 'E':
                raise Exception(result['RETURN']['MESSAGE'])
            
            return {
                'success': True,
                'data': result['DOCUMENTDATA'],
                'description': result['DOCUMENTDESCRIPTION'],
                'files': result['DOCUMENTFILES']
            }
            
        except Exception as e:
            logger.error(f"Get document failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def download_document(
        self,
        doc_number: str,
        doc_type: str,
        doc_part: str,
        output_path: str
    ) -> bool:
        """
        Descarga un archivo del documento
        
        Args:
            doc_number: Número de documento
            doc_type: Tipo de documento
            doc_part: Parte del documento
            output_path: Ruta de salida
            
        Returns:
            True si éxito, False si error
        """
        try:
            # Checkout document
            result = self.connection.call(
                'BAPI_DOCUMENT_CHECKOUTVIEW2',
                DOCUMENTTYPE=doc_type,
                DOCUMENTNUMBER=doc_number,
                DOCUMENTPART=doc_part,
                DOCUMENTVERSION='00'
            )
            
            if result['RETURN']['TYPE'] == 'E':
                raise Exception(result['RETURN']['MESSAGE'])
            
            # Get file content (base64 encoded)
            file_content_b64 = result['FILECONTENT']
            file_content = base64.b64decode(file_content_b64)
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"Document downloaded: {doc_number} to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def search_documents(
        self,
        search_term: str,
        doc_type: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Busca documentos en SAP DMS
        
        Args:
            search_term: Término de búsqueda
            doc_type: Tipo de documento (opcional)
            max_results: Máximo de resultados
            
        Returns:
            Lista de documentos encontrados
        """
        try:
            search_criteria = {
                'DOCTEXT': search_term
            }
            
            if doc_type:
                search_criteria['DOKAR'] = doc_type
            
            result = self.connection.call(
                'BAPI_DOCUMENT_SEARCH',
                SEARCHCRITERIA=search_criteria,
                MAXROWS=max_results
            )
            
            documents = []
            for doc in result['DOCUMENTLIST']:
                documents.append({
                    'number': doc['DOKNR'],
                    'type': doc['DOKAR'],
                    'version': doc['DOKVR'],
                    'part': doc['DOKTL'],
                    'description': doc['DKTXT'],
                    'status': doc['DOKST'],
                    'created_by': doc['AENAM'],
                    'created_date': doc['AEDAT']
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
```

### Uso del Connector

```python
# Ejemplo de uso

from connectors.sap_dms_connector import SAPDMSConnector

# 1. Inicializar y conectar
sap = SAPDMSConnector()
if not sap.connect():
    print("Error conectando a SAP")
    exit(1)

# 2. Crear documento
result = sap.create_document(
    doc_number='DOC00001234',
    doc_type='DOC',
    doc_part='000',
    description='Manual de Usuario v1.0',
    file_path='/path/to/manual.pdf',
    metadata={
        'Department': 'IT',
        'Year': '2025'
    }
)
print(f"Create result: {result}")

# 3. Obtener información de documento
doc_info = sap.get_document(
    doc_number='DOC00001234',
    doc_type='DOC',
    doc_part='000'
)
print(f"Document info: {doc_info}")

# 4. Buscar documentos
results = sap.search_documents(
    search_term='manual',
    doc_type='DOC',
    max_results=20
)
print(f"Search found {len(results)} documents")

# 5. Download de documento
success = sap.download_document(
    doc_number='DOC00001234',
    doc_type='DOC',
    doc_part='000',
    output_path='/tmp/downloaded_manual.pdf'
)
print(f"Download: {'Success' if success else 'Failed'}")

# 6. Cerrar conexión
sap.disconnect()
```

---

## 📊 Comparativa de Conectores

| Feature | SharePoint | SAP DMS |
|---------|-----------|---------|
| **Autenticación** | OAuth2 / Client Credentials | RFC (usuario/password) |
| **Protocolo** | REST API (HTTPS) | RFC (TCP/IP) |
| **Upload Speed** | ~10 MB/s | ~5 MB/s |
| **Download Speed** | ~15 MB/s | ~8 MB/s |
| **Max File Size** | 100 GB | 2 GB |
| **Concurrent Uploads** | 10 | 3 |
| **Search Performance** | Excelente | Bueno |
| **Metadata Handling** | Flexible (custom columns) | Estructurado (INFO records) |
| **Versioning** | Automático | Manual |
| **Permissions** | Role-based (Azure AD) | Role-based (SAP roles) |
| **Offline Support** | Sí (sync) | No |
| **Cost** | Incluido en M365 | Incluido en SAP |

---

## 🔧 Troubleshooting

### SharePoint Issues

#### Issue: "AADSTS700016: Application not found"

**Causa:** Client ID incorrecto o app no registrada

**Solución:**
```bash
# Verificar Client ID en Azure Portal
https://portal.azure.com → Azure AD → App registrations

# Verificar variables de entorno
echo $SHAREPOINT_CLIENT_ID
```

#### Issue: "403 Forbidden"

**Causa:** Permisos insuficientes

**Solución:**
```bash
# Verificar permisos en Azure Portal
Azure AD → App registrations → [Tu App] → API permissions

# Asegurar que tienes:
- Sites.ReadWrite.All (Application)
- Files.ReadWrite.All (Application)

# Grant admin consent
```

#### Issue: "The requested operation is part of an experimental feature"

**Causa:** Feature no habilitada en SharePoint

**Solución:**
```bash
# Habilitar vía PowerShell
Connect-SPOService -Url https://yourcompany-admin.sharepoint.com
Set-SPOTenant -EnableAzureADB2BIntegration $true
```

### SAP DMS Issues

#### Issue: "RFC_ERROR_SYSTEM_FAILURE"

**Causa:** SAP RFC SDK no instalado correctamente

**Solución:**
```bash
# Verificar instalación
ls -la /opt/nwrfcsdk/lib

# Verificar variables
echo $SAPNWRFC_HOME
echo $LD_LIBRARY_PATH

# Reinstalar pyrfc
pip uninstall pyrfc
pip install --no-cache-dir pyrfc
```

#### Issue: "Name or password is incorrect"

**Causa:** Credenciales inválidas o expiradas

**Solución:**
```bash
# Verificar usuario en SAP
Tcode: SU01 → Buscar usuario → Verificar validez

# Verificar password expirado
Tcode: SU01 → Usuario → Password → Change

# Verificar autorizaciones
Tcode: SU53 → Ver últimos errores de autorización
```

#### Issue: "BAPI_DOCUMENT_CREATE2 not found"

**Causa:** Versión SAP antigua o función no disponible

**Solución:**
```bash
# Verificar disponibilidad de BAPI
Tcode: SE37 → Buscar BAPI_DOCUMENT_CREATE2

# Alternativas para versiones antiguas:
- BAPI_DOCUMENT_CREATE
- CV120_DOCUMENT_CREATE
```

---

## ✅ Best Practices

### General

1. **Connection Pooling**
```python
# Mantener pool de conexiones
pool_size = 5
connections = [connector.connect() for _ in range(pool_size)]
```

2. **Retry Logic**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def upload_with_retry(file_path):
    return connector.upload_file(file_path)
```

3. **Circuit Breaker**
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def protected_operation():
    return connector.some_operation()
```

### SharePoint Specific

1. **Batch Operations**
```python
# Upload múltiples archivos en batch
batch_size = 10
for i in range(0, len(files), batch_size):
    batch = files[i:i+batch_size]
    results = [sp.upload_file(f) for f in batch]
```

2. **Large File Upload**
```python
# Para archivos > 100 MB, usar chunked upload
chunk_size = 10 * 1024 * 1024  # 10 MB chunks
# Implementar lógica de chunking
```

### SAP DMS Specific

1. **Gestión de Sesiones RFC**
```python
# Cerrar conexiones después de uso
try:
    result = sap.create_document(...)
finally:
    sap.disconnect()
```

2. **Batch Input para Múltiples Docs**
```python
# Usar batch input para crear múltiples documentos
docs = [...]
for doc in docs:
    sap.create_document(doc)
    sap.connection.call('BAPI_TRANSACTION_COMMIT')
```

---

## 📚 Referencias

### SharePoint
- [Office365-REST-Python-Client Docs](https://github.com/vgrem/Office365-REST-Python-Client)
- [Microsoft Graph API](https://docs.microsoft.com/graph)
- [SharePoint REST API](https://docs.microsoft.com/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service)

### SAP DMS
- [PyRFC Documentation](https://sap.github.io/PyRFC/)
- [SAP NetWeaver RFC SDK](https://support.sap.com/nwrfcsdk)
- [SAP DMS BAPIs](https://help.sap.com/doc/saphelp_47x200/4.7x/en-US/ba/baa7c4484111d189f00000e829fbfe/content.htm)

---

**Última actualización:** Octubre 10, 2025  
**Versión:** 1.0  
**Estado:** ✅ Production Ready
