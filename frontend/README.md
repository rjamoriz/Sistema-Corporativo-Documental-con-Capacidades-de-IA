# Frontend - React + TypeScript + Vite

Aplicación frontend del Sistema Corporativo Documental con capacidades de IA.

## 🚀 Tecnologías

- **React 18** - Framework UI
- **TypeScript** - Type safety
- **Vite** - Build tool y dev server
- **TailwindCSS** - Styling
- **React Router** - Routing
- **TanStack Query** - Data fetching y caching
- **Zustand** - State management
- **Recharts** - Data visualization
- **React Dropzone** - File uploads
- **React Markdown** - Markdown rendering

## 📦 Instalación

```bash
# Instalar dependencias
npm install

# Copiar variables de entorno
cp .env.example .env

# Editar .env con la URL del backend
nano .env
```

## 🏃 Ejecución

```bash
# Desarrollo (puerto 3000)
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview

# Linting
npm run lint

# Tests
npm run test
```

## 📁 Estructura

```
src/
├── components/          # Componentes React
│   ├── Dashboard.tsx   # Dashboard principal
│   ├── Upload.tsx      # Subida de documentos
│   ├── Search.tsx      # Búsqueda híbrida
│   ├── RAGChat.tsx     # Chat con RAG
│   └── Layout.tsx      # Layout principal
├── lib/                # Utilidades
│   ├── api.ts          # Cliente axios
│   └── api-client.ts   # API endpoints
├── store/              # Zustand stores
│   ├── authStore.ts    # Auth state
│   └── uploadStore.ts  # Upload state
├── types/              # TypeScript types
│   └── index.ts        # Types centralizados
├── App.tsx             # App principal
├── main.tsx            # Entry point
└── index.css           # Estilos globales
```

## 🔧 Configuración

### API Backend

Configura la URL del backend en `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Proxy de Desarrollo

Vite está configurado para hacer proxy de `/api` al backend en desarrollo:

```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

## 🎨 Características

### Dashboard
- Estadísticas generales
- Gráficos de distribución por categoría
- Distribución de riesgos (pie chart)
- Estado de cumplimiento
- Documentos recientes

### Upload
- Drag & drop de archivos
- Múltiples formatos soportados
- Barra de progreso
- Queue de uploads
- Validación de tamaño y tipo

### Search
- Búsqueda híbrida (BM25 + vectorial)
- Filtros por categoría, fecha, riesgo
- Modos: híbrida, semántica, palabras clave
- Paginación de resultados
- Snippets con highlighting

### RAG Chat
- Chat conversacional con documentos
- Streaming de respuestas
- Referencias con scores
- Citaciones automáticas
- Markdown rendering

## 🔒 Autenticación

El frontend usa JWT tokens almacenados en localStorage:

```typescript
// Login
const { access_token, user } = await authApi.login(email, password);
useAuthStore.getState().login(access_token, user);

// Logout
useAuthStore.getState().logout();
```

Todas las requests incluyen el token automáticamente vía interceptor de axios.

## 📊 State Management

### Auth Store (Zustand + persist)
```typescript
const { user, isAuthenticated, login, logout } = useAuthStore();
```

### Upload Store (Zustand)
```typescript
const { uploads, addUpload, updateUpload, removeUpload } = useUploadStore();
```

## 🎯 API Client

Todos los endpoints están tipados y documentados en `src/lib/api-client.ts`:

```typescript
// Documents
await documentsApi.uploadDocument(file, userId);
await documentsApi.getDocument(documentId);
await documentsApi.listDocuments({ category: 'LEGAL' });

// Search
await searchApi.search({ query: 'contrato', search_mode: 'hybrid' });

// RAG
await ragApi.ask({ query: '¿Qué dice sobre privacidad?' });
await ragApi.askStream({ query, stream: true }, onChunk, onComplete);
```

## 🚀 Deployment

### Build

```bash
npm run build
```

Genera los archivos estáticos en `dist/`.

### Docker

```dockerfile
FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Variables de Entorno

En producción, configura:
- `VITE_API_BASE_URL`: URL del backend API

## 📝 TODO

- [ ] Implementar componente de Viewer de documentos
- [ ] Dashboard de Riesgos
- [ ] Dashboard de Cumplimiento
- [ ] Página de perfil de usuario
- [ ] Dark mode
- [ ] Internacionalización (i18n)
- [ ] Tests unitarios (Vitest)
- [ ] Tests E2E (Playwright)

## 📄 Licencia

Propietario - Uso interno corporativo
