/**
 * Document Viewer Page
 * 
 * Example page showing how to use the Enhanced Document Viewer
 */

import React, { useState } from 'react';
import { EnhancedViewer } from '../components/DocumentViewer';
import { FileTextIcon, UploadIcon } from 'lucide-react';

export const DocumentViewerPage: React.FC = () => {
  // Example PDF URLs (can be from API, upload, or sample)
  const [currentPdfUrl, setCurrentPdfUrl] = useState<string>(
    // Sample PDF from Mozilla (for testing)
    'https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf'
  );
  const [documentId, setDocumentId] = useState<string>('sample-doc-1');

  // Handle custom PDF URL
  const [customUrl, setCustomUrl] = useState<string>('');

  const handleLoadCustomUrl = () => {
    if (customUrl.trim()) {
      setCurrentPdfUrl(customUrl);
      setDocumentId(`custom-${Date.now()}`);
    }
  };

  // Handle file upload
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      const url = URL.createObjectURL(file);
      setCurrentPdfUrl(url);
      setDocumentId(`upload-${Date.now()}`);
    }
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileTextIcon className="w-6 h-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">
              Enhanced Document Viewer
            </h1>
          </div>

          <div className="flex items-center gap-4">
            {/* Custom URL Input */}
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={customUrl}
                onChange={(e) => setCustomUrl(e.target.value)}
                placeholder="https://example.com/document.pdf"
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-80"
                onKeyPress={(e) => e.key === 'Enter' && handleLoadCustomUrl()}
              />
              <button
                onClick={handleLoadCustomUrl}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Cargar URL
              </button>
            </div>

            {/* File Upload */}
            <label className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors cursor-pointer text-sm font-medium">
              <UploadIcon className="w-4 h-4" />
              <span>Subir PDF</span>
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
          </div>
        </div>

        {/* Quick Links */}
        <div className="mt-4 flex gap-2">
          <button
            onClick={() => {
              setCurrentPdfUrl('https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf');
              setDocumentId('sample-1');
            }}
            className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
          >
            📄 Sample 1: Mozilla PDF.js
          </button>
          <button
            onClick={() => {
              setCurrentPdfUrl('https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf');
              setDocumentId('sample-2');
            }}
            className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
          >
            📄 Sample 2: W3C Test PDF
          </button>
        </div>
      </div>

      {/* Enhanced Viewer */}
      <div className="flex-1">
        <EnhancedViewer
          fileUrl={currentPdfUrl}
          documentId={documentId}
          initialPage={1}
          enableAnnotations={true}
          onLoadSuccess={(numPages) => {
            console.log(`Document loaded successfully: ${numPages} pages`);
          }}
          onError={(error) => {
            console.error('Document load error:', error);
          }}
        />
      </div>
    </div>
  );
};

export default DocumentViewerPage;
