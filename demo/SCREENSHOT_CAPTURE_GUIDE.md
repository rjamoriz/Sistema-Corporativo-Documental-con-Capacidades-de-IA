# 📸 Guía Rápida para Capturar Screenshots

## 🎯 Objetivo
Capturar 10 screenshots profesionales de las funcionalidades clave del sistema para usar en presentaciones y documentación.

---

## ⚡ Pre-requisitos

### 1. Servicios Corriendo
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend
npm run dev

# Verificar que todo esté corriendo:
# ✓ Backend: http://localhost:8000/health
# ✓ Frontend: http://localhost:3000
# ✓ GraphQL: http://localhost:8000/api/graphql/
```

### 2. Datos de Demo Cargados
```bash
# Si aún no has ejecutado seed
python demo/scripts/seed_demo_data.py
```

### 3. Navegador Preparado
- Usar Chrome o Firefox en modo normal (no incógnito para esta demo)
- Zoom al 100% (Ctrl+0 / Cmd+0)
- Cerrar pestañas innecesarias
- Ocultar extensiones visibles

---

## 📸 Screenshots Requeridos

### Screenshot 1: Dashboard Principal
**Archivo:** `demo/screenshots/01-dashboard.png`

**Pasos:**
1. Login como `admin.demo` / `Demo2025!`
2. Navegar a dashboard principal
3. Asegurar que se vean:
   - Lista de documentos (5 documentos)
   - Filtros y búsqueda
   - Header con usuario logueado
   - Estadísticas (si existen)

**Comando para captura:**
```bash
# Linux con gnome-screenshot
gnome-screenshot -w -f demo/screenshots/01-dashboard.png

# macOS
# Cmd + Shift + 4, luego Space, click en ventana
```

---

### Screenshot 2: Visor de Documentos
**Archivo:** `demo/screenshots/02-document-viewer.png`

**Pasos:**
1. Mismo usuario (admin.demo)
2. Abrir "Manual de Procedimientos Corporativos"
3. Asegurar que se vean:
   - PDF renderizado claramente
   - Controles de navegación (página, zoom, rotación)
   - Thumbnails sidebar (abierto)
   - Campo de búsqueda

**Tip:** Navegar a página 5 para mejor composición visual

---

### Screenshot 3: Sistema de Anotaciones
**Archivo:** `demo/screenshots/03-annotations.png`

**Pasos:**
1. Logout y login como `revisor.demo` / `Demo2025!`
2. Abrir "Política de Seguridad de la Información"
3. Si hay anotaciones pre-creadas, mostrarlas
4. Si no, crear al menos:
   - 1 highlight amarillo
   - 1 sticky note naranja
5. Asegurar que se vea:
   - Documento con anotaciones visibles
   - Toolbar de anotaciones
   - Sidebar con lista de anotaciones
   - Selector de colores

---

### Screenshot 4: Comparación de Documentos
**Archivo:** `demo/screenshots/04-comparison.png`

**Pasos:**
1. Login como `admin.demo`
2. Navegar a página de comparación
3. Cargar dos documentos (o usar URLs de ejemplo)
4. Asegurar que se vea:
   - Vista split 50/50
   - Ambos documentos con contenido visible
   - Controles de sync scroll
   - Panel de metadata (si está abierto)

**Nota:** Si no tienes dos versiones, captura el layout con documentos de placeholder

---

### Screenshot 5: GraphQL Playground
**Archivo:** `demo/screenshots/05-graphql-playground.png`

**Pasos:**
1. Navegar a http://localhost:8000/api/graphql/
2. En el editor, pegar esta query:
```graphql
query GetDocuments {
  documents(limit: 5) {
    id
    title
    version
    status
    createdAt
  }
}
```
3. Click "Execute" para ver resultados
4. Abrir panel de DOCS (botón verde)
5. Capturar con query + resultado + docs visibles

---

### Screenshot 6: Integración SharePoint (Opcional)
**Archivo:** `demo/screenshots/06-sharepoint-integration.png`

**Pasos:**
1. Login como `admin.demo`
2. Navegar a sección de integraciones > SharePoint
3. Asegurar que se vea:
   - Estado de conexión
   - Panel de configuración
   - Lista de documentos (si está implementado)

**Nota:** Si esta feature no está implementada en frontend, puedes crear una captura de diseño/mockup

---

### Screenshot 7: Integración SAP DMS (Opcional)
**Archivo:** `demo/screenshots/07-sap-integration.png`

**Pasos:**
1. Mismo usuario
2. Navegar a integraciones > SAP DMS
3. Asegurar que se vea:
   - Estado de conexión
   - Formulario de búsqueda
   - Panel de configuración

**Nota:** Similar al anterior, si no está implementado, usar mockup

---

### Screenshot 8: Detalle de Anotación
**Archivo:** `demo/screenshots/08-annotation-detail.png`

**Pasos:**
1. Login como `revisor.demo`
2. Documento con anotaciones
3. Hacer close-up de una anotación específica
4. Si es posible, mostrar tooltip o panel de edición abierto

---

### Screenshot 9: Búsqueda de Documentos
**Archivo:** `demo/screenshots/09-search-results.png`

**Pasos:**
1. Login como `usuario.demo`
2. En dashboard, usar búsqueda
3. Buscar: "procedimiento" o "seguridad"
4. Capturar resultados con highlighting

---

### Screenshot 10: Metadata de Documento
**Archivo:** `demo/screenshots/10-document-metadata.png`

**Pasos:**
1. Login como `admin.demo`
2. Abrir cualquier documento
3. Expandir panel de metadata (si existe)
4. Asegurar que se vea:
   - Autor, fecha, versión
   - Tags
   - Historial (si aplica)
   - Permisos

---

## 🛠️ Herramientas de Captura

### Linux (Ubuntu/Debian)
```bash
# Instalar gnome-screenshot si no está
sudo apt install gnome-screenshot

# Captura de ventana activa
gnome-screenshot -w

# Captura de área seleccionada
gnome-screenshot -a

# Con retraso de 5 segundos
gnome-screenshot -d 5 -w
```

### macOS
```bash
# Pantalla completa
Cmd + Shift + 3

# Área seleccionada
Cmd + Shift + 4

# Ventana específica
Cmd + Shift + 4, luego Space, click en ventana
```

### Windows
```bash
# Snipping Tool
Windows + Shift + S

# Print Screen
Windows + Print Screen
```

---

## ✅ Checklist de Captura

- [ ] 01-dashboard.png
- [ ] 02-document-viewer.png
- [ ] 03-annotations.png
- [ ] 04-comparison.png
- [ ] 05-graphql-playground.png
- [ ] 06-sharepoint-integration.png (opcional)
- [ ] 07-sap-integration.png (opcional)
- [ ] 08-annotation-detail.png
- [ ] 09-search-results.png
- [ ] 10-document-metadata.png

**Total requeridos:** 5 esenciales + 5 opcionales = 10 screenshots

---

## 📐 Especificaciones Técnicas

### Resolución
- **Mínimo:** 1920x1080 (Full HD)
- **Formato:** PNG sin compresión
- **Tamaño máximo:** ~2-3 MB por imagen

### Composición
- Incluir barra de URL del navegador
- UI limpia (sin notificaciones)
- Datos de demo visibles (usuarios: *.demo)
- Texto legible (no muy pequeño)

### Naming
```
[número]-[descripción]-[versión].png

Ejemplos:
01-dashboard-v1.png
02-document-viewer-v1.png
```

---

## 🚀 Script de Automatización (Opcional)

Si prefieres, puedes usar Playwright o Selenium para captura automática:

```python
# Ejemplo con Playwright (requiere: pip install playwright)
from playwright.sync_api import sync_playwright

def capture_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        # Screenshot 1: Dashboard
        page.goto("http://localhost:3000/login")
        page.fill("#username", "admin.demo")
        page.fill("#password", "Demo2025!")
        page.click("button[type=submit]")
        page.wait_for_url("**/dashboard")
        page.screenshot(path="demo/screenshots/01-dashboard.png")
        
        # ... más screenshots
        
        browser.close()

if __name__ == "__main__":
    capture_screenshots()
```

---

## 💡 Tips Finales

1. **Consistencia:** Usa mismo navegador y tamaño para todos
2. **Limpieza:** Modo incógnito o perfil limpio sin extensiones
3. **Timing:** Espera a que todo cargue (no spinners)
4. **Realismo:** Usa datos de demo (no producción)
5. **Calidad:** Resolución mínima Full HD

---

## 📞 Si Necesitas Ayuda

**Problemas comunes:**

**Q: Servicios no están corriendo**
```bash
# Verificar puertos
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
```

**Q: Datos no aparecen**
```bash
# Re-seed database
python demo/scripts/seed_demo_data.py
```

**Q: Frontend no renderiza PDFs**
```bash
# Verificar que PDFs existen
ls demo/sample-documents/*.pdf
```

---

**¡Listo para capturar!** 📸

**Tiempo estimado:** 20-30 minutos para 10 screenshots profesionales.
