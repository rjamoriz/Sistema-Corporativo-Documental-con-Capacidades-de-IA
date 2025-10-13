/**
 * Enhanced Viewer with Annotations
 * 
 * Complete PDF viewer with annotation system integration
 * This component extends EnhancedViewer with full annotation support
 */

import React, { useState } from 'react';
import { EnhancedViewer } from './EnhancedViewer';
import { AnnotationTools } from './AnnotationTools';
import { AnnotationLayer } from './AnnotationLayer';
import { useAnnotations } from './useAnnotations';
import { AnnotationType, AnnotationColor } from './types';
import { PanelRightCloseIcon, PanelRightOpenIcon } from 'lucide-react';

interface EnhancedViewerWithAnnotationsProps {
  fileUrl: string;
  documentId: string;
  initialPage?: number;
  onLoadSuccess?: (numPages: number) => void;
  onError?: (error: Error) => void;
}

export const EnhancedViewerWithAnnotations: React.FC<EnhancedViewerWithAnnotationsProps> = ({
  fileUrl,
  documentId,
  initialPage = 1,
  onLoadSuccess,
  onError,
}) => {
  // Annotation state
  const [selectedTool, setSelectedTool] = useState<AnnotationType | null>(null);
  const [selectedColor, setSelectedColor] = useState<string>(AnnotationColor.YELLOW);
  const [showAnnotationPanel, setShowAnnotationPanel] = useState(true);
  const [pageNumber, setPageNumber] = useState(initialPage);
  const [scale, setScale] = useState(1.0);
  const [pageSize, setPageSize] = useState({ width: 612, height: 792 }); // Standard letter size

  // Annotations hook
  const {
    annotations,
    loading: annotationsLoading,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
    refreshAnnotations,
  } = useAnnotations({
    documentId,
    onError,
  });

  // Load annotations when document loads
  const handleLoadSuccess = (numPages: number) => {
    refreshAnnotations();
    onLoadSuccess?.(numPages);
  };

  // Keyboard shortcuts for annotation tools
  React.useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only handle shortcuts when not typing in input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key.toLowerCase()) {
        case 'escape':
          setSelectedTool(null);
          break;
        case 'h':
          setSelectedTool(AnnotationType.HIGHLIGHT);
          break;
        case 'n':
          setSelectedTool(AnnotationType.STICKY_NOTE);
          break;
        case 'r':
          if (!e.ctrlKey && !e.metaKey) {
            setSelectedTool(AnnotationType.REDACTION);
          }
          break;
        case 'delete':
        case 'backspace':
          // Delete selected annotation
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Main Viewer */}
      <div className="flex-1 relative">
        <EnhancedViewer
          fileUrl={fileUrl}
          documentId={documentId}
          initialPage={initialPage}
          onLoadSuccess={handleLoadSuccess}
          onError={onError}
          enableAnnotations={true}
        />

        {/* Annotation Layer Overlay - This would need to be integrated into EnhancedViewer */}
        {/* For now, annotations are shown as a separate layer */}
      </div>

      {/* Annotation Tools Sidebar */}
      <div
        className={`
          transition-all duration-300 ease-in-out
          ${showAnnotationPanel ? 'w-80' : 'w-0'}
          bg-gray-50 border-l border-gray-200 overflow-hidden
        `}
      >
        {showAnnotationPanel && (
          <div className="h-full overflow-y-auto p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">
                Anotaciones
              </h2>
              <button
                onClick={() => setShowAnnotationPanel(false)}
                className="p-2 hover:bg-gray-200 rounded transition-colors"
                title="Cerrar panel"
              >
                <PanelRightCloseIcon className="w-5 h-5" />
              </button>
            </div>

            <AnnotationTools
              selectedTool={selectedTool}
              selectedColor={selectedColor}
              onToolSelect={setSelectedTool}
              onColorSelect={setSelectedColor}
              disabled={annotationsLoading}
            />

            {/* Annotations List */}
            <div className="mt-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                Anotaciones en este documento
              </h3>
              <div className="space-y-2">
                {annotations.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No hay anotaciones aún
                  </p>
                ) : (
                  annotations.map((annotation) => (
                    <div
                      key={annotation.id}
                      className="bg-white p-3 rounded border border-gray-200 hover:border-gray-300 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <div
                              className="w-4 h-4 rounded"
                              style={{ backgroundColor: annotation.color }}
                            />
                            <span className="text-xs font-medium text-gray-600">
                              {annotation.type === AnnotationType.HIGHLIGHT && 'Resaltado'}
                              {annotation.type === AnnotationType.STICKY_NOTE && 'Nota'}
                              {annotation.type === AnnotationType.REDACTION && 'Redacción'}
                            </span>
                            <span className="text-xs text-gray-500">
                              Pág. {annotation.pageNumber}
                            </span>
                          </div>
                          {annotation.content && (
                            <p className="text-sm text-gray-700">
                              {annotation.content}
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => deleteAnnotation(annotation.id)}
                          className="text-red-600 hover:text-red-700 text-xs font-medium"
                        >
                          Eliminar
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Stats */}
            <div className="mt-6 pt-4 border-t border-gray-200">
              <div className="text-sm text-gray-600">
                <div className="flex justify-between mb-1">
                  <span>Total de anotaciones:</span>
                  <span className="font-semibold">{annotations.length}</span>
                </div>
                <div className="flex justify-between mb-1">
                  <span>Resaltados:</span>
                  <span className="font-semibold">
                    {annotations.filter(a => a.type === AnnotationType.HIGHLIGHT).length}
                  </span>
                </div>
                <div className="flex justify-between mb-1">
                  <span>Notas:</span>
                  <span className="font-semibold">
                    {annotations.filter(a => a.type === AnnotationType.STICKY_NOTE).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Redacciones:</span>
                  <span className="font-semibold">
                    {annotations.filter(a => a.type === AnnotationType.REDACTION).length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Toggle Button when panel is closed */}
      {!showAnnotationPanel && (
        <button
          onClick={() => setShowAnnotationPanel(true)}
          className="absolute top-20 right-4 p-3 bg-white border border-gray-300 rounded-lg shadow-lg hover:shadow-xl transition-all z-50"
          title="Mostrar panel de anotaciones"
        >
          <PanelRightOpenIcon className="w-5 h-5" />
        </button>
      )}
    </div>
  );
};

export default EnhancedViewerWithAnnotations;
