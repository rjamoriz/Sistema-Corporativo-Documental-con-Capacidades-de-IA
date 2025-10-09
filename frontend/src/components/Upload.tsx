import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { CloudArrowUpIcon, DocumentIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { documentsApi } from '@/lib/api-client';
import { useAuthStore } from '@/store/authStore';
import { useUploadStore } from '@/store/uploadStore';
import toast from 'react-hot-toast';

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/msword': ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/vnd.ms-excel': ['.xls'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'text/plain': ['.txt'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/tiff': ['.tif', '.tiff'],
};

interface UploadItemProps {
  id: string;
  file: File;
  progress: number;
  status: string;
  error?: string;
  onRemove: (id: string) => void;
}

const UploadItem: React.FC<UploadItemProps> = ({ id, file, progress, status, error, onRemove }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      case 'uploading':
      case 'processing':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'Pendiente';
      case 'uploading':
        return `Subiendo... ${progress}%`;
      case 'processing':
        return 'Procesando...';
      case 'completed':
        return 'Completado';
      case 'failed':
        return 'Error';
      default:
        return 'Desconocido';
    }
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <DocumentIcon className="w-8 h-8 text-gray-400 flex-shrink-0" />
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className={`text-xs ${getStatusColor()}`}>{getStatusText()}</span>
          <span className="text-xs text-gray-500">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </span>
        </div>
        
        {status === 'uploading' && (
          <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
            <div
              className="bg-blue-600 h-1.5 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
        
        {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
      </div>
      
      {(status === 'completed' || status === 'failed') && (
        <button
          onClick={() => onRemove(id)}
          className="flex-shrink-0 p-1 hover:bg-gray-200 rounded transition-colors"
        >
          <XMarkIcon className="w-5 h-5 text-gray-500" />
        </button>
      )}
    </div>
  );
};

export const UploadComponent: React.FC = () => {
  const { user } = useAuthStore();
  const { uploads, addUpload, updateUpload, removeUpload, clearCompleted } = useUploadStore();
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = useCallback(async (files: File[]) => {
    if (!user) {
      toast.error('Debe iniciar sesión para subir documentos');
      return;
    }

    setIsUploading(true);

    for (const file of files) {
      const uploadId = `${file.name}-${Date.now()}`;
      
      // Validate file
      if (file.size > MAX_FILE_SIZE) {
        toast.error(`${file.name}: Archivo demasiado grande (máx. 50MB)`);
        continue;
      }

      // Add to upload queue
      addUpload(uploadId, {
        file,
        progress: 0,
        status: 'uploading',
      });

      try {
        // Simulate progress for better UX
        const progressInterval = setInterval(() => {
          updateUpload(uploadId, {
            progress: Math.min(90, (uploads[uploadId]?.progress || 0) + 10),
          });
        }, 200);

        const document = await documentsApi.uploadDocument(file, user.id);

        clearInterval(progressInterval);

        updateUpload(uploadId, {
          progress: 100,
          status: 'completed',
          documentId: document.id,
        });

        toast.success(`${file.name} subido correctamente`);
      } catch (error) {
        updateUpload(uploadId, {
          status: 'failed',
          error: error instanceof Error ? error.message : 'Error desconocido',
        });
        toast.error(`Error al subir ${file.name}`);
      }
    }

    setIsUploading(false);
  }, [user, uploads, addUpload, updateUpload]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    handleUpload(acceptedFiles);
  }, [handleUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: MAX_FILE_SIZE,
    disabled: isUploading,
  });

  const uploadList = Object.entries(uploads);

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Subir Documentos</h2>
        
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
            transition-colors
            ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'}
            ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <CloudArrowUpIcon className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          
          {isDragActive ? (
            <p className="text-lg text-primary-600 font-medium">
              Suelta los archivos aquí...
            </p>
          ) : (
            <>
              <p className="text-lg text-gray-700 font-medium mb-2">
                Arrastra archivos aquí o haz clic para seleccionar
              </p>
              <p className="text-sm text-gray-500">
                Formatos soportados: PDF, Word, Excel, TXT, Imágenes (PNG, JPG, TIFF)
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Tamaño máximo: 50 MB por archivo
              </p>
            </>
          )}
        </div>
      </div>

      {uploadList.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Archivos en cola ({uploadList.length})
            </h3>
            {uploadList.some(([_, u]) => u.status === 'completed') && (
              <button
                onClick={clearCompleted}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Limpiar completados
              </button>
            )}
          </div>
          
          <div className="space-y-3">
            {uploadList.map(([id, upload]) => (
              <UploadItem
                key={id}
                id={id}
                file={upload.file}
                progress={upload.progress}
                status={upload.status}
                error={upload.error}
                onRemove={removeUpload}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
