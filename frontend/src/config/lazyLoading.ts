/**
 * Lazy Loading Components Configuration
 * Code splitting para mejorar performance del frontend
 */
import { lazy } from 'react';

// ========================================
// LAZY LOADING DE COMPONENTES PESADOS
// ========================================

// Dashboard components (heavy with charts)
export const ThirdPartyValidationDashboard = lazy(
  () => import('@/components/validation/ThirdPartyValidationDashboard')
);

// Search components (heavy with OpenSearch integration)
export const SearchInterface = lazy(
  () => import('@/components/search/SearchInterface')
);

export const AdvancedSearch = lazy(
  () => import('@/components/search/AdvancedSearch')
);

// Document viewer (heavy with PDF rendering)
export const DocumentViewer = lazy(
  () => import('@/components/documents/DocumentViewer')
);

// Upload component (heavy with file processing)
export const UploadComponent = lazy(
  () => import('@/components/Upload')
);

// Analytics dashboards
export const AnalyticsDashboard = lazy(
  () => import('@/components/analytics/AnalyticsDashboard')
);

export const ComplianceDashboard = lazy(
  () => import('@/components/compliance/ComplianceDashboard')
);

// Admin panels
export const UserManagement = lazy(
  () => import('@/components/admin/UserManagement')
);

export const SystemSettings = lazy(
  () => import('@/components/admin/SystemSettings')
);

// ========================================
// PRELOAD FUNCTIONS
// ========================================

/**
 * Preload crítico para rutas comunes
 * Llamar en idle time o al hover de links
 */
export const preloadCritical = () => {
  // Precargar componentes que probablemente se usarán pronto
  import('@/components/search/SearchInterface');
  import('@/components/documents/DocumentViewer');
};

/**
 * Preload para admin (solo si usuario es admin)
 */
export const preloadAdmin = () => {
  import('@/components/admin/UserManagement');
  import('@/components/admin/SystemSettings');
};

/**
 * Preload validation dashboard
 */
export const preloadValidationDashboard = () => {
  import('@/components/validation/ThirdPartyValidationDashboard');
};

// ========================================
// ROUTE-BASED CODE SPLITTING
// ========================================

export const routes = {
  // Public routes
  home: lazy(() => import('@/pages/Home')),
  login: lazy(() => import('@/pages/Login')),
  
  // Protected routes
  dashboard: lazy(() => import('@/pages/Dashboard')),
  documents: lazy(() => import('@/pages/Documents')),
  search: lazy(() => import('@/pages/Search')),
  validation: lazy(() => import('@/pages/Validation')),
  analytics: lazy(() => import('@/pages/Analytics')),
  
  // Admin routes
  admin: lazy(() => import('@/pages/Admin')),
  users: lazy(() => import('@/pages/admin/Users')),
  settings: lazy(() => import('@/pages/admin/Settings')),
};

// ========================================
// CHUNK OPTIMIZATION CONFIG
// ========================================

/**
 * Configuración de chunking para Vite
 * Agregar a vite.config.ts
 */
export const chunkConfig = {
  manualChunks: {
    // Vendor chunks
    'react-vendor': ['react', 'react-dom', 'react-router-dom'],
    'ui-vendor': ['@mui/material', '@mui/icons-material', '@emotion/react', '@emotion/styled'],
    'charts-vendor': ['recharts'],
    'utils-vendor': ['axios', 'date-fns', 'lodash'],
    
    // Feature chunks
    'validation': [
      './src/components/validation/ThirdPartyValidationDashboard',
      './src/services/validationService'
    ],
    'search': [
      './src/components/search/SearchInterface',
      './src/components/search/AdvancedSearch'
    ],
    'documents': [
      './src/components/documents/DocumentViewer',
      './src/components/documents/DocumentList'
    ],
  },
};

export default {
  ThirdPartyValidationDashboard,
  SearchInterface,
  AdvancedSearch,
  DocumentViewer,
  UploadComponent,
  AnalyticsDashboard,
  ComplianceDashboard,
  UserManagement,
  SystemSettings,
  preloadCritical,
  preloadAdmin,
  preloadValidationDashboard,
  routes,
  chunkConfig,
};
