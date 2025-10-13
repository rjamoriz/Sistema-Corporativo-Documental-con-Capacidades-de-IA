# 📄 Enhanced Document Viewer

Visor de documentos PDF avanzado con capacidades completas de visualización, navegación, búsqueda y anotaciones.

## ✨ Características

### 🔍 **Visualización y Navegación**
- ✅ Renderizado PDF con `react-pdf`
- ✅ Navegación entre páginas (anterior/siguiente/saltar a página)
- ✅ Miniaturas de páginas en sidebar
- ✅ Smooth scrolling

### 🔎 **Zoom y Rotación**
- ✅ 6 niveles de zoom: 50%, 75%, 100%, 125%, 150%, 200%
- ✅ Modo "Ajustar a ancho" (fit-to-width)
- ✅ Rotación en 90°: 0°, 90°, 180°, 270°
- ✅ Zoom responsive a tamaño de ventana

### 🔎 **Búsqueda**
- ✅ Búsqueda de texto en documento
- ✅ Campo de búsqueda con autocompletado
- ✅ Resaltado de resultados (próximamente)

### ⌨️ **Atajos de Teclado**
- `←` / `PageUp` - Página anterior
- `→` / `PageDown` - Página siguiente
- `Home` - Primera página
- `End` - Última página
- `+` / `=` - Aumentar zoom
- `-` / `_` - Reducir zoom
- `Ctrl+R` / `Cmd+R` - Rotar 90°
- `Ctrl+F` / `Cmd+F` - Enfocar búsqueda

### 📥 **Acciones**
- ✅ Descargar documento
- ✅ Imprimir documento
- ✅ Compartir (próximamente)

### 🎨 **Sistema de Anotaciones** (Próximamente)
- ⏳ Highlights (resaltados amarillos)
- ⏳ Sticky notes (notas adhesivas)
- ⏳ Redactions (redacciones negras)
- ⏳ Persistencia con GraphQL

## 📦 Instalación

Las dependencias ya están instaladas en el proyecto:

```json
{
  "dependencies": {
    "react-pdf": "^10.2.0",
    "pdfjs-dist": "^5.4.296"
  }
}
```

## 🚀 Uso

### Importación Básica

```tsx
import { EnhancedViewer } from '@/components/DocumentViewer';

function MyComponent() {
  return (
    <EnhancedViewer
      fileUrl="https://example.com/document.pdf"
      documentId="doc-123"
      initialPage={1}
      enableAnnotations={true}
      onLoadSuccess={(numPages) => console.log(`Loaded ${numPages} pages`)}
      onError={(error) => console.error('Error:', error)}
    />
  );
}
```

### Con URL Dinámica

```tsx
import { useState } from 'react';
import { EnhancedViewer } from '@/components/DocumentViewer';

function DocumentPage() {
  const [pdfUrl, setPdfUrl] = useState<string>('');

  return (
    <div className="h-screen flex flex-col">
      <input
        type="text"
        value={pdfUrl}
        onChange={(e) => setPdfUrl(e.target.value)}
        placeholder="Enter PDF URL"
      />
      {pdfUrl && (
        <EnhancedViewer
          fileUrl={pdfUrl}
          documentId={`doc-${Date.now()}`}
        />
      )}
    </div>
  );
}
```

### Con Upload de Archivo

```tsx
import { useState } from 'react';
import { EnhancedViewer } from '@/components/DocumentViewer';

function UploadAndView() {
  const [pdfUrl, setPdfUrl] = useState<string>('');

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      const url = URL.createObjectURL(file);
      setPdfUrl(url);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="application/pdf"
        onChange={handleFileUpload}
      />
      {pdfUrl && <EnhancedViewer fileUrl={pdfUrl} />}
    </div>
  );
}
```

### Con GraphQL (Datos del Backend)

```tsx
import { useQuery } from '@tanstack/react-query';
import { EnhancedViewer } from '@/components/DocumentViewer';

function DocumentViewer({ documentId }: { documentId: string }) {
  const { data } = useQuery({
    queryKey: ['document', documentId],
    queryFn: async () => {
      const response = await fetch('/api/graphql/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: `
            query GetDocument($id: ID!) {
              document(id: $id) {
                id
                filename
                url
                pageCount
              }
            }
          `,
          variables: { id: documentId }
        })
      });
      const json = await response.json();
      return json.data.document;
    }
  });

  if (!data) return <div>Loading...</div>;

  return (
    <EnhancedViewer
      fileUrl={data.url}
      documentId={data.id}
      onLoadSuccess={(numPages) => {
        console.log(`Expected: ${data.pageCount}, Loaded: ${numPages}`);
      }}
    />
  );
}
```

## 🎨 Props API

### `EnhancedViewerProps`

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `fileUrl` | `string` | **required** | URL o path del documento PDF |
| `documentId` | `string` | `undefined` | ID del documento (para anotaciones) |
| `initialPage` | `number` | `1` | Página inicial (1-indexed) |
| `onLoadSuccess` | `(numPages: number) => void` | `undefined` | Callback al cargar exitosamente |
| `onError` | `(error: Error) => void` | `undefined` | Callback en error |
| `enableAnnotations` | `boolean` | `true` | Habilitar/deshabilitar anotaciones |

## 🏗️ Arquitectura

```
DocumentViewer/
├── EnhancedViewer.tsx       # Componente principal
├── AnnotationLayer.tsx      # (Próximamente) Canvas de anotaciones
├── AnnotationTools.tsx      # (Próximamente) Toolbar de herramientas
├── ThumbnailSidebar.tsx     # (Próximamente) Sidebar componentizado
├── SearchPanel.tsx          # (Próximamente) Panel de búsqueda avanzado
├── index.ts                 # Exports
└── README.md                # Esta documentación
```

## 🔧 Configuración

### PDF.js Worker

El worker de PDF.js se carga automáticamente desde CDN:

```ts
pdfjs.GlobalWorkerOptions.workerSrc = 
  `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;
```

Para producción, considera descargar el worker localmente:

```bash
cp node_modules/pdfjs-dist/build/pdf.worker.min.js public/
```

Luego actualiza la configuración:

```ts
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';
```

### Estilos CSS

El componente requiere los estilos de `react-pdf`:

```tsx
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
```

Ya incluidos en `EnhancedViewer.tsx`.

## 🎯 Estados del Componente

```tsx
{
  numPages: number;           // Total de páginas
  pageNumber: number;         // Página actual (1-indexed)
  zoomIndex: number;          // Índice de zoom (0-5)
  rotation: number;           // Ángulo de rotación (0, 90, 180, 270)
  searchText: string;         // Texto de búsqueda
  showThumbnails: boolean;    // Mostrar sidebar de miniaturas
  fitToWidth: boolean;        // Modo ajustar a ancho
  containerWidth: number;     // Ancho del contenedor
}
```

## 🧪 Testing

### Test de Renderizado

```tsx
import { render, screen } from '@testing-library/react';
import { EnhancedViewer } from './EnhancedViewer';

test('renders PDF viewer', () => {
  render(<EnhancedViewer fileUrl="test.pdf" />);
  expect(screen.getByLabelText('Página anterior')).toBeInTheDocument();
});
```

### Test de Navegación

```tsx
test('navigates to next page', async () => {
  const { getByLabelText } = render(
    <EnhancedViewer fileUrl="test.pdf" />
  );
  
  const nextButton = getByLabelText('Página siguiente');
  fireEvent.click(nextButton);
  
  // Verificar que la página cambió
  expect(screen.getByDisplayValue('2')).toBeInTheDocument();
});
```

## 🚀 Roadmap

### Fase 1: Visualización Básica ✅ (Completado)
- [x] Renderizado PDF
- [x] Navegación entre páginas
- [x] Zoom controls
- [x] Rotación
- [x] Miniaturas
- [x] Atajos de teclado

### Fase 2: Sistema de Anotaciones ⏳ (En progreso)
- [ ] AnnotationLayer component
- [ ] Highlight tool
- [ ] Sticky note tool
- [ ] Redaction tool
- [ ] GraphQL mutations integration
- [ ] Real-time sync

### Fase 3: Búsqueda Avanzada ⏳
- [ ] Full-text search con highlighting
- [ ] Navegación entre resultados
- [ ] Filtros avanzados
- [ ] Búsqueda por metadatos

### Fase 4: Comparación de Versiones ⏳
- [ ] Split view (lado a lado)
- [ ] Diff algorithm
- [ ] Highlight de cambios
- [ ] Timeline de versiones

### Fase 5: Optimización 🔮
- [ ] Virtual scrolling para documentos grandes
- [ ] Lazy loading de páginas
- [ ] Caching inteligente
- [ ] Web Workers para procesamiento

## 📊 Performance

### Métricas Objetivo
- ⚡ First Paint: < 1s
- ⚡ Page Navigation: < 100ms
- ⚡ Zoom/Rotate: < 50ms
- 💾 Memory: < 100MB para documentos de 50 páginas

### Optimizaciones Aplicadas
- ✅ React.memo para prevenir re-renders
- ✅ useCallback para funciones estables
- ✅ Lazy loading de thumbnails
- ✅ Debounce en búsqueda

## 🐛 Problemas Conocidos

1. **PDF.js Worker CORS**: En desarrollo local, puede haber issues CORS. Usar CDN o copiar worker.
2. **Large PDFs**: Documentos > 100 páginas pueden ser lentos. Implementar virtual scrolling.
3. **Mobile**: Gestos táctiles no completamente optimizados aún.

## 🤝 Contribuir

Para agregar nuevas features:

1. Crear branch: `git checkout -b feature/nueva-feature`
2. Implementar feature en `EnhancedViewer.tsx` o nuevo componente
3. Agregar tests en `EnhancedViewer.test.tsx`
4. Actualizar documentación
5. Crear PR

## 📝 Changelog

### v1.0.0 (Octubre 2025)
- ✅ Implementación inicial del Enhanced Viewer
- ✅ Navegación completa de páginas
- ✅ Sistema de zoom (6 niveles + fit-to-width)
- ✅ Rotación en 90°
- ✅ Sidebar de miniaturas
- ✅ Búsqueda básica
- ✅ Atajos de teclado
- ✅ Toolbar completo

### v1.1.0 (Próximamente)
- ⏳ Sistema de anotaciones
- ⏳ GraphQL integration
- ⏳ Real-time collaboration

---

**Desarrollado para FinancIA 2030**  
Sprint 6: Enhanced Document Viewer  
Octubre 2025
