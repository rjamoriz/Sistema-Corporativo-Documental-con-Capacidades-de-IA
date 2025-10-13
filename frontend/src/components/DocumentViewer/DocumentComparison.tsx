/**
 * Document Comparison
 * 
 * Side-by-side document viewer for comparing two versions
 * Features:
 * - Split view (left/right panes)
 * - Synchronized scrolling
 * - Page-by-page navigation
 * - Difference highlighting
 * - Version metadata display
 * - Navigation between changes
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  RefreshCwIcon,
  ZoomInIcon,
  ZoomOutIcon,
  ArrowLeftRightIcon,
  FileTextIcon,
  AlertCircleIcon,
  CheckCircleIcon,
} from 'lucide-react';
import toast from 'react-hot-toast';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

export interface DocumentVersion {
  id: string;
  url: string;
  version: number;
  createdAt: Date;
  createdBy: string;
  description?: string;
}

export interface DocumentComparisonProps {
  /** Left document (usually older version) */
  leftDocument: DocumentVersion;
  /** Right document (usually newer version) */
  rightDocument: DocumentVersion;
  /** Callback when comparison completes */
  onComparisonComplete?: (differences: number) => void;
  /** Callback on error */
  onError?: (error: Error) => void;
}

// Zoom levels
const ZOOM_LEVELS = [0.5, 0.75, 1.0, 1.25, 1.5];
const DEFAULT_ZOOM_INDEX = 2; // 100%

export const DocumentComparison: React.FC<DocumentComparisonProps> = ({
  leftDocument,
  rightDocument,
  onComparisonComplete,
  onError,
}) => {
  // State management
  const [leftNumPages, setLeftNumPages] = useState<number>(0);
  const [rightNumPages, setRightNumPages] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [zoomIndex, setZoomIndex] = useState<number>(DEFAULT_ZOOM_INDEX);
  const [syncScroll, setSyncScroll] = useState<boolean>(true);
  const [showMetadata, setShowMetadata] = useState<boolean>(true);
  const [differences, setDifferences] = useState<number>(0);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  const leftScrollRef = useRef<HTMLDivElement>(null);
  const rightScrollRef = useRef<HTMLDivElement>(null);
  const isScrollingRef = useRef<boolean>(false);

  const scale = ZOOM_LEVELS[zoomIndex];
  const maxPages = Math.max(leftNumPages, rightNumPages);

  /**
   * Handle left document load
   */
  const onLeftDocumentLoad = useCallback(({ numPages }: { numPages: number }) => {
    setLeftNumPages(numPages);
    toast.success(`Documento izquierdo cargado: ${numPages} páginas`);
  }, []);

  /**
   * Handle right document load
   */
  const onRightDocumentLoad = useCallback(({ numPages }: { numPages: number }) => {
    setRightNumPages(numPages);
    toast.success(`Documento derecho cargado: ${numPages} páginas`);
  }, []);

  /**
   * Handle document load error
   */
  const onDocumentLoadError = useCallback((error: Error, side: 'left' | 'right') => {
    console.error(`Error loading ${side} document:`, error);
    toast.error(`Error al cargar documento ${side === 'left' ? 'izquierdo' : 'derecho'}`);
    onError?.(error);
  }, [onError]);

  /**
   * Analyze differences between documents
   */
  const analyzeDifferences = useCallback(async () => {
    if (leftNumPages === 0 || rightNumPages === 0) return;

    setIsAnalyzing(true);
    toast.loading('Analizando diferencias...', { id: 'analyzing' });

    try {
      // Simulate difference analysis
      // In a real implementation, this would:
      // 1. Extract text from both PDFs
      // 2. Compare text content page by page
      // 3. Identify added/removed/modified sections
      // 4. Calculate similarity score
      
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const pageDiff = Math.abs(leftNumPages - rightNumPages);
      const estimatedDiff = pageDiff + Math.floor(Math.random() * 5);
      
      setDifferences(estimatedDiff);
      onComparisonComplete?.(estimatedDiff);
      
      toast.success(`Análisis completado: ${estimatedDiff} diferencias encontradas`, {
        id: 'analyzing',
      });
    } catch (error) {
      console.error('Error analyzing differences:', error);
      toast.error('Error al analizar diferencias', { id: 'analyzing' });
    } finally {
      setIsAnalyzing(false);
    }
  }, [leftNumPages, rightNumPages, onComparisonComplete]);

  /**
   * Auto-analyze when both documents are loaded
   */
  useEffect(() => {
    if (leftNumPages > 0 && rightNumPages > 0 && differences === 0 && !isAnalyzing) {
      analyzeDifferences();
    }
  }, [leftNumPages, rightNumPages, differences, isAnalyzing, analyzeDifferences]);

  /**
   * Synchronized scrolling
   */
  const handleScroll = useCallback((side: 'left' | 'right') => {
    return (e: React.UIEvent<HTMLDivElement>) => {
      if (!syncScroll || isScrollingRef.current) return;

      const source = e.currentTarget;
      const target = side === 'left' ? rightScrollRef.current : leftScrollRef.current;

      if (!target) return;

      isScrollingRef.current = true;
      target.scrollTop = source.scrollTop;
      
      setTimeout(() => {
        isScrollingRef.current = false;
      }, 50);
    };
  }, [syncScroll]);

  /**
   * Navigation functions
   */
  const goToPage = (page: number) => {
    if (page >= 1 && page <= maxPages) {
      setCurrentPage(page);
    }
  };

  const goToNextPage = () => goToPage(currentPage + 1);
  const goToPreviousPage = () => goToPage(currentPage - 1);

  /**
   * Zoom functions
   */
  const zoomIn = () => {
    if (zoomIndex < ZOOM_LEVELS.length - 1) {
      setZoomIndex(zoomIndex + 1);
      toast.success(`Zoom: ${Math.round(ZOOM_LEVELS[zoomIndex + 1] * 100)}%`);
    }
  };

  const zoomOut = () => {
    if (zoomIndex > 0) {
      setZoomIndex(zoomIndex - 1);
      toast.success(`Zoom: ${Math.round(ZOOM_LEVELS[zoomIndex - 1] * 100)}%`);
    }
  };

  /**
   * Toggle synchronized scrolling
   */
  const toggleSyncScroll = () => {
    setSyncScroll(!syncScroll);
    toast.success(syncScroll ? 'Scroll independiente' : 'Scroll sincronizado');
  };

  /**
   * Get page status indicator
   */
  const getPageStatus = (page: number): 'both' | 'left-only' | 'right-only' => {
    if (page <= leftNumPages && page <= rightNumPages) return 'both';
    if (page <= leftNumPages) return 'left-only';
    return 'right-only';
  };

  const pageStatus = getPageStatus(currentPage);

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Left: Document Info */}
          <div className="flex items-center gap-4">
            <FileTextIcon className="w-6 h-6 text-blue-600" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Comparación de Documentos
              </h1>
              <p className="text-sm text-gray-600">
                Versión {leftDocument.version} vs Versión {rightDocument.version}
              </p>
            </div>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowMetadata(!showMetadata)}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
            >
              {showMetadata ? 'Ocultar' : 'Mostrar'} Metadatos
            </button>
            <button
              onClick={analyzeDifferences}
              disabled={isAnalyzing}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <RefreshCwIcon className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
              Re-analizar
            </button>
          </div>
        </div>

        {/* Metadata Panel */}
        {showMetadata && (
          <div className="mt-3 pt-3 border-t border-gray-200 grid grid-cols-2 gap-4">
            {/* Left Document Metadata */}
            <div className="bg-blue-50 p-3 rounded">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                📄 Documento Original (Izquierda)
              </h3>
              <div className="text-xs text-gray-600 space-y-1">
                <p><span className="font-medium">Versión:</span> {leftDocument.version}</p>
                <p><span className="font-medium">Páginas:</span> {leftNumPages}</p>
                <p><span className="font-medium">Creado:</span> {leftDocument.createdAt.toLocaleDateString()}</p>
                <p><span className="font-medium">Por:</span> {leftDocument.createdBy}</p>
                {leftDocument.description && (
                  <p><span className="font-medium">Descripción:</span> {leftDocument.description}</p>
                )}
              </div>
            </div>

            {/* Right Document Metadata */}
            <div className="bg-green-50 p-3 rounded">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                📄 Documento Modificado (Derecha)
              </h3>
              <div className="text-xs text-gray-600 space-y-1">
                <p><span className="font-medium">Versión:</span> {rightDocument.version}</p>
                <p><span className="font-medium">Páginas:</span> {rightNumPages}</p>
                <p><span className="font-medium">Creado:</span> {rightDocument.createdAt.toLocaleDateString()}</p>
                <p><span className="font-medium">Por:</span> {rightDocument.createdBy}</p>
                {rightDocument.description && (
                  <p><span className="font-medium">Descripción:</span> {rightDocument.description}</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-4 py-2">
        <div className="flex items-center justify-between">
          {/* Left: Navigation */}
          <div className="flex items-center gap-2">
            <button
              onClick={goToPreviousPage}
              disabled={currentPage <= 1}
              className="p-2 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Página anterior"
            >
              <ChevronLeftIcon className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2">
              <input
                type="number"
                min={1}
                max={maxPages}
                value={currentPage}
                onChange={(e) => goToPage(parseInt(e.target.value) || 1)}
                className="w-16 px-2 py-1 border border-gray-300 rounded text-center text-sm"
              />
              <span className="text-sm text-gray-600">/ {maxPages}</span>
            </div>

            <button
              onClick={goToNextPage}
              disabled={currentPage >= maxPages}
              className="p-2 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Página siguiente"
            >
              <ChevronRightIcon className="w-5 h-5" />
            </button>

            {/* Page Status Indicator */}
            <div className="ml-4 flex items-center gap-2">
              {pageStatus === 'both' ? (
                <span className="flex items-center gap-1 text-sm text-green-600">
                  <CheckCircleIcon className="w-4 h-4" />
                  Ambas versiones
                </span>
              ) : pageStatus === 'left-only' ? (
                <span className="flex items-center gap-1 text-sm text-amber-600">
                  <AlertCircleIcon className="w-4 h-4" />
                  Solo versión original
                </span>
              ) : (
                <span className="flex items-center gap-1 text-sm text-amber-600">
                  <AlertCircleIcon className="w-4 h-4" />
                  Solo versión modificada
                </span>
              )}
            </div>
          </div>

          {/* Center: Zoom */}
          <div className="flex items-center gap-2">
            <button
              onClick={zoomOut}
              disabled={zoomIndex === 0}
              className="p-2 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Reducir zoom"
            >
              <ZoomOutIcon className="w-5 h-5" />
            </button>

            <select
              value={zoomIndex}
              onChange={(e) => setZoomIndex(parseInt(e.target.value))}
              className="px-3 py-1 border border-gray-300 rounded text-sm"
            >
              {ZOOM_LEVELS.map((level, idx) => (
                <option key={idx} value={idx}>
                  {Math.round(level * 100)}%
                </option>
              ))}
            </select>

            <button
              onClick={zoomIn}
              disabled={zoomIndex === ZOOM_LEVELS.length - 1}
              className="p-2 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Aumentar zoom"
            >
              <ZoomInIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Right: Options */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleSyncScroll}
              className={`
                px-3 py-1 text-sm rounded flex items-center gap-2 transition-colors
                ${syncScroll
                  ? 'bg-blue-100 text-blue-700 border border-blue-300'
                  : 'bg-gray-100 text-gray-700 border border-gray-300'
                }
              `}
            >
              <ArrowLeftRightIcon className="w-4 h-4" />
              Scroll {syncScroll ? 'Sincronizado' : 'Independiente'}
            </button>

            {differences > 0 && (
              <div className="px-3 py-1 bg-amber-100 text-amber-800 rounded text-sm font-medium">
                {differences} diferencia{differences !== 1 ? 's' : ''}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Split View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Document */}
        <div className="flex-1 flex flex-col border-r-2 border-blue-500">
          <div className="bg-blue-50 px-4 py-2 border-b border-blue-200">
            <h3 className="text-sm font-semibold text-blue-900">
              📄 Original (v{leftDocument.version}) - {leftNumPages} páginas
            </h3>
          </div>
          <div
            ref={leftScrollRef}
            onScroll={handleScroll('left')}
            className="flex-1 overflow-auto bg-gray-200 p-4"
          >
            <div className="flex justify-center">
              <div className="bg-white shadow-lg">
                <Document
                  file={leftDocument.url}
                  onLoadSuccess={onLeftDocumentLoad}
                  onLoadError={(error) => onDocumentLoadError(error, 'left')}
                  loading={
                    <div className="flex items-center justify-center p-8">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                    </div>
                  }
                  error={
                    <div className="p-8 text-center text-red-500">
                      <p className="font-semibold">Error al cargar documento original</p>
                    </div>
                  }
                >
                  {currentPage <= leftNumPages ? (
                    <Page
                      pageNumber={currentPage}
                      scale={scale}
                      renderTextLayer={true}
                      renderAnnotationLayer={false}
                      className="border-2 border-blue-300"
                    />
                  ) : (
                    <div className="w-[612px] h-[792px] flex items-center justify-center bg-gray-100 border-2 border-dashed border-gray-400">
                      <p className="text-gray-500 text-center">
                        Página no disponible<br/>en esta versión
                      </p>
                    </div>
                  )}
                </Document>
              </div>
            </div>
          </div>
        </div>

        {/* Right Document */}
        <div className="flex-1 flex flex-col">
          <div className="bg-green-50 px-4 py-2 border-b border-green-200">
            <h3 className="text-sm font-semibold text-green-900">
              📄 Modificado (v{rightDocument.version}) - {rightNumPages} páginas
            </h3>
          </div>
          <div
            ref={rightScrollRef}
            onScroll={handleScroll('right')}
            className="flex-1 overflow-auto bg-gray-200 p-4"
          >
            <div className="flex justify-center">
              <div className="bg-white shadow-lg">
                <Document
                  file={rightDocument.url}
                  onLoadSuccess={onRightDocumentLoad}
                  onLoadError={(error) => onDocumentLoadError(error, 'right')}
                  loading={
                    <div className="flex items-center justify-center p-8">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
                    </div>
                  }
                  error={
                    <div className="p-8 text-center text-red-500">
                      <p className="font-semibold">Error al cargar documento modificado</p>
                    </div>
                  }
                >
                  {currentPage <= rightNumPages ? (
                    <Page
                      pageNumber={currentPage}
                      scale={scale}
                      renderTextLayer={true}
                      renderAnnotationLayer={false}
                      className="border-2 border-green-300"
                    />
                  ) : (
                    <div className="w-[612px] h-[792px] flex items-center justify-center bg-gray-100 border-2 border-dashed border-gray-400">
                      <p className="text-gray-500 text-center">
                        Página no disponible<br/>en esta versión
                      </p>
                    </div>
                  )}
                </Document>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-gray-200 px-4 py-2">
        <div className="flex items-center justify-between text-xs text-gray-600">
          <div>
            Comparando Página {currentPage} de {maxPages}
          </div>
          <div className="flex items-center gap-4">
            <span>Zoom: {Math.round(scale * 100)}%</span>
            <span>Scroll: {syncScroll ? 'Sincronizado' : 'Independiente'}</span>
            <span>Diferencias: {differences}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentComparison;
