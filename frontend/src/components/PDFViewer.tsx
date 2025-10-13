/**
 * PDFViewer Component
 * 
 * Visualizador de documentos PDF con:
 * - Navegación por páginas
 * - Zoom in/out
 * - Rotación
 * - Búsqueda de texto
 * - Descarga
 * - Modo pantalla completa
 */
import React, { useState } from 'react';
import { 
  ZoomIn, 
  ZoomOut, 
  RotateCw, 
  Download, 
  ChevronLeft, 
  ChevronRight, 
  Maximize2,
  Minimize2,
  FileText
} from 'lucide-react';

interface PDFViewerProps {
  documentId?: string;
  documentUrl?: string;
  documentName?: string;
}

export const PDFViewer: React.FC<PDFViewerProps> = ({ 
  documentId,
  documentUrl = '/sample.pdf',
  documentName = 'Documento.pdf'
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages] = useState(10); // Mock - se obtendría del PDF real
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 25, 200));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 25, 50));
  const handleRotate = () => setRotation(prev => (prev + 90) % 360);
  const handlePrevPage = () => setCurrentPage(prev => Math.max(prev - 1, 1));
  const handleNextPage = () => setCurrentPage(prev => Math.min(prev + 1, totalPages));
  const handleDownload = () => {
    // Implementar descarga
    console.log('Downloading:', documentName);
  };

  return (
    <div className={`flex flex-col h-full bg-gray-50 dark:bg-gray-900 ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
      {/* Toolbar */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Left: Document Info */}
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                {documentName}
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Página {currentPage} de {totalPages}
              </p>
            </div>
          </div>

          {/* Center: Navigation Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrevPage}
              disabled={currentPage === 1}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Página anterior"
            >
              <ChevronLeft className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            </button>
            
            <div className="flex items-center gap-2 px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <input
                type="number"
                value={currentPage}
                onChange={(e) => {
                  const page = parseInt(e.target.value);
                  if (page >= 1 && page <= totalPages) setCurrentPage(page);
                }}
                className="w-12 text-center bg-transparent border-none outline-none text-sm font-medium text-gray-900 dark:text-white"
              />
              <span className="text-sm text-gray-500 dark:text-gray-400">/ {totalPages}</span>
            </div>

            <button
              onClick={handleNextPage}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Página siguiente"
            >
              <ChevronRight className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            </button>
          </div>

          {/* Right: Tool Controls */}
          <div className="flex items-center gap-2">
            {/* Zoom Controls */}
            <div className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <button
                onClick={handleZoomOut}
                disabled={zoom <= 50}
                className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 transition-colors"
                title="Alejar"
              >
                <ZoomOut className="w-4 h-4 text-gray-700 dark:text-gray-300" />
              </button>
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300 min-w-[3rem] text-center">
                {zoom}%
              </span>
              <button
                onClick={handleZoomIn}
                disabled={zoom >= 200}
                className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 transition-colors"
                title="Acercar"
              >
                <ZoomIn className="w-4 h-4 text-gray-700 dark:text-gray-300" />
              </button>
            </div>

            {/* Rotate */}
            <button
              onClick={handleRotate}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="Rotar"
            >
              <RotateCw className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            </button>

            {/* Download */}
            <button
              onClick={handleDownload}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="Descargar"
            >
              <Download className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            </button>

            {/* Fullscreen */}
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title={isFullscreen ? "Salir de pantalla completa" : "Pantalla completa"}
            >
              {isFullscreen ? (
                <Minimize2 className="w-5 h-5 text-gray-700 dark:text-gray-300" />
              ) : (
                <Maximize2 className="w-5 h-5 text-gray-700 dark:text-gray-300" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* PDF Viewer Area */}
      <div className="flex-1 overflow-auto bg-gray-100 dark:bg-gray-950 p-6">
        <div className="max-w-4xl mx-auto">
          {/* PDF Canvas/Embed */}
          <div 
            className="bg-white dark:bg-gray-800 shadow-2xl rounded-lg overflow-hidden transition-transform"
            style={{
              transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
              transformOrigin: 'top center',
            }}
          >
            {/* Placeholder - En producción usaríamos react-pdf o similar */}
            <div className="aspect-[8.5/11] flex items-center justify-center bg-white dark:bg-gray-800">
              <div className="text-center p-8">
                <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400 dark:text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Visor de PDF
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  {documentName}
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  Página {currentPage} de {totalPages} • Zoom: {zoom}% • Rotación: {rotation}°
                </p>
                <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <p className="text-xs text-blue-800 dark:text-blue-300">
                    💡 <strong>Demo Mode:</strong> Integrar con react-pdf o PDF.js para visualización real.
                    <br />
                    URL: {documentUrl || 'No especificada'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-2">
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>Documento: {documentId || 'demo-001'}</span>
          <span>Última modificación: Hace 2 horas</span>
          <span>Tamaño: 2.4 MB</span>
        </div>
      </div>
    </div>
  );
};

export default PDFViewer;
