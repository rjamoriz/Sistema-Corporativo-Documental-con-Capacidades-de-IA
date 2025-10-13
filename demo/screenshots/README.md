# 📸 Screenshots de Demo

Esta carpeta contiene las capturas de pantalla de las funcionalidades clave del sistema.

## 📋 Screenshots Requeridos

### 1. Dashboard Principal (`01-dashboard.png`)
**Qué capturar:**
- Vista completa del dashboard con lista de documentos
- Filtros y búsqueda visible
- Panel de estadísticas (si existe)
- Usuario logueado visible en header

**Usuario:** `admin.demo`  
**URL:** `http://localhost:3000/dashboard`

---

### 2. Visor de Documentos (`02-document-viewer.png`)
**Qué capturar:**
- Documento PDF abierto con controles visibles
- Zoom, rotación, navegación de páginas
- Sidebar de thumbnails (si está abierto)
- Búsqueda de texto

**Usuario:** `admin.demo`  
**Documento:** Manual de Procedimientos Corporativos  
**URL:** `http://localhost:3000/documents/doc-001`

---

### 3. Sistema de Anotaciones (`03-annotations.png`)
**Qué capturar:**
- Documento con múltiples anotaciones visibles
- Toolbar de anotaciones con herramientas
- Sidebar con lista de anotaciones
- Al menos 1 highlight, 1 sticky note visible

**Usuario:** `revisor.demo`  
**Documento:** Política de Seguridad  
**URL:** `http://localhost:3000/documents/doc-002`

---

### 4. Comparación de Documentos (`04-comparison.png`)
**Qué capturar:**
- Vista split con dos documentos lado a lado
- Controles de sync scroll visibles
- Ambos documentos con contenido visible
- Panel de metadata (si está abierto)

**Usuario:** `admin.demo`  
**URL:** `http://localhost:3000/comparison`

---

### 5. GraphQL Playground (`05-graphql-playground.png`)
**Qué capturar:**
- GraphQL Playground con query de ejemplo
- Panel de documentación (DOCS) abierto
- Resultado de query visible

**URL:** `http://localhost:8000/api/graphql/`  
**Query sugerida:**
```graphql
query GetDocuments {
  documents(limit: 5) {
    id
    title
    version
    status
  }
}
```

---

### 6. Integración SharePoint (`06-sharepoint-integration.png`)
**Qué capturar:**
- Panel de integración con SharePoint
- Lista de documentos de SharePoint
- Estado de conexión visible (Connected)
- Botones de importar/sincronizar

**Usuario:** `admin.demo`  
**URL:** `http://localhost:3000/integrations/sharepoint`

---

### 7. Integración SAP DMS (`07-sap-integration.png`)
**Qué capturar:**
- Panel de integración con SAP DMS
- Formulario de búsqueda de documentos SAP
- Resultados de búsqueda (si hay)
- Estado de conexión visible

**Usuario:** `admin.demo`  
**URL:** `http://localhost:3000/integrations/sap-dms`

---

### 8. Anotaciones - Detalle (`08-annotation-detail.png`)
**Qué capturar:**
- Close-up de una anotación específica
- Tooltip o panel de edición visible
- Color picker (si está abierto)
- Información de creador y fecha

**Usuario:** `revisor.demo`

---

### 9. Búsqueda de Documentos (`09-search-results.png`)
**Qué capturar:**
- Campo de búsqueda con término ingresado
- Resultados de búsqueda listados
- Filtros aplicados
- Highlighting de términos en resultados

**Usuario:** `usuario.demo`

---

### 10. Metadata de Documento (`10-document-metadata.png`)
**Qué capturar:**
- Panel de metadata expandido
- Información completa: autor, fecha, versión, tags
- Historial de versiones (si existe)
- Permisos de documento

**Usuario:** `admin.demo`

---

## 🛠️ Herramientas Recomendadas

### macOS
```bash
# Screenshot de ventana completa
Cmd + Shift + 3

# Screenshot de selección
Cmd + Shift + 4

# Screenshot de ventana específica
Cmd + Shift + 4, luego Space
```

### Linux
```bash
# Screenshot con Gnome
gnome-screenshot

# Screenshot con selección
gnome-screenshot -a

# Screenshot con retraso (5 segundos)
gnome-screenshot -d 5
```

### Windows
```
# Screenshot de pantalla completa
Windows + Print Screen

# Screenshot con Snipping Tool
Windows + Shift + S
```

## 📐 Especificaciones

### Resolución
- **Mínimo:** 1920x1080 (Full HD)
- **Recomendado:** 2560x1440 (2K) o superior
- **Formato:** PNG (sin compresión)

### Composición
- Incluir toda la ventana del navegador (con URL visible)
- Evitar información personal real
- Usar datos de demo (usuarios: admin.demo, etc.)
- Mantener UI limpia (cerrar notificaciones innecesarias)

### Naming Convention
```
[número]-[descripción]-[versión].png

Ejemplos:
01-dashboard-v1.png
02-document-viewer-v2.png
03-annotations-final.png
```

## 📝 Checklist de Screenshots

- [ ] 01-dashboard.png
- [ ] 02-document-viewer.png
- [ ] 03-annotations.png
- [ ] 04-comparison.png
- [ ] 05-graphql-playground.png
- [ ] 06-sharepoint-integration.png
- [ ] 07-sap-integration.png
- [ ] 08-annotation-detail.png
- [ ] 09-search-results.png
- [ ] 10-document-metadata.png

## 💡 Tips para Screenshots de Calidad

1. **Zoom del navegador:** Mantener al 100% (Ctrl+0 / Cmd+0)
2. **Ocultar extensiones:** Modo incógnito o perfil limpio
3. **Tema:** Usar tema claro (mejor para presentaciones)
4. **Datos realistas:** Usar documentos y anotaciones de muestra
5. **Timing:** Capturar cuando todo esté cargado (no spinners)
6. **Consistencia:** Mismo navegador y tamaño para todos

---

## 🎨 Post-Procesamiento (Opcional)

Si deseas agregar anotaciones a los screenshots:

```bash
# Instalar ImageMagick (Linux/macOS)
sudo apt install imagemagick  # Linux
brew install imagemagick       # macOS

# Agregar texto
convert input.png \
  -pointsize 24 \
  -fill red \
  -annotate +100+100 "Feature Key" \
  output.png

# Agregar flecha/círculo (usar GIMP o similar)
```

---

**Última actualización:** Octubre 10, 2025  
**Estado:** Plantilla lista - Screenshots pendientes de captura
