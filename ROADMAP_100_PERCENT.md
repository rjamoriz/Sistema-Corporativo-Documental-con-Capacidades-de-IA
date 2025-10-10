# 🎯 Roadmap para 100% Cobertura RFP

**Objetivo:** Completar el 4% restante de requisitos RFP  
**Estado Actual:** 96% ✅  
**Meta:** 100% ✅✅  
**Timeline:** 9 semanas (2.5 meses)  
**Fecha de Inicio:** 14 de Octubre de 2025  
**Fecha de Finalización:** 16 de Diciembre de 2025

---

## 📊 Resumen de Gaps

| Gap | Impacto | Esfuerzo | Prioridad | Estado |
|-----|---------|----------|-----------|--------|
| **Validación de terceros** | ALTO | 3 sem | P0 | ❌ Crítico |
| **Conectores enterprise** | ALTO | 4 sem | P0 | 🔶 Parcial |
| **Formatos adicionales** | MEDIO | 2 sem | P1 | 🔶 Pendiente |

**Total:** 9 semanas de trabajo estructurado

---

## 🚀 Sprint 6: Validación de Terceros (3 semanas)

**Objetivo:** Integrar validación automática con listas de sanciones, registros mercantiles y scoring ESG

### Semana 1: Integración OFAC y EU Sanctions (40h)

#### Tareas:

1. **Investigar y seleccionar APIs** (8h)
   - [ ] Evaluar OFAC Sanctions List API (Treasury.gov)
   - [ ] Evaluar EU Sanctions Database API
   - [ ] Evaluar World Bank Debarred Firms API
   - [ ] Seleccionar proveedor comercial (Dow Jones, Refinitiv, ComplyAdvantage)
   - [ ] Comparar costes y licencias

2. **Diseñar modelo de datos** (8h)
   - [ ] Crear tabla `sanctions_list` en PostgreSQL:
     ```sql
     CREATE TABLE sanctions_list (
         id UUID PRIMARY KEY,
         entity_name VARCHAR(500) NOT NULL,
         entity_type VARCHAR(50), -- PERSON, COMPANY, VESSEL
         source VARCHAR(100), -- OFAC, EU, UN
         list_name VARCHAR(200),
         sanction_type VARCHAR(100),
         countries TEXT[],
         programs TEXT[],
         effective_date DATE,
         expiry_date DATE,
         last_updated TIMESTAMP,
         raw_data JSONB
     );
     CREATE INDEX idx_sanctions_entity_name ON sanctions_list USING gin(to_tsvector('english', entity_name));
     ```
   - [ ] Crear tabla `validation_history`:
     ```sql
     CREATE TABLE validation_history (
         id UUID PRIMARY KEY,
         document_id UUID REFERENCES documents(id),
         entity_name VARCHAR(500),
         validation_date TIMESTAMP,
         is_sanctioned BOOLEAN,
         matched_entries JSONB,
         confidence_score FLOAT,
         validation_source VARCHAR(100)
     );
     ```

3. **Implementar servicio de validación** (16h)
   ```python
   # backend/services/sanctions_service.py
   from typing import List, Optional
   import httpx
   from fuzzywuzzy import fuzz
   
   class SanctionsService:
       def __init__(self):
           self.ofac_api_url = "https://sanctionslistapi.ofac.treas.gov/api/v1"
           self.eu_api_url = "https://webgate.ec.europa.eu/fsd/fsf"
           self.cache_ttl = 86400  # 24 horas
       
       async def check_entity(
           self,
           entity_name: str,
           entity_type: str = "PERSON",
           countries: Optional[List[str]] = None
       ) -> dict:
           """
           Validar entidad contra listas de sanciones
           """
           results = {
               "is_sanctioned": False,
               "matches": [],
               "confidence": 0.0,
               "sources_checked": []
           }
           
           # 1. Verificar OFAC
           ofac_matches = await self._check_ofac(entity_name, entity_type)
           results["sources_checked"].append("OFAC")
           
           # 2. Verificar EU Sanctions
           eu_matches = await self._check_eu_sanctions(entity_name, entity_type)
           results["sources_checked"].append("EU_SANCTIONS")
           
           # 3. Verificar World Bank
           wb_matches = await self._check_world_bank(entity_name)
           results["sources_checked"].append("WORLD_BANK")
           
           # 4. Consolidar resultados
           all_matches = ofac_matches + eu_matches + wb_matches
           
           if all_matches:
               results["is_sanctioned"] = True
               results["matches"] = all_matches
               results["confidence"] = max(m["score"] for m in all_matches)
           
           return results
       
       async def _check_ofac(self, name: str, entity_type: str) -> List[dict]:
           """Verificar contra OFAC Sanctions List"""
           async with httpx.AsyncClient() as client:
               response = await client.get(
                   f"{self.ofac_api_url}/search",
                   params={
                       "name": name,
                       "type": entity_type
                   },
                   headers={"Authorization": f"Bearer {OFAC_API_KEY}"}
               )
               
               if response.status_code == 200:
                   data = response.json()
                   matches = []
                   
                   for entry in data.get("results", []):
                       # Fuzzy matching para manejar variaciones
                       score = fuzz.token_sort_ratio(
                           name.lower(),
                           entry["name"].lower()
                       )
                       
                       if score > 85:  # Threshold 85%
                           matches.append({
                               "source": "OFAC",
                               "name": entry["name"],
                               "score": score / 100.0,
                               "list": entry["program"],
                               "details": entry
                           })
                   
                   return matches
               
               return []
       
       async def _check_eu_sanctions(self, name: str, entity_type: str) -> List[dict]:
           """Verificar contra EU Sanctions Database"""
           # Implementación similar a OFAC
           pass
       
       async def _check_world_bank(self, name: str) -> List[dict]:
           """Verificar contra World Bank Debarred Firms"""
           # Implementación similar
           pass
       
       async def validate_document_entities(self, document_id: UUID) -> dict:
           """
           Validar todas las entidades extraídas de un documento
           """
           # 1. Obtener entidades NER del documento
           entities = await self.ner_service.get_entities(document_id)
           
           # 2. Filtrar entidades relevantes (ORG, PERSON)
           relevant_entities = [
               e for e in entities
               if e["label"] in ["ORG", "PERSON", "GPE"]
           ]
           
           # 3. Validar cada entidad
           validation_results = []
           
           for entity in relevant_entities:
               result = await self.check_entity(
                   entity_name=entity["text"],
                   entity_type="COMPANY" if entity["label"] == "ORG" else "PERSON"
               )
               
               validation_results.append({
                   "entity": entity["text"],
                   "entity_type": entity["label"],
                   **result
               })
               
               # Guardar en historial
               await self._save_validation_history(
                   document_id=document_id,
                   entity_name=entity["text"],
                   result=result
               )
           
           # 4. Generar resumen
           is_high_risk = any(r["is_sanctioned"] for r in validation_results)
           
           return {
               "document_id": document_id,
               "is_high_risk": is_high_risk,
               "entities_checked": len(validation_results),
               "sanctioned_entities": [
                   r for r in validation_results if r["is_sanctioned"]
               ],
               "validation_results": validation_results
           }
   ```

4. **Crear endpoint API** (8h)
   ```python
   # backend/api/v1/validation.py
   from fastapi import APIRouter, HTTPException
   from uuid import UUID
   
   router = APIRouter(prefix="/validation", tags=["validation"])
   
   @router.post("/sanctions/check")
   async def check_sanctions(
       entity_name: str,
       entity_type: str = "PERSON"
   ):
       """Verificar entidad contra listas de sanciones"""
       service = SanctionsService()
       result = await service.check_entity(entity_name, entity_type)
       return result
   
   @router.post("/document/{document_id}/validate-entities")
   async def validate_document_entities(document_id: UUID):
       """Validar todas las entidades de un documento"""
       service = SanctionsService()
       result = await service.validate_document_entities(document_id)
       return result
   
   @router.get("/sanctions/history/{document_id}")
   async def get_validation_history(document_id: UUID):
       """Obtener historial de validaciones"""
       # Implementación
       pass
   ```

**Entregables Semana 1:**
- ✅ Servicio de validación OFAC
- ✅ Servicio de validación EU Sanctions
- ✅ Modelo de datos en PostgreSQL
- ✅ API REST endpoints
- ✅ Tests unitarios (10 tests)

---

### Semana 2: Registros Mercantiles y Scoring ESG (40h)

#### Tareas:

1. **Integración con InfoEmpresas/Informa** (16h)
   - [ ] Contratar API de InfoEmpresas o Informa D&B
   - [ ] Implementar servicio de consulta:
     ```python
     # backend/services/business_registry_service.py
     class BusinessRegistryService:
         async def check_company(self, cif: str, name: str) -> dict:
             """
             Verificar empresa en registro mercantil
             """
             # 1. Consultar API InfoEmpresas
             company_data = await self._query_infoempresa(cif)
             
             # 2. Extraer información relevante
             return {
                 "cif": cif,
                 "name": company_data["name"],
                 "is_active": company_data["status"] == "ACTIVE",
                 "incorporation_date": company_data["incorporation_date"],
                 "capital": company_data["capital"],
                 "legal_form": company_data["legal_form"],
                 "address": company_data["address"],
                 "administrators": company_data["administrators"],
                 "financial_indicators": {
                     "revenue": company_data["revenue"],
                     "employees": company_data["employees"],
                     "credit_score": company_data["credit_score"]
                 },
                 "risk_indicators": {
                     "has_debts": company_data["has_debts"],
                     "legal_proceedings": company_data["legal_proceedings"],
                     "bankruptcy_risk": company_data["bankruptcy_risk"]
                 }
             }
     ```

2. **Implementar Scoring ESG** (16h)
   - [ ] Integrar con API de scoring ESG (Refinitiv, MSCI, Sustainalytics)
   - [ ] Crear servicio ESG:
     ```python
     # backend/services/esg_service.py
     class ESGService:
         async def get_esg_score(self, company_name: str, ticker: Optional[str] = None) -> dict:
             """
             Obtener scoring ESG de empresa
             """
             # 1. Consultar API ESG (ej: Refinitiv)
             esg_data = await self._query_esg_api(company_name, ticker)
             
             # 2. Estructurar respuesta
             return {
                 "company": company_name,
                 "overall_score": esg_data["esg_score"],  # 0-100
                 "rating": esg_data["rating"],  # AAA, AA, A, BBB, BB, B, CCC
                 "environmental": {
                     "score": esg_data["environmental_score"],
                     "emissions": esg_data["emissions"],
                     "resource_usage": esg_data["resource_usage"]
                 },
                 "social": {
                     "score": esg_data["social_score"],
                     "labor_practices": esg_data["labor_practices"],
                     "human_rights": esg_data["human_rights"]
                 },
                 "governance": {
                     "score": esg_data["governance_score"],
                     "board_structure": esg_data["board_structure"],
                     "ethics": esg_data["ethics"]
                 },
                 "controversies": esg_data["controversies"],
                 "last_updated": esg_data["last_updated"]
             }
     ```

3. **Consolidar validación integral** (8h)
   - [ ] Crear servicio unificado:
     ```python
     # backend/services/third_party_validation_service.py
     class ThirdPartyValidationService:
         def __init__(self):
             self.sanctions = SanctionsService()
             self.registry = BusinessRegistryService()
             self.esg = ESGService()
         
         async def comprehensive_validation(self, document_id: UUID) -> dict:
             """
             Validación integral de terceros mencionados en documento
             """
             # 1. Extraer entidades del documento
             entities = await self.extract_entities(document_id)
             
             # 2. Validar cada entidad
             results = []
             
             for entity in entities:
                 validation = {
                     "entity_name": entity["text"],
                     "entity_type": entity["label"]
                 }
                 
                 # Sanciones
                 validation["sanctions"] = await self.sanctions.check_entity(
                     entity["text"], entity["label"]
                 )
                 
                 # Registro mercantil (solo para ORG)
                 if entity["label"] == "ORG":
                     validation["registry"] = await self.registry.check_company(
                         cif=entity.get("cif"),
                         name=entity["text"]
                     )
                     
                     # Scoring ESG
                     validation["esg"] = await self.esg.get_esg_score(
                         entity["text"]
                     )
                 
                 results.append(validation)
             
             # 3. Calcular riesgo global
             risk_level = self._calculate_risk_level(results)
             
             return {
                 "document_id": document_id,
                 "risk_level": risk_level,
                 "entities_validated": len(results),
                 "validations": results,
                 "summary": self._generate_summary(results)
             }
     ```

**Entregables Semana 2:**
- ✅ Integración InfoEmpresas/Informa
- ✅ Servicio de Scoring ESG
- ✅ Validación integral unificada
- ✅ Tests de integración (15 tests)

---

### Semana 3: Dashboard y Automatización (40h)

#### Tareas:

1. **Crear dashboard de validaciones** (16h)
   - [ ] Componente React para visualización:
     ```typescript
     // frontend/src/components/ThirdPartyValidationDashboard.tsx
     interface ValidationDashboardProps {
       documentId: string;
     }
     
     export const ThirdPartyValidationDashboard: React.FC<ValidationDashboardProps> = ({ documentId }) => {
       const [validations, setValidations] = useState<ValidationResult[]>([]);
       
       useEffect(() => {
         fetchValidations(documentId);
       }, [documentId]);
       
       return (
         <div className="validation-dashboard">
           <h2>Validación de Terceros</h2>
           
           {/* Resumen de riesgo */}
           <RiskSummaryCard validations={validations} />
           
           {/* Lista de entidades validadas */}
           <EntitiesTable entities={validations} />
           
           {/* Detalle de sanciones */}
           {validations.some(v => v.sanctions.is_sanctioned) && (
             <SanctionsAlert sanctionedEntities={getSanctionedEntities(validations)} />
           )}
           
           {/* Scoring ESG */}
           <ESGScoreChart esgScores={getESGScores(validations)} />
         </div>
       );
     };
     ```

2. **Automatizar validación en pipeline** (16h)
   - [ ] Integrar en flujo de procesamiento:
     ```python
     # backend/services/document_pipeline.py
     class DocumentPipeline:
         async def process_document(self, document_id: UUID):
             # ... pasos existentes ...
             
             # 7. Validación de terceros (NUEVO)
             validation_service = ThirdPartyValidationService()
             validation_result = await validation_service.comprehensive_validation(
                 document_id
             )
             
             # 8. Actualizar estado del documento
             if validation_result["risk_level"] == "HIGH":
                 await self.flag_for_manual_review(
                     document_id,
                     reason="Entidades sancionadas detectadas"
                 )
             
             # 9. Guardar resultados
             await self.save_validation_results(document_id, validation_result)
     ```

3. **Alertas y notificaciones** (8h)
   - [ ] Sistema de alertas para detecciones críticas
   - [ ] Email/Slack notification cuando se detecta entidad sancionada

**Entregables Semana 3:**
- ✅ Dashboard de validaciones
- ✅ Automatización en pipeline
- ✅ Sistema de alertas
- ✅ Documentación completa
- ✅ Tests end-to-end (20 tests)

**Total Tests Semana 1-3:** 45 tests adicionales

---

## 🔌 Sprint 7: Conectores Enterprise (4 semanas)

**Objetivo:** Implementar conectores para SharePoint, Alfresco y Exchange

### Semana 4: Conector SharePoint Online (40h)

#### Tareas:

1. **Setup autenticación Microsoft Graph** (8h)
   - [ ] Registrar app en Azure AD
   - [ ] Configurar permisos (Files.Read.All, Sites.Read.All)
   - [ ] Implementar OAuth2 flow
   - [ ] Almacenar tokens en Redis con refresh automático

2. **Implementar servicio SharePoint** (24h)
   ```python
   # backend/connectors/sharepoint_connector.py
   from office365.runtime.auth.authentication_context import AuthenticationContext
   from office365.sharepoint.client_context import ClientContext
   
   class SharePointConnector:
       def __init__(self):
           self.site_url = SHAREPOINT_SITE_URL
           self.client_id = SHAREPOINT_CLIENT_ID
           self.client_secret = SHAREPOINT_CLIENT_SECRET
       
       async def connect(self) -> ClientContext:
           """Establecer conexión con SharePoint"""
           auth_ctx = AuthenticationContext(self.site_url)
           auth_ctx.acquire_token_for_app(
               client_id=self.client_id,
               client_secret=self.client_secret
           )
           return ClientContext(self.site_url, auth_ctx)
       
       async def list_documents(
           self,
           folder_path: str = "Shared Documents",
           recursive: bool = True
       ) -> List[dict]:
           """Listar documentos en carpeta"""
           ctx = await self.connect()
           folder = ctx.web.get_folder_by_server_relative_url(folder_path)
           files = folder.files
           ctx.load(files)
           ctx.execute_query()
           
           documents = []
           for file in files:
               documents.append({
                   "name": file.properties["Name"],
                   "url": file.properties["ServerRelativeUrl"],
                   "size": file.properties["Length"],
                   "modified": file.properties["TimeLastModified"],
                   "author": file.properties["Author"]
               })
           
           return documents
       
       async def download_document(self, file_url: str, dest_path: str):
           """Descargar documento de SharePoint"""
           ctx = await self.connect()
           file = ctx.web.get_file_by_server_relative_url(file_url)
           
           with open(dest_path, 'wb') as local_file:
               file.download(local_file)
               ctx.execute_query()
       
       async def sync_folder(
           self,
           sharepoint_folder: str,
           local_folder: str,
           include_patterns: List[str] = ["*.pdf", "*.docx"],
           exclude_patterns: List[str] = []
       ):
           """Sincronizar carpeta de SharePoint"""
           documents = await self.list_documents(sharepoint_folder, recursive=True)
           
           for doc in documents:
               # Filtrar por patrones
               if not self._matches_patterns(doc["name"], include_patterns):
                   continue
               
               if self._matches_patterns(doc["name"], exclude_patterns):
                   continue
               
               # Descargar e ingestar
               local_path = f"{local_folder}/{doc['name']}"
               await self.download_document(doc["url"], local_path)
               
               # Ingestar en sistema
               await self.ingest_service.ingest_document(
                   file_path=local_path,
                   metadata={
                       "source": "SharePoint",
                       "original_url": doc["url"],
                       "modified_date": doc["modified"],
                       "author": doc["author"]
                   }
               )
   ```

3. **Scheduler de sincronización** (8h)
   ```python
   # backend/scheduler/sharepoint_sync_job.py
   from apscheduler.schedulers.asyncio import AsyncIOScheduler
   
   scheduler = AsyncIOScheduler()
   
   @scheduler.scheduled_job('cron', hour=2, minute=0)  # 2 AM diario
   async def sync_sharepoint_documents():
       """Job de sincronización diaria"""
       connector = SharePointConnector()
       
       # Carpetas a sincronizar (configurables)
       folders = [
           "Shared Documents/Contratos",
           "Shared Documents/Financiero",
           "Shared Documents/Legal"
       ]
       
       for folder in folders:
           try:
               await connector.sync_folder(
                   sharepoint_folder=folder,
                   local_folder="/tmp/sharepoint_sync"
               )
               logger.info(f"Sincronizada carpeta: {folder}")
           except Exception as e:
               logger.error(f"Error sincronizando {folder}: {e}")
   ```

**Entregables Semana 4:**
- ✅ Conector SharePoint Online
- ✅ Sincronización automática
- ✅ API endpoints
- ✅ Tests (15 tests)

---

### Semana 5: Conector Alfresco (40h)

#### Tareas:

1. **Implementar servicio Alfresco** (32h)
   ```python
   # backend/connectors/alfresco_connector.py
   import requests
   from requests.auth import HTTPBasicAuth
   
   class AlfrescoConnector:
       def __init__(self):
           self.base_url = ALFRESCO_BASE_URL
           self.username = ALFRESCO_USERNAME
           self.password = ALFRESCO_PASSWORD
           self.auth = HTTPBasicAuth(self.username, self.password)
       
       async def search_documents(
           self,
           query: str,
           max_results: int = 100
       ) -> List[dict]:
           """Buscar documentos en Alfresco"""
           url = f"{self.base_url}/api/-default-/public/search/versions/1/search"
           
           payload = {
               "query": {
                   "query": query,
                   "language": "afts"  # Alfresco Full Text Search
               },
               "paging": {
                   "maxItems": max_results
               }
           }
           
           response = requests.post(url, json=payload, auth=self.auth)
           response.raise_for_status()
           
           results = []
           for entry in response.json()["list"]["entries"]:
               node = entry["entry"]
               results.append({
                   "id": node["id"],
                   "name": node["name"],
                   "content_type": node["content"]["mimeType"],
                   "size": node["content"]["sizeInBytes"],
                   "created": node["createdAt"],
                   "modified": node["modifiedAt"],
                   "path": node["path"]["name"]
               })
           
           return results
       
       async def download_document(self, node_id: str, dest_path: str):
           """Descargar documento de Alfresco"""
           url = f"{self.base_url}/api/-default-/public/alfresco/versions/1/nodes/{node_id}/content"
           
           response = requests.get(url, auth=self.auth, stream=True)
           response.raise_for_status()
           
           with open(dest_path, 'wb') as f:
               for chunk in response.iter_content(chunk_size=8192):
                   f.write(chunk)
   ```

2. **Webhook listener para cambios** (8h)
   - Implementar endpoint para recibir notificaciones de Alfresco
   - Procesamiento automático de nuevos documentos

**Entregables Semana 5:**
- ✅ Conector Alfresco
- ✅ Webhook listener
- ✅ Tests (12 tests)

---

### Semana 6: Conector Exchange (40h)

#### Tareas:

1. **Implementar servicio Exchange** (32h)
   ```python
   # backend/connectors/exchange_connector.py
   from exchangelib import Credentials, Account, DELEGATE
   
   class ExchangeConnector:
       def __init__(self):
           credentials = Credentials(
               username=EXCHANGE_USERNAME,
               password=EXCHANGE_PASSWORD
           )
           self.account = Account(
               primary_smtp_address=EXCHANGE_EMAIL,
               credentials=credentials,
               autodiscover=True,
               access_type=DELEGATE
           )
       
       async def fetch_emails_with_attachments(
           self,
           folder: str = "inbox",
           days_back: int = 7
       ) -> List[dict]:
           """Obtener emails con adjuntos"""
           from datetime import datetime, timedelta
           
           start_date = datetime.now() - timedelta(days=days_back)
           
           emails = []
           for item in self.account.inbox.filter(datetime_received__gt=start_date):
               if item.attachments:
                   emails.append({
                       "subject": item.subject,
                       "from": item.sender.email_address,
                       "date": item.datetime_received,
                       "attachments": [
                           {
                               "name": att.name,
                               "size": att.size,
                               "content_type": att.content_type
                           }
                           for att in item.attachments
                       ]
                   })
           
           return emails
       
       async def download_attachments(self, email_id: str, dest_folder: str):
           """Descargar adjuntos de email"""
           # Implementación
           pass
   ```

2. **Procesamiento automático de adjuntos** (8h)
   - Scheduler para revisar buzón periódicamente
   - Filtrado por remitentes/asuntos configurables
   - Ingesta automática de adjuntos

**Entregables Semana 6:**
- ✅ Conector Exchange
- ✅ Procesamiento adjuntos
- ✅ Tests (10 tests)

---

### Semana 7: Unificación y UI (40h)

#### Tareas:

1. **Dashboard de conectores** (24h)
   - Panel de configuración de conectores
   - Estado de sincronizaciones
   - Logs de ingesta
   - Estadísticas por fuente

2. **API unificada de conectores** (16h)
   ```python
   # backend/api/v1/connectors.py
   @router.get("/connectors/status")
   async def get_connectors_status():
       """Estado de todos los conectores"""
       return {
           "sharepoint": await sharepoint_connector.get_status(),
           "alfresco": await alfresco_connector.get_status(),
           "exchange": await exchange_connector.get_status()
       }
   
   @router.post("/connectors/{connector_type}/sync")
   async def trigger_sync(connector_type: str):
       """Disparar sincronización manual"""
       # Implementación
       pass
   ```

**Entregables Semana 7:**
- ✅ Dashboard de conectores
- ✅ API unificada
- ✅ Documentación completa
- ✅ Tests end-to-end (15 tests)

**Total Tests Semana 4-7:** 52 tests adicionales

---

## 📄 Sprint 8: Formatos Adicionales (2 semanas)

**Objetivo:** Soporte para AFP, MP3, MP4

### Semana 8: Formatos AFP y Audio (40h)

#### Tareas:

1. **Parser AFP** (24h)
   ```python
   # backend/parsers/afp_parser.py
   import afplib  # Librería para parsear AFP
   
   class AFPParser:
       async def parse(self, file_path: str) -> dict:
           """Parsear archivo AFP"""
           with open(file_path, 'rb') as f:
               afp_data = afplib.parse(f.read())
           
           # Extraer texto y metadata
           text = afp_data.get_text()
           metadata = {
               "page_count": afp_data.page_count,
               "fonts": afp_data.fonts,
               "images": afp_data.images
           }
           
           return {
               "text": text,
               "metadata": metadata
           }
   ```

2. **Transcripción de audio (MP3)** (16h)
   ```python
   # backend/services/audio_transcription_service.py
   from openai import OpenAI
   
   class AudioTranscriptionService:
       def __init__(self):
           self.client = OpenAI(api_key=OPENAI_API_KEY)
       
       async def transcribe(self, audio_path: str) -> dict:
           """Transcribir audio con Whisper"""
           with open(audio_path, 'rb') as audio_file:
               transcript = self.client.audio.transcriptions.create(
                   model="whisper-1",
                   file=audio_file,
                   language="es",
                   response_format="verbose_json"
               )
           
           return {
               "text": transcript.text,
               "language": transcript.language,
               "duration": transcript.duration,
               "segments": transcript.segments
           }
   ```

**Entregables Semana 8:**
- ✅ Parser AFP
- ✅ Transcripción MP3
- ✅ Tests (15 tests)

---

### Semana 9: Formato Video (MP4) (40h)

#### Tareas:

1. **Extracción de audio de video** (16h)
   ```python
   # backend/services/video_processing_service.py
   import ffmpeg
   
   class VideoProcessingService:
       async def extract_audio(self, video_path: str) -> str:
           """Extraer audio de video"""
           audio_path = video_path.replace('.mp4', '.mp3')
           
           ffmpeg.input(video_path).output(
               audio_path,
               acodec='libmp3lame',
               audio_bitrate='192k'
           ).run()
           
           return audio_path
       
       async def extract_frames(self, video_path: str, fps: int = 1) -> List[str]:
           """Extraer frames del video"""
           # Para OCR de títulos/texto en video
           pass
   ```

2. **Pipeline completo de video** (24h)
   - Extracción de audio → Transcripción
   - Extracción de frames → OCR
   - Consolidación de texto
   - Generación de metadata (duración, resolución, etc.)

**Entregables Semana 9:**
- ✅ Procesamiento de video
- ✅ Pipeline completo
- ✅ Tests (12 tests)
- ✅ Documentación

**Total Tests Semana 8-9:** 27 tests adicionales

---

## 📊 Resumen del Roadmap

### Timeline Completo

```
Octubre 2025
├─ Sem 1 (14-20): Validación OFAC + EU Sanctions
├─ Sem 2 (21-27): Registros Mercantiles + ESG
└─ Sem 3 (28-3):  Dashboard + Automatización

Noviembre 2025
├─ Sem 4 (4-10):   Conector SharePoint
├─ Sem 5 (11-17):  Conector Alfresco
├─ Sem 6 (18-24):  Conector Exchange
└─ Sem 7 (25-1):   Unificación + UI

Diciembre 2025
├─ Sem 8 (2-8):    AFP + MP3
└─ Sem 9 (9-15):   MP4 + Finalización
```

**Fecha de Entrega:** 16 de Diciembre de 2025

---

### Esfuerzo Total

| Sprint | Semanas | Horas | Tests |
|--------|---------|-------|-------|
| **Sprint 6: Validación Terceros** | 3 | 120h | 45 |
| **Sprint 7: Conectores** | 4 | 160h | 52 |
| **Sprint 8: Formatos** | 2 | 80h | 27 |
| **TOTAL** | **9** | **360h** | **124** |

**Equivalente:** 2 desarrolladores full-time durante 9 semanas

---

### Entregables por Sprint

#### Sprint 6 (Validación Terceros):
- ✅ Servicio de validación OFAC
- ✅ Servicio de validación EU Sanctions
- ✅ Integración InfoEmpresas/Informa
- ✅ Scoring ESG
- ✅ Validación integral unificada
- ✅ Dashboard de validaciones
- ✅ Automatización en pipeline
- ✅ 45 tests

#### Sprint 7 (Conectores):
- ✅ Conector SharePoint Online
- ✅ Conector Alfresco
- ✅ Conector Exchange
- ✅ Dashboard de conectores
- ✅ API unificada
- ✅ Schedulers de sincronización
- ✅ 52 tests

#### Sprint 8 (Formatos):
- ✅ Parser AFP
- ✅ Transcripción MP3 (Whisper)
- ✅ Procesamiento MP4
- ✅ Pipeline completo multimedia
- ✅ 27 tests

---

## 🎯 Resultado Final

### Cobertura RFP Esperada: **100%** ✅✅✅

| Sección RFP | Antes | Después | Mejora |
|-------------|-------|---------|--------|
| Captura de Documentos | 95% | **100%** | +5% |
| Entendimiento Automatizado | 98% | **100%** | +2% |
| Búsqueda Avanzada | 100% | **100%** | - |
| RAG y Chatbots | 95% | **98%** | +3% |
| Evaluación de Riesgo | 98% | **100%** | +2% |
| **Validación y Compliance** | 90% | **100%** | +10% |
| **APIs e Integración** | 92% | **100%** | +8% |
| **TOTAL** | **96%** | **100%** | **+4%** |

---

## 💰 Costos Estimados

### Recursos Humanos
- 2 desarrolladores senior × 9 semanas × €800/semana = **€14,400**

### APIs y Servicios
- OFAC/EU Sanctions API: €500/mes
- InfoEmpresas/Informa: €300/mes
- ESG Data (Refinitiv): €800/mes
- SharePoint Online: Incluido en Microsoft 365
- Alfresco: Licencia existente
- OpenAI Whisper API: €0.006/min (estimado €100/mes)

**Total APIs (3 meses):** €5,100

### Infraestructura
- Storage adicional: €50/mes
- Compute adicional: €100/mes

**Total Infraestructura (3 meses):** €450

### **COSTO TOTAL:** €19,950

---

## 📝 Checklist de Implementación

### Antes de Empezar
- [ ] Contratar APIs necesarias (OFAC, InfoEmpresas, ESG)
- [ ] Configurar credenciales SharePoint/Alfresco/Exchange
- [ ] Provisionar recursos de infraestructura
- [ ] Asignar equipo de desarrollo (2 devs)
- [ ] Crear branch `feature/100-percent-rfp`

### Sprint 6 - Validación Terceros
- [ ] Semana 1: OFAC + EU Sanctions
- [ ] Semana 2: Registros Mercantiles + ESG
- [ ] Semana 3: Dashboard + Automatización
- [ ] Code review y merge

### Sprint 7 - Conectores
- [ ] Semana 4: SharePoint
- [ ] Semana 5: Alfresco
- [ ] Semana 6: Exchange
- [ ] Semana 7: Unificación
- [ ] Code review y merge

### Sprint 8 - Formatos
- [ ] Semana 8: AFP + MP3
- [ ] Semana 9: MP4
- [ ] Code review y merge
- [ ] **Merge a main** 🎉

### Post-Implementación
- [ ] Actualizar documentación
- [ ] Actualizar RFP_COVERAGE_STATUS.md → 100%
- [ ] Demo al cliente
- [ ] Training a usuarios
- [ ] Monitoreo en producción

---

## 🎉 Conclusión

Con este plan estructurado de **9 semanas** y un equipo de **2 desarrolladores**, alcanzaremos el **100% de cobertura RFP** el **16 de Diciembre de 2025**.

**Próximos Pasos Inmediatos:**
1. ✅ Aprobar roadmap
2. ✅ Contratar APIs necesarias
3. ✅ Asignar equipo
4. ✅ Iniciar Sprint 6 (Semana del 14 de Octubre)

**¡Let's go to 100%!** 🚀
