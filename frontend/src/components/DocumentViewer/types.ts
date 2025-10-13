/**
 * Annotation Types
 * 
 * Type definitions for the annotation system
 */

export enum AnnotationType {
  HIGHLIGHT = 'HIGHLIGHT',
  STICKY_NOTE = 'STICKY_NOTE',
  REDACTION = 'REDACTION',
  COMMENT = 'COMMENT',
}

export enum AnnotationColor {
  YELLOW = '#FFEB3B',
  GREEN = '#4CAF50',
  BLUE = '#2196F3',
  RED = '#F44336',
  PURPLE = '#9C27B0',
  ORANGE = '#FF9800',
  BLACK = '#000000',
}

export interface Position {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Annotation {
  id: string;
  documentId: string;
  userId: string;
  type: AnnotationType;
  pageNumber: number;
  position: Position;
  content?: string;
  color: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface AnnotationInput {
  documentId: string;
  type: AnnotationType;
  pageNumber: number;
  position: Position;
  content?: string;
  color?: string;
}

export interface AnnotationUpdateInput {
  content?: string;
  position?: Position;
  color?: string;
}

export interface AnnotationLayerProps {
  documentId: string;
  pageNumber: number;
  pageWidth: number;
  pageHeight: number;
  scale: number;
  annotations: Annotation[];
  selectedTool: AnnotationType | null;
  selectedColor: string;
  onAnnotationCreate: (annotation: AnnotationInput) => void;
  onAnnotationUpdate: (id: string, update: AnnotationUpdateInput) => void;
  onAnnotationDelete: (id: string) => void;
  onAnnotationSelect?: (id: string | null) => void;
}

export interface AnnotationToolsProps {
  selectedTool: AnnotationType | null;
  selectedColor: string;
  onToolSelect: (tool: AnnotationType | null) => void;
  onColorSelect: (color: string) => void;
  disabled?: boolean;
}
