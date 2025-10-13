/**
 * Document Comparison Page
 * 
 * Example page for comparing two document versions
 */

import React, { useState } from 'react';
import { DocumentComparison } from '../components/DocumentViewer/DocumentComparison';
import { FileTextIcon, PlusIcon } from 'lucide-react';

interface DocumentVersion {
  id: string;
  url: string;
  version: number;
  createdAt: Date;
  createdBy: string;
  description?: string;
}

export const DocumentComparisonPage: React.FC = () => {
  // Sample document versions
  const [leftDoc, setLeftDoc] = useState<DocumentVersion>({
    id: 'doc-v1',
    url: 'https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf',
    version: 1,
    createdAt: new Date('2025-01-01'),
    createdBy: 'Juan Pérez',
    description: 'Versión inicial del documento',
  });

  const [rightDoc, setRightDoc] = useState<DocumentVersion>({
    id: 'doc-v2',
    url: 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
    version: 2,
    createdAt: new Date('2025-10-10'),
    createdBy: 'María García',
    description: 'Versión actualizada con correcciones',
  });

  const [showComparison, setShowComparison] = useState(true);
  const [customLeftUrl, setCustomLeftUrl] = useState('');
  const [customRightUrl, setCustomRightUrl] = useState('');

  const handleLoadCustomUrls = () => {
    if (customLeftUrl.trim() && customRightUrl.trim()) {
      setLeftDoc({
        id: `custom-left-${Date.now()}`,
        url: customLeftUrl,
        version: 1,
        createdAt: new Date(),
        createdBy: 'Usuario',
        description: 'Documento personalizado',
      });
      setRightDoc({
        id: `custom-right-${Date.now()}`,
        url: customRightUrl,
        version: 2,
        createdAt: new Date(),
        createdBy: 'Usuario',
        description: 'Documento personalizado modificado',
      });
      setShowComparison(true);
    }
  };

  // Handle file uploads
  const handleFileUpload = (side: 'left' | 'right') => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      const url = URL.createObjectURL(file);
      const doc: DocumentVersion = {
        id: `upload-${side}-${Date.now()}`,
        url,
        version: side === 'left' ? 1 : 2,
        createdAt: new Date(),
        createdBy: 'Usuario',
        description: `Archivo subido: ${file.name}`,
      };
      
      if (side === 'left') {
        setLeftDoc(doc);
      } else {
        setRightDoc(doc);
      }
      setShowComparison(true);
    }
  };

  if (!showComparison) {
    return (
      <div className="h-screen flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center gap-3">
            <FileTextIcon className="w-6 h-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">
              Comparación de Documentos
            </h1>
          </div>
        </div>

        {/* Configuration Panel */}
        <div className="flex-1 bg-gray-100 p-8 flex items-center justify-center">
          <div className="max-w-4xl w-full bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              Selecciona dos documentos para comparar
            </h2>

            {/* URL Inputs */}
            <div className="grid grid-cols-2 gap-6 mb-8">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Documento Original (Izquierda)
                </label>
                <input
                  type="text"
                  value={customLeftUrl}
                  onChange={(e) => setCustomLeftUrl(e.target.value)}
                  placeholder="https://example.com/document-v1.pdf"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Documento Modificado (Derecha)
                </label>
                <input
                  type="text"
                  value={customRightUrl}
                  onChange={(e) => setCustomRightUrl(e.target.value)}
                  placeholder="https://example.com/document-v2.pdf"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>

            <button
              onClick={handleLoadCustomUrls}
              disabled={!customLeftUrl.trim() || !customRightUrl.trim()}
              className="w-full mb-8 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              Cargar y Comparar
            </button>

            {/* File Uploads */}
            <div className="border-t border-gray-200 pt-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                O sube archivos locales
              </h3>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block w-full px-6 py-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition-colors cursor-pointer">
                    <div className="text-center">
                      <PlusIcon className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        Subir Documento Original
                      </span>
                    </div>
                    <input
                      type="file"
                      accept="application/pdf"
                      onChange={handleFileUpload('left')}
                      className="hidden"
                    />
                  </label>
                </div>
                <div>
                  <label className="block w-full px-6 py-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 transition-colors cursor-pointer">
                    <div className="text-center">
                      <PlusIcon className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        Subir Documento Modificado
                      </span>
                    </div>
                    <input
                      type="file"
                      accept="application/pdf"
                      onChange={handleFileUpload('right')}
                      className="hidden"
                    />
                  </label>
                </div>
              </div>
            </div>

            {/* Quick Examples */}
            <div className="mt-8 pt-8 border-t border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Ejemplos rápidos
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => setShowComparison(true)}
                  className="w-full px-4 py-2 text-left bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors"
                >
                  <span className="font-medium text-gray-900">
                    Ejemplo 1:
                  </span>
                  <span className="text-gray-600 ml-2">
                    Mozilla PDF.js vs W3C Test PDF
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <DocumentComparison
      leftDocument={leftDoc}
      rightDocument={rightDoc}
      onComparisonComplete={(differences) => {
        console.log(`Comparison complete: ${differences} differences found`);
      }}
      onError={(error) => {
        console.error('Comparison error:', error);
      }}
    />
  );
};

export default DocumentComparisonPage;
