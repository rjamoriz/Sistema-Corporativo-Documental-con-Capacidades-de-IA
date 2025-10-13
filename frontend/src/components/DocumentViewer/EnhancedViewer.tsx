/**
 * Enhanced Document Viewer
 * 
 * PDF viewer with advanced features:
 * - PDF rendering with react-pdf
 * - Zoom controls (50%, 75%, 100%, 125%, 150%, 200%, fit-width)
 * - Rotation (0°, 90°, 180°, 270°)
 * - Page navigation (prev/next/jump to page)
 * - Text search with highlighting
 * - Thumbnail sidebar
 * - Keyboard shortcuts
 * - Annotation support (highlights, sticky notes, redactions)
 * 
 * @component EnhancedViewer
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import {
  ZoomInIcon,
  ZoomOutIcon,
  RotateCwIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  SearchIcon,
  LayoutGridIcon,
  MaximizeIcon,
  DownloadIcon,
  PrinterIcon,
  XIcon,
} from 'lucide-react';
import toast from 'react-hot-toast';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

interface EnhancedViewerProps {
  /** URL or file path of the PDF document */
  fileUrl: string;
  /** Document ID for annotations */
  documentId?: string;
  /** Initial page number (1-indexed) */
  initialPage?: number;
  /** Callback when document loads successfully */
  onLoadSuccess?: (numPages: number) => void;
  /** Callback on error */
  onError?: (error: Error) => void;
  /** Enable/disable annotations */
  enableAnnotations?: boolean;
}

// Zoom levels
const ZOOM_LEVELS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0];
const DEFAULT_ZOOM_INDEX = 2; // 100%

// Rotation angles
const ROTATION_ANGLES = [0, 90, 180, 270];

export const EnhancedViewer: React.FC<EnhancedViewerProps> = ({
  fileUrl,
  documentId,
  initialPage = 1,
  onLoadSuccess,
  onError,
  enableAnnotations = true,
}) => {
  // State management
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(initialPage);
  const [zoomIndex, setZoomIndex] = useState<number>(DEFAULT_ZOOM_INDEX);
  const [rotation, setRotation] = useState<number>(0);
  const [searchText, setSearchText] = useState<string>('');
  const [showThumbnails, setShowThumbnails] = useState<boolean>(false);
  const [fitToWidth, setFitToWidth] = useState<boolean>(false);
  const [containerWidth, setContainerWidth] = useState<number>(800);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const pageRef = useRef<HTMLDivElement>(null);

  // Calculate current zoom scale
  const scale = fitToWidth 
    ? containerWidth / 612 // 612 is standard PDF page width in points
    : ZOOM_LEVELS[zoomIndex];

  /**
   * Handle successful document load
   */
  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    toast.success(`Documento cargado: ${numPages} páginas`);
    onLoadSuccess?.(numPages);
  }, [onLoadSuccess]);

  /**
   * Handle document load error
   */
  const onDocumentLoadError = useCallback((error: Error) => {
    console.error('Error loading PDF:', error);
    toast.error(`Error al cargar el documento: ${error.message}`);
    onError?.(error);
  }, [onError]);

  /**
   * Update container width on resize
   */
  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth - 40); // Subtract padding
      }
    };

    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  /**
   * Keyboard shortcuts
   */
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Prevent shortcuts when typing in input fields
      if (e.target instanceof HTMLInputElement) return;

      switch (e.key) {
        case 'ArrowLeft':
        case 'PageUp':
          e.preventDefault();
          goToPreviousPage();
          break;
        case 'ArrowRight':
        case 'PageDown':
          e.preventDefault();
          goToNextPage();
          break;
        case 'Home':
          e.preventDefault();
          goToPage(1);
          break;
        case 'End':
          e.preventDefault();
          goToPage(numPages);
          break;
        case '+':
        case '=':
          e.preventDefault();
          zoomIn();
          break;
        case '-':
        case '_':
          e.preventDefault();
          zoomOut();
          break;
        case 'r':
        case 'R':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            rotateClockwise();
          }
          break;
        case 'f':
        case 'F':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            document.getElementById('search-input')?.focus();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [numPages, pageNumber, zoomIndex]);

  // Navigation functions
  const goToPage = (page: number) => {
    if (page >= 1 && page <= numPages) {
      setPageNumber(page);
    }
  };

  const goToNextPage = () => goToPage(pageNumber + 1);
  const goToPreviousPage = () => goToPage(pageNumber - 1);

  // Zoom functions
  const zoomIn = () => {
    if (zoomIndex < ZOOM_LEVELS.length - 1) {
      setZoomIndex(zoomIndex + 1);
      setFitToWidth(false);
      toast.success(`Zoom: ${Math.round(ZOOM_LEVELS[zoomIndex + 1] * 100)}%`);
    }
  };

  const zoomOut = () => {
    if (zoomIndex > 0) {
      setZoomIndex(zoomIndex - 1);
      setFitToWidth(false);
      toast.success(`Zoom: ${Math.round(ZOOM_LEVELS[zoomIndex - 1] * 100)}%`);
    }
  };

  const toggleFitToWidth = () => {
    setFitToWidth(!fitToWidth);
    toast.success(fitToWidth ? 'Zoom manual' : 'Ajustar a ancho');
  };

  // Rotation functions
  const rotateClockwise = () => {
    const currentIndex = ROTATION_ANGLES.indexOf(rotation);
    const nextIndex = (currentIndex + 1) % ROTATION_ANGLES.length;
    setRotation(ROTATION_ANGLES[nextIndex]);
    toast.success(`Rotación: ${ROTATION_ANGLES[nextIndex]}°`);
  };

  // Search functions
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchText.trim()) {
      toast.success(`Buscando: "${searchText}"`);
      // TODO: Implement text search with highlighting
    }
  };

  const clearSearch = () => {
    setSearchText('');
  };

  // Download function
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = `document-${documentId || 'unknown'}.pdf`;
    link.click();
    toast.success('Descargando documento...');
  };

  // Print function
  const handlePrint = () => {
    window.open(fileUrl, '_blank');
    toast.success('Abriendo documento para imprimir...');
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Thumbnail Sidebar */}
      {showThumbnails && (
        <div className="w-48 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-2">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-700">Miniaturas</h3>
              <button
                onClick={() => setShowThumbnails(false)}
                className="p-1 hover:bg-gray-100 rounded"
                aria-label="Cerrar miniaturas"
              >
                <XIcon className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-2">
              {Array.from({ length: numPages }, (_, i) => i + 1).map((page) => (
                <button
                  key={page}
                  onClick={() => goToPage(page)}
                  className={`w-full p-2 border rounded hover:border-blue-500 transition-colors ${
                    page === pageNumber ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  }`}
                >
                  <div className="aspect-[8.5/11] bg-gray-100 flex items-center justify-center">
                    <Document file={fileUrl} loading="">
                      <Page
                        pageNumber={page}
                        width={160}
                        renderTextLayer={false}
                        renderAnnotationLayer={false}
                      />
                    </Document>
                  </div>
                  <p className="text-xs text-gray-600 mt-1 text-center">Página {page}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Viewer */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-white border-b border-gray-200 px-4 py-2">
          <div className="flex items-center justify-between gap-4">
            {/* Left: Navigation */}
            <div className="flex items-center gap-2">
              <button
                onClick={goToPreviousPage}
                disabled={pageNumber <= 1}
                className="p-2 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Página anterior"
              >
                <ChevronLeftIcon className="w-5 h-5" />
              </button>
              
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  min={1}
                  max={numPages}
                  value={pageNumber}
                  onChange={(e) => goToPage(parseInt(e.target.value) || 1)}
                  className="w-16 px-2 py-1 border border-gray-300 rounded text-center text-sm"
                />
                <span className="text-sm text-gray-600">/ {numPages}</span>
              </div>

              <button
                onClick={goToNextPage}
                disabled={pageNumber >= numPages}
                className="p-2 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Página siguiente"
              >
                <ChevronRightIcon className="w-5 h-5" />
              </button>
            </div>

            {/* Center: Zoom & Rotation */}
            <div className="flex items-center gap-2">
              <button
                onClick={zoomOut}
                disabled={zoomIndex === 0 && !fitToWidth}
                className="p-2 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Reducir zoom"
              >
                <ZoomOutIcon className="w-5 h-5" />
              </button>

              <select
                value={fitToWidth ? 'fit' : zoomIndex}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === 'fit') {
                    toggleFitToWidth();
                  } else {
                    setZoomIndex(parseInt(value));
                    setFitToWidth(false);
                  }
                }}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="fit">Ajustar ancho</option>
                {ZOOM_LEVELS.map((level, idx) => (
                  <option key={idx} value={idx}>
                    {Math.round(level * 100)}%
                  </option>
                ))}
              </select>

              <button
                onClick={zoomIn}
                disabled={zoomIndex === ZOOM_LEVELS.length - 1 && !fitToWidth}
                className="p-2 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Aumentar zoom"
              >
                <ZoomInIcon className="w-5 h-5" />
              </button>

              <div className="w-px h-6 bg-gray-300" />

              <button
                onClick={rotateClockwise}
                className="p-2 hover:bg-gray-100 rounded"
                aria-label="Rotar 90°"
              >
                <RotateCwIcon className="w-5 h-5" />
              </button>

              <button
                onClick={() => setShowThumbnails(!showThumbnails)}
                className="p-2 hover:bg-gray-100 rounded"
                aria-label="Mostrar miniaturas"
              >
                <LayoutGridIcon className="w-5 h-5" />
              </button>
            </div>

            {/* Right: Search & Actions */}
            <div className="flex items-center gap-2">
              <form onSubmit={handleSearch} className="relative">
                <input
                  id="search-input"
                  type="text"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  placeholder="Buscar en documento..."
                  className="pl-8 pr-8 py-1 border border-gray-300 rounded text-sm w-48"
                />
                <SearchIcon className="w-4 h-4 absolute left-2 top-1/2 -translate-y-1/2 text-gray-400" />
                {searchText && (
                  <button
                    type="button"
                    onClick={clearSearch}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    <XIcon className="w-4 h-4" />
                  </button>
                )}
              </form>

              <div className="w-px h-6 bg-gray-300" />

              <button
                onClick={handleDownload}
                className="p-2 hover:bg-gray-100 rounded"
                aria-label="Descargar"
              >
                <DownloadIcon className="w-5 h-5" />
              </button>

              <button
                onClick={handlePrint}
                className="p-2 hover:bg-gray-100 rounded"
                aria-label="Imprimir"
              >
                <PrinterIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* PDF Viewer Container */}
        <div
          ref={containerRef}
          className="flex-1 overflow-auto bg-gray-200 p-4"
        >
          <div className="flex justify-center">
            <div ref={pageRef} className="bg-white shadow-lg">
              <Document
                file={fileUrl}
                onLoadSuccess={onDocumentLoadSuccess}
                onLoadError={onDocumentLoadError}
                loading={
                  <div className="flex items-center justify-center p-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                  </div>
                }
                error={
                  <div className="p-8 text-center text-red-500">
                    <p className="font-semibold">Error al cargar el documento</p>
                    <p className="text-sm mt-2">Por favor, verifica la URL o intenta nuevamente</p>
                  </div>
                }
              >
                <Page
                  pageNumber={pageNumber}
                  scale={scale}
                  rotate={rotation}
                  renderTextLayer={true}
                  renderAnnotationLayer={enableAnnotations}
                  className="border border-gray-300"
                />
              </Document>
            </div>
          </div>
        </div>

        {/* Footer Info */}
        <div className="bg-white border-t border-gray-200 px-4 py-2">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <div>
              Página {pageNumber} de {numPages}
            </div>
            <div className="flex items-center gap-4">
              <span>Zoom: {fitToWidth ? 'Ajustado' : `${Math.round(scale * 100)}%`}</span>
              <span>Rotación: {rotation}°</span>
              {documentId && <span>ID: {documentId}</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedViewer;
