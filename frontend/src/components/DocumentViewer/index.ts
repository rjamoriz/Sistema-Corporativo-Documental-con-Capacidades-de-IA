/**
 * Enhanced Viewer - Export Module
 * 
 * Central export point for all document viewer components
 */

export { EnhancedViewer } from './EnhancedViewer';
export { EnhancedViewerWithAnnotations } from './EnhancedViewerWithAnnotations';
export { AnnotationLayer } from './AnnotationLayer';
export { AnnotationTools } from './AnnotationTools';
export { useAnnotations } from './useAnnotations';
export { DocumentComparison } from './DocumentComparison';

// Export types
export type {
  Annotation,
  AnnotationType,
  AnnotationColor,
  Position,
  AnnotationInput,
  AnnotationUpdateInput,
  AnnotationLayerProps,
  AnnotationToolsProps,
} from './types';

export type { DocumentVersion, DocumentComparisonProps } from './DocumentComparison';

export { AnnotationType as AnnotationTypeEnum, AnnotationColor as AnnotationColorEnum } from './types';

