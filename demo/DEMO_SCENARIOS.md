# 🎯 Escenarios de Demostración Detallados

Este documento describe los escenarios específicos para demostrar las capacidades del Sistema Documental Corporativo con IA.

## 📋 Índice de Escenarios

1. [Gestión Documental Básica](#escenario-1-gestión-documental-básica) (5 min)
2. [Sistema de Anotaciones Avanzado](#escenario-2-sistema-de-anotaciones-avanzado) (5 min)
3. [Comparación de Documentos](#escenario-3-comparación-de-documentos) (5 min)
4. [Integración con SharePoint](#escenario-4-integración-con-sharepoint) (3 min)
5. [Integración con SAP DMS](#escenario-5-integración-con-sap-dms) (3 min)
6. [API GraphQL](#escenario-6-api-graphql) (2 min)
7. [Flujo de Trabajo Completo](#escenario-7-flujo-de-trabajo-completo) (7 min)

---

## Escenario 1: Gestión Documental Básica

**Duración:** 5 minutos  
**Usuario:** `admin.demo` / `Demo2025!`  
**Objetivo:** Demostrar funcionalidades básicas del visor de documentos

### Pasos

1. **Login** (30 seg)
   ```
   - Navegar a http://localhost:3000
   - Usuario: admin.demo
   - Password: Demo2025!
   - Click en "Iniciar Sesión"
   ```
   
   **Puntos a destacar:**
   - Autenticación segura con JWT
   - Interfaz limpia y profesional

2. **Dashboard de Documentos** (1 min)
   ```
   - Observar lista de documentos disponibles
   - Mostrar filtros por categoría
   - Demostrar búsqueda por título
   - Mostrar vista de tarjetas vs lista
   ```
   
   **Puntos a destacar:**
   - 5 documentos de ejemplo pre-cargados
   - Metadata visible (tamaño, fecha, versión)
   - Estados de documentos (Aprobado, Borrador, En Revisión)

3. **Abrir Documento** (30 seg)
   ```
   - Click en "Manual de Procedimientos Corporativos"
   - Esperar carga del visor PDF
   ```
   
   **Puntos a destacar:**
   - Carga rápida (<2 segundos)
   - Rendering de alta calidad con react-pdf

4. **Navegación Básica** (1 min)
   ```
   - Usar controles de página (anterior/siguiente)
   - Saltar a página específica (página 45)
   - Probar atajos de teclado:
     * Arrow Up/Down: Página anterior/siguiente
     * Home/End: Primera/última página
   ```
   
   **Puntos a destacar:**
   - Navegación fluida y responsive
   - Keyboard shortcuts para productividad

5. **Funciones de Zoom** (1 min)
   ```
   - Probar niveles de zoom: 50%, 75%, 100%, 125%, 150%, 200%
   - Usar "Fit to Width" (ajustar a ancho)
   - Zoom con Ctrl + Scroll (mouse wheel)
   ```
   
   **Puntos a destacar:**
   - 6 niveles de zoom predefinidos
   - Modo "Fit to Width" inteligente
   - Zoom suave sin lag

6. **Rotación** (30 seg)
   ```
   - Click en botón de rotación
   - Rotar 90° → 180° → 270° → 0°
   ```
   
   **Puntos a destacar:**
   - Útil para documentos escaneados
   - Rotación instantánea

7. **Thumbnails** (30 seg)
   ```
   - Toggle sidebar de thumbnails (ON/OFF)
   - Click en thumbnail para saltar a página
   - Scroll por thumbnails
   ```
   
   **Puntos a destacar:**
   - Vista previa visual de todas las páginas
   - Navegación rápida a cualquier sección

8. **Búsqueda en Documento** (1 min)
   ```
   - Click en campo de búsqueda
   - Buscar: "procedimiento"
   - Observar resultados destacados
   - Navegar entre coincidencias
   ```
   
   **Puntos a destacar:**
   - Búsqueda de texto completo (full-text search)
   - Highlighting de resultados
   - Navegación entre coincidencias

9. **Descargar/Imprimir** (30 seg)
   ```
   - Click en botón de descarga
   - Click en botón de impresión
   ```
   
   **Puntos a destacar:**
   - Descarga del PDF original
   - Diálogo de impresión nativo del navegador

### KPIs de Éxito
- ✅ Documento carga en < 2 segundos
- ✅ Zoom y rotación sin lag perceptible
- ✅ Búsqueda encuentra resultados en < 500ms
- ✅ Thumbnails renderizan en < 3 segundos

---

## Escenario 2: Sistema de Anotaciones Avanzado

**Duración:** 5 minutos  
**Usuario:** `revisor.demo` / `Demo2025!`  
**Objetivo:** Demostrar capacidades de anotación colaborativa

### Pasos

1. **Cambio de Usuario** (30 seg)
   ```
   - Logout de admin.demo
   - Login como revisor.demo / Demo2025!
   ```
   
   **Puntos a destacar:**
   - Diferentes usuarios tienen diferentes permisos
   - María Revisor tiene rol de REVIEWER

2. **Abrir Documento con Anotaciones** (30 seg)
   ```
   - Abrir "Política de Seguridad de la Información"
   - Observar anotaciones existentes en el documento
   ```
   
   **Puntos a destacar:**
   - Anotaciones visibles sobre el PDF
   - Canvas overlay transparente

3. **Crear Highlight** (1 min)
   ```
   - Click en herramienta "Highlight" (amarillo)
   - Seleccionar color (amarillo, verde, azul, púrpura)
   - Hacer drag sobre texto en página 8
   - Agregar comentario: "Punto importante - revisar con CISO"
   - Guardar anotación
   ```
   
   **Puntos a destacar:**
   - 6 colores disponibles para destacar
   - Comentarios contextuales
   - Guardado instantáneo via GraphQL

4. **Crear Sticky Note** (1 min)
   ```
   - Click en herramienta "Sticky Note" (naranja)
   - Click en posición en página 15
   - Escribir: "⚠️ URGENTE: Actualizar controles ISO 27001:2022"
   - Guardar
   ```
   
   **Puntos a destacar:**
   - Notas tipo "post-it" digitales
   - Posicionamiento libre en la página
   - Uso de emojis soportado

5. **Crear Redaction** (1 min)
   ```
   - Click en herramienta "Redaction" (negro)
   - Hacer drag sobre información sensible (página 3)
   - Confirmar redacción
   ```
   
   **Puntos a destacar:**
   - Oculta información confidencial
   - Útil para compartir versiones censuradas
   - Color negro sólido

6. **Sidebar de Anotaciones** (30 seg)
   ```
   - Observar panel lateral con lista de anotaciones
   - Click en anotación para navegar a ella
   - Ver estadísticas: 3 highlights, 2 sticky notes, 1 redaction
   ```
   
   **Puntos a destacar:**
   - Lista organizada por tipo y página
   - Navegación rápida a cualquier anotación
   - Stats en tiempo real

7. **Editar/Eliminar Anotación** (1 min)
   ```
   - Click en herramienta "Select"
   - Click en anotación existente
   - Editar comentario
   - Guardar cambios
   - Seleccionar otra anotación
   - Click en "Eliminar"
   - Confirmar eliminación
   ```
   
   **Puntos a destacar:**
   - CRUD completo de anotaciones
   - Confirmación antes de eliminar
   - Actualización instantánea

8. **Keyboard Shortcuts** (30 seg)
   ```
   - Presionar "H" → activa Highlight
   - Presionar "N" → activa Sticky Note
   - Presionar "R" → activa Redaction
   - Presionar "Esc" → cancela modo drawing
   ```
   
   **Puntos a destacar:**
   - Atajos de teclado para productividad
   - Modo power-user

### KPIs de Éxito
- ✅ Crear anotación < 3 segundos (incluye guardado GraphQL)
- ✅ Rendering Canvas a 60 FPS (sin lag al dibujar)
- ✅ Edición de anotación sin reload de página
- ✅ Lista de anotaciones actualizada en tiempo real

---

## Escenario 3: Comparación de Documentos

**Duración:** 5 minutos  
**Usuario:** `admin.demo` / `Demo2025!`  
**Objetivo:** Demostrar comparación side-by-side de versiones

### Pasos

1. **Acceder a Comparación** (30 seg)
   ```
   - Login como admin.demo
   - Navegar a "Comparar Documentos" en menú
   - O acceder a /comparison
   ```

2. **Cargar Documentos** (1 min)
   ```
   - Panel de configuración visible
   - Document 1 (Original):
     * Título: "Contrato XYZ - v1.0"
     * URL: /storage/demo/contrato_xyz_2025_v1.pdf
   - Document 2 (Modificado):
     * Título: "Contrato XYZ - v1.2"
     * URL: /storage/demo/contrato_xyz_2025_v1.2.pdf
   - Click en "Cargar y Comparar"
   ```
   
   **Puntos a destacar:**
   - Soporte para URLs y archivos locales
   - Validación de formatos (solo PDF)

3. **Vista Split** (1 min)
   ```
   - Observar vista dividida (50/50)
   - Documento original a la izquierda (borde azul)
   - Documento modificado a la derecha (borde verde)
   - Ambos documentos cargados simultáneamente
   ```
   
   **Puntos a destacar:**
   - Layout responsive y adaptable
   - Códigos de color intuitivos
   - Rendering paralelo eficiente

4. **Scroll Sincronizado** (1 min 30 seg)
   ```
   - Toggle "Sync Scroll" = ON (por defecto)
   - Hacer scroll en documento izquierdo
   - Observar scroll automático en documento derecho
   - Ambos documentos permanecen alineados
   - Probar scroll rápido y lento
   ```
   
   **Puntos a destacar:**
   - Sincronización fluida con throttling (100ms)
   - Refs de React para performance óptima
   - Sin lag perceptible

5. **Desactivar Sync** (30 seg)
   ```
   - Toggle "Sync Scroll" = OFF
   - Hacer scroll en documento izquierdo → derecho no se mueve
   - Hacer scroll en documento derecho → izquierdo no se mueve
   - Navegación independiente
   ```
   
   **Puntos a destacar:**
   - Flexibilidad para análisis detallado
   - Control fino sobre navegación

6. **Controles Unificados** (1 min)
   ```
   - Usar controles de página centrales
   - Cambiar página → ambos documentos cambian
   - Usar zoom unificado (5 niveles: 50%-150%)
   - Ambos documentos mantienen mismo zoom
   ```
   
   **Puntos a destacar:**
   - Controles centralizados para eficiencia
   - Estado sincronizado entre documentos

7. **Metadata de Versiones** (30 seg)
   ```
   - Click en "Version Metadata" (toggle panel)
   - Observar información de ambos documentos:
     * Versión: 1.0 vs 1.2
     * Fecha: 2024-12-15 vs 2025-01-10
     * Autor: Depto Legal
     * Páginas: 23 vs 23
   - Collapse panel
   ```
   
   **Puntos a destacar:**
   - Información contextual importante
   - Ayuda a entender diferencias

8. **Análisis de Diferencias** (placeholder) (30 seg)
   ```
   - Click en "Analyze Differences"
   - Ver resumen:
     * Pages changed: 5
     * Text differences: 127
     * Structural changes: 3
   ```
   
   **Puntos a destacar:**
   - Feature en desarrollo (placeholder)
   - Futuro: diff algorithm avanzado
   - Útil para auditorías y compliance

### KPIs de Éxito
- ✅ Ambos documentos cargan en < 3 segundos
- ✅ Scroll sync latencia < 50ms
- ✅ Zoom simultáneo sin stuttering
- ✅ Manejo de documentos con diferente número de páginas

---

## Escenario 4: Integración con SharePoint

**Duración:** 3 minutos  
**Usuario:** `admin.demo` / `Demo2025!`  
**Objetivo:** Demostrar integración nativa con SharePoint Online

### Pasos

1. **Acceder a Conectores** (30 seg)
   ```
   - Login como admin.demo
   - Navegar a "Integraciones" → "SharePoint"
   - Observar estado de conexión
   ```

2. **Configuración** (30 seg)
   ```
   - Ver configuración actual:
     * Site URL: https://demo.sharepoint.com/sites/Documents
     * Status: ✅ Connected
     * Last sync: 2 minutos ago
   - Mostrar permisos de aplicación Azure AD
   ```
   
   **Puntos a destacar:**
   - OAuth2 con Azure AD (autenticación segura)
   - Permisos granulares (Files.Read.All, Sites.Read.All)

3. **Listar Documentos** (1 min)
   ```
   - Click en "Ver Documentos de SharePoint"
   - Observar lista de archivos de biblioteca compartida:
     * Reporte Mensual.pdf
     * Política Vacaciones.docx
     * Presupuesto 2025.xlsx
   - Filtrar por tipo de archivo (solo PDFs)
   ```
   
   **Puntos a destacar:**
   - Listado en tiempo real desde SharePoint
   - Metadata de SharePoint preservada
   - Filtros y búsqueda

4. **Importar Documento** (1 min)
   ```
   - Seleccionar "Reporte Mensual.pdf"
   - Click en "Importar al Sistema"
   - Esperar confirmación
   - Ver documento importado en dashboard local
   ```
   
   **Puntos a destacar:**
   - Importación seamless
   - Metadata se transfiere automáticamente
   - Documento ahora disponible para anotaciones

5. **Sincronización Bidireccional** (30 seg)
   ```
   - Mostrar configuración de sync:
     * Auto-sync: Enabled
     * Frequency: Every 30 minutes
     * Last sync: 3 minutos ago
   - Explicar que cambios en SharePoint se reflejan automáticamente
   ```
   
   **Puntos a destacar:**
   - Sync automático programado
   - Evita duplicación de trabajo
   - Single source of truth

### Puntos Clave a Mencionar
- ✅ OAuth2 seguro (no almacena contraseñas)
- ✅ Soporte para SharePoint Online y On-Premises
- ✅ Sync bidireccional opcional
- ✅ Preserva permisos y metadata de SharePoint

---

## Escenario 5: Integración con SAP DMS

**Duración:** 3 minutos  
**Usuario:** `admin.demo` / `Demo2025!`  
**Objetivo:** Demostrar integración con SAP Document Management System

### Pasos

1. **Acceder a Conector SAP** (30 seg)
   ```
   - Navegar a "Integraciones" → "SAP DMS"
   - Observar estado de conexión:
     * SAP Host: demo-sap.example.com
     * System: PRD (00)
     * Status: ✅ Connected
   ```

2. **Búsqueda por Número SAP** (1 min)
   ```
   - Click en "Buscar Documento SAP"
   - Ingresar número: DOC-2025-00123
   - Click "Buscar"
   - Ver resultados:
     * Documento: Especificación Técnica XYZ
     * SAP Document Type: DRW (Drawing)
     * Version: 03
     * Status: Released
   ```
   
   **Puntos a destacar:**
   - Integración vía RFC (Remote Function Call)
   - BAPIs estándar SAP (CREATE2, GETDETAIL2, etc.)
   - Búsqueda por múltiples criterios

3. **Descargar desde SAP** (1 min)
   ```
   - Click en documento encontrado
   - Click "Descargar desde SAP"
   - Esperar descarga (vía CHECKOUTVIEW2 BAPI)
   - Documento descargado y abierto en visor local
   ```
   
   **Puntos a destacar:**
   - Descarga directa desde SAP content server
   - Mantiene versionamiento SAP
   - Formato original preservado

4. **Crear Documento en SAP** (demo conceptual) (30 seg)
   ```
   - Click "Crear Nuevo en SAP"
   - Ver formulario:
     * Document Type: DRW, SPE, TXT, etc.
     * Document Number: Auto-generado o manual
     * Description: [texto libre]
     * File: Seleccionar archivo local
   - Explicar que se crearía en SAP al submit
   ```
   
   **Puntos a destacar:**
   - Creación bidireccional
   - Tipos de documento configurables
   - Workflow SAP respetado

5. **Metadata SAP** (30 seg)
   ```
   - Mostrar metadata sincronizada:
     * SAP Document Number
     * SAP Version
     * SAP Status (In Work, Released, etc.)
     * Change Number
     * Valid From / Valid To
   - Explicar que metadata se actualiza automáticamente
   ```

### Puntos Clave a Mencionar
- ✅ RFC/BAPI nativo (no screen scraping)
- ✅ Soporte para SAP ERP y S/4HANA
- ✅ Versionamiento sincronizado
- ✅ Workflow SAP integrado

---

## Escenario 6: API GraphQL

**Duración:** 2 minutos  
**Usuario:** Técnico / Desarrollador  
**Objetivo:** Demostrar API GraphQL flexible y potente

### Pasos

1. **Abrir GraphQL Playground** (30 seg)
   ```
   - Navegar a http://localhost:8000/api/graphql/
   - Observar interfaz GraphQL Playground
   - Mostrar schema documentation (panel derecho)
   ```
   
   **Puntos a destacar:**
   - API moderna basada en Strawberry
   - Introspección completa del schema
   - Documentación auto-generada

2. **Query: Listar Documentos** (30 seg)
   ```graphql
   query GetDocuments {
     documents(limit: 5) {
       id
       title
       filename
       version
       status
       createdAt
       metadata {
         author
         pageCount
         confidentiality
       }
     }
   }
   ```
   
   **Puntos a destacar:**
   - Solo solicitas los campos que necesitas
   - Evita over-fetching
   - Respuesta JSON estructurada

3. **Query: Documento con Anotaciones** (30 seg)
   ```graphql
   query GetDocumentWithAnnotations {
     document(id: "doc-001") {
       title
       annotations {
         id
         type
         color
         content
         pageNumber
         createdBy {
           username
           fullName
         }
       }
     }
   }
   ```
   
   **Puntos a destacar:**
   - Consultas anidadas (nested queries)
   - Relaciones entre entidades
   - Una sola request = múltiples recursos

4. **Mutation: Crear Anotación** (30 seg)
   ```graphql
   mutation CreateAnnotation {
     createAnnotation(input: {
       documentId: "doc-001"
       pageNumber: 10
       type: HIGHLIGHT
       color: YELLOW
       position: { x: 100, y: 200, width: 300, height: 20 }
       content: "Importante para revisión"
     }) {
       id
       type
       color
       content
       createdAt
     }
   }
   ```
   
   **Puntos a destacar:**
   - Mutations para modificar datos
   - Input validation automática
   - Respuesta inmediata con datos creados

5. **Introspección del Schema** (30 seg)
   ```
   - Click en "DOCS" en Playground
   - Explorar tipos disponibles:
     * Document
     * Annotation
     * User
     * DocumentMetadata
   - Mostrar fields y relaciones
   ```
   
   **Puntos a destacar:**
   - Self-documenting API
   - Explora schema sin documentación externa
   - Autocomplete en queries

### Puntos Clave a Mencionar
- ✅ GraphQL > REST para aplicaciones complejas
- ✅ Flexibility: clientes deciden qué datos necesitan
- ✅ Single endpoint: /api/graphql/
- ✅ Type-safe con Strawberry + TypeScript frontend

---

## Escenario 7: Flujo de Trabajo Completo

**Duración:** 7 minutos  
**Usuario:** Múltiples usuarios  
**Objetivo:** Demostrar un flujo end-to-end realista

### Historia

**Contexto:** María (revisor.demo) necesita revisar el "Plan Estratégico 2025-2027" que está en borrador, agregar sus comentarios, y enviar para aprobación final al administrador.

### Pasos

1. **María: Login y Asignación** (1 min)
   ```
   - Login como revisor.demo
   - Dashboard muestra: "Tienes 1 documento pendiente de revisión"
   - Click en "Plan Estratégico 2025-2027"
   - Status: IN_REVIEW
   - Ver metadata:
     * Última modificación: Hace 2 días
     * Modificado por: Dirección General
     * Versión: 2.1
   ```

2. **María: Revisión y Anotaciones** (2 min)
   ```
   - Navegar a página 10 (Objetivos Estratégicos)
   - Crear highlight verde: "Objetivo clave bien definido"
   - Página 25: Crear sticky note naranja:
     "📊 KPI: Verificar que sea medible y alcanzable"
   - Página 50: Crear highlight amarillo: "Inversión en IA - alinear con presupuesto"
   - Página 78: Crear redaction: [información confidencial sobre adquisición]
   ```
   
   **Puntos a destacar:**
   - Múltiples tipos de anotaciones
   - Comentarios constructivos
   - Redacción de información sensible

3. **María: Aprobar Secciones** (1 min)
   ```
   - Sidebar de anotaciones muestra resumen:
     * 2 highlights verdes (aprobado)
     * 1 sticky note naranja (requiere acción)
     * 1 highlight amarillo (comentario)
     * 1 redaction
   - Click en "Enviar para Aprobación Final"
   - Agregar nota: "Documento revisado. Listo para aprobación con comentarios menores."
   - Confirmar envío
   - Status cambia a: PENDING_APPROVAL
   ```

4. **Admin: Recibir Notificación** (30 seg)
   ```
   - Logout de revisor.demo
   - Login como admin.demo
   - Notificación en dashboard:
     "Plan Estratégico 2025-2027 requiere tu aprobación"
   - Click en notificación
   ```

5. **Admin: Revisar Comentarios** (1 min 30 seg)
   ```
   - Documento abierto con todas las anotaciones de María
   - Revisar cada anotación:
     * Click en sidebar para navegar a cada una
     * Leer comentarios
     * Verificar redacción en página 78
   - Comparar con versión anterior (2.0):
     * Click "Comparar con v2.0"
     * Ver cambios side-by-side
     * Verificar mejoras realizadas
   ```

6. **Admin: Aprobar Documento** (1 min)
   ```
   - Click "Aprobar Documento"
   - Dialog de confirmación:
     * Marcar como versión final: ✓
     * Publicar en SharePoint: ✓
     * Notificar stakeholders: ✓
   - Click "Confirmar Aprobación"
   - Status cambia a: APPROVED
   - Versión actualizada a: 2.2 (final)
   ```

7. **Admin: Publicación Automática** (30 seg)
   ```
   - Sistema muestra progreso:
     ✓ Documento aprobado
     ✓ Generando PDF final con watermark
     ✓ Subiendo a SharePoint: /Approved/PlanEstrategico_2025-2027_v2.2.pdf
     ✓ Notificaciones enviadas a: 12 usuarios
   - Confirmación final: "Documento publicado exitosamente"
   ```

### Resultado Final
- ✅ Documento revisado colaborativamente
- ✅ Comentarios capturados y resueltos
- ✅ Versiones comparadas
- ✅ Información sensible redactada
- ✅ Aprobado y publicado automáticamente
- ✅ Integración con SharePoint completada

---

## 📊 Resumen de Capacidades Demostradas

| Capacidad | Escenarios | Tiempo | Impacto |
|-----------|-----------|--------|---------|
| Visor PDF Avanzado | 1 | 5 min | Alto |
| Sistema de Anotaciones | 2, 7 | 12 min | Muy Alto |
| Comparación de Documentos | 3, 7 | 6 min | Alto |
| Integración SharePoint | 4, 7 | 4 min | Medio |
| Integración SAP DMS | 5 | 3 min | Medio |
| API GraphQL | 6 | 2 min | Alto (Devs) |
| Workflow Completo | 7 | 7 min | Muy Alto |

## 🎯 Métricas de Éxito de la Demo

### Performance
- ✅ Carga de documentos: < 2 segundos
- ✅ Rendering de anotaciones: 60 FPS
- ✅ Scroll sincronizado: < 50ms latencia
- ✅ API response time: < 200ms

### Funcionalidad
- ✅ 100% de features core demostradas
- ✅ 0 errores durante demo
- ✅ Flujo de trabajo end-to-end completado
- ✅ Integraciones verificadas funcionando

### UX
- ✅ Interfaz intuitiva (no requiere capacitación previa)
- ✅ Navegación fluida y responsive
- ✅ Feedback visual inmediato en todas las acciones
- ✅ Keyboard shortcuts para power users

## 📝 Notas Finales

### Preparación Pre-Demo
1. Ejecutar seed de datos: `python demo/scripts/seed_demo_data.py`
2. Generar PDFs: `python demo/scripts/generate_sample_pdfs.py`
3. Verificar servicios corriendo:
   - Backend: http://localhost:8000/health
   - Frontend: http://localhost:3000
   - GraphQL: http://localhost:8000/api/graphql/

### Durante la Demo
- Mantener ritmo dinámico pero no apresurado
- Pausar para preguntas después de cada escenario
- Destacar diferenciadores vs competencia
- Enfatizar 100% RFP Coverage y production-ready

### Después de la Demo
- Distribuir documentación (DEMO_SCRIPT.md, API_REFERENCE.md)
- Proveer acceso a demo environment para pruebas
- Agendar sesión de Q&A técnica con equipo IT
- Solicitar feedback estructurado

---

**Versión:** 1.0  
**Última actualización:** Octubre 10, 2025  
**100% RFP Coverage Achieved** 🎯
