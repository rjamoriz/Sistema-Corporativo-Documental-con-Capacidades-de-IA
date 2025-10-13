import React, { useState, useEffect } from 'react';

interface Template {
  id: string;
  name: string;
  description: string;
  categories: Record<string, string>;
}

interface GenerationTask {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  documents_generated: number;
  total_documents: number;
  created_at: string;
  output_path?: string;
  error?: string;
  documents_uploaded?: number;
  generated_files?: SyntheticFile[];
}

interface SyntheticFile {
  filename: string;
  category: string;
  size: number;
  created_at: string;
  metadata: {
    entities: string[];
    chunks: number;
    risk_level: string;
  };
  preview_text: string;
}

interface EmbeddingData {
  text: string;
  embedding: number[];
  dimension: number;
  model: string;
}

export default function AdminSyntheticData() {
  // State
  const [count, setCount] = useState(50);
  const [selectedTemplate, setSelectedTemplate] = useState('default');
  const [autoUpload, setAutoUpload] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [currentTask, setCurrentTask] = useState<GenerationTask | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [previewDist, setPreviewDist] = useState<any>(null);
  const [tasks, setTasks] = useState<GenerationTask[]>([]);
  
  // Nuevos estados para visualización de archivos y vectorización
  const [selectedFile, setSelectedFile] = useState<SyntheticFile | null>(null);
  const [showFileViewer, setShowFileViewer] = useState(false);
  const [openaiApiKey, setOpenaiApiKey] = useState(localStorage.getItem('openai_api_key') || '');
  const [showVectorization, setShowVectorization] = useState(false);
  const [vectorizingText, setVectorizingText] = useState('');
  const [embeddingResult, setEmbeddingResult] = useState<EmbeddingData | null>(null);
  const [vectorizing, setVectorizing] = useState(false);
  const [activeTab, setActiveTab] = useState<'generation' | 'files' | 'vectorization'>('generation');
  const [syntheticFiles, setSyntheticFiles] = useState<SyntheticFile[]>([]);

  // Cargar templates al montar
  useEffect(() => {
    loadTemplates();
    loadTasks();
  }, []);

  // Poll status mientras genera
  useEffect(() => {
    if (!currentTask || currentTask.status === 'completed' || currentTask.status === 'failed') {
      return;
    }

    const interval = setInterval(() => {
      pollTaskStatus(currentTask.task_id);
    }, 2000);

    return () => clearInterval(interval);
  }, [currentTask]);

  // Funciones API
  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/v1/synthetic/templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const loadTasks = async () => {
    try {
      const response = await fetch('/api/v1/synthetic/tasks', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTasks(data);
      }
    } catch (error) {
      console.error('Error loading tasks:', error);
    }
  };

  const previewDistribution = async () => {
    try {
      const response = await fetch(
        `/api/v1/synthetic/preview-distribution?template_id=${selectedTemplate}&total_documents=${count}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPreviewDist(data);
      }
    } catch (error) {
      console.error('Error previewing distribution:', error);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);

    try {
      const response = await fetch('/api/v1/synthetic/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          total_documents: count,
          template_id: selectedTemplate,
          auto_upload: autoUpload
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentTask({
          task_id: data.task_id,
          status: 'pending',
          progress: 0,
          documents_generated: 0,
          total_documents: data.total_documents,
          created_at: new Date().toISOString()
        });
        
        // Recargar lista de tareas
        loadTasks();
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        setGenerating(false);
      }
    } catch (error) {
      console.error('Error generating:', error);
      alert('Error al iniciar generación');
      setGenerating(false);
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    try {
      const response = await fetch(`/api/v1/synthetic/status/${taskId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentTask(data);

        if (data.status === 'completed') {
          setGenerating(false);
          loadTasks();
          alert(`✅ ${data.documents_generated} documentos generados correctamente!`);
        } else if (data.status === 'failed') {
          setGenerating(false);
          alert(`❌ Error: ${data.error}`);
        }
      }
    } catch (error) {
      console.error('Error polling status:', error);
    }
  };

  const deleteTask = async (taskId: string) => {
    if (!confirm('¿Eliminar esta tarea?')) return;

    try {
      const response = await fetch(`/api/v1/synthetic/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        loadTasks();
      }
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  // Nueva función: Cargar archivos sintéticos generados
  const loadSyntheticFiles = async (taskId: string) => {
    try {
      const response = await fetch(`/api/v1/synthetic/tasks/${taskId}/files`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        return data.files;
      }
    } catch (error) {
      console.error('Error loading files:', error);
    }
    return [];
  };

  // Nueva función: Vectorizar texto con OpenAI
  const vectorizeText = async () => {
    if (!openaiApiKey) {
      alert('Por favor, configura tu API Key de OpenAI');
      return;
    }

    if (!vectorizingText.trim()) {
      alert('Por favor, ingresa un texto para vectorizar');
      return;
    }

    setVectorizing(true);

    try {
      const response = await fetch('https://api.openai.com/v1/embeddings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${openaiApiKey}`
        },
        body: JSON.stringify({
          input: vectorizingText,
          model: 'text-embedding-3-small'
        })
      });

      if (response.ok) {
        const data = await response.json();
        const embedding = data.data[0].embedding;
        
        setEmbeddingResult({
          text: vectorizingText,
          embedding: embedding,
          dimension: embedding.length,
          model: data.model
        });

        // Guardar API key para próximas sesiones
        localStorage.setItem('openai_api_key', openaiApiKey);
      } else {
        const error = await response.json();
        alert(`Error de OpenAI: ${error.error?.message || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error('Error vectorizing:', error);
      alert('Error al vectorizar el texto');
    } finally {
      setVectorizing(false);
    }
  };

  // Función para visualizar archivo
  const viewFile = async (task: GenerationTask) => {
    const files = await loadSyntheticFiles(task.task_id);
    if (files && files.length > 0) {
      setSyntheticFiles(files);
      setSelectedFile(files[0]);
      setActiveTab('files');
    } else {
      alert('No se encontraron archivos para esta tarea');
    }
  };

  // Preview distribution cuando cambia template o count
  useEffect(() => {
    if (selectedTemplate && count > 0) {
      previewDistribution();
    }
  }, [selectedTemplate, count]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      case 'running':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100';
      case 'failed':
        return 'bg-red-100';
      case 'running':
        return 'bg-blue-100';
      default:
        return 'bg-gray-100';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6" style={{ maxWidth: '1400px' }}>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">🧪 Generador de Datos Sintéticos</h1>
        <p className="text-gray-600">
          Genera documentos de prueba, visualiza su estructura y vectoriza con OpenAI
        </p>
      </div>

      {/* Tabs de navegación */}
      <div className="flex gap-2 border-b mb-6">
        <button
          onClick={() => setActiveTab('generation')}
          className={`px-6 py-3 font-medium border-b-2 transition ${
            activeTab === 'generation'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-blue-600'
          }`}
        >
          📄 Generación
        </button>
        <button
          onClick={() => setActiveTab('files')}
          className={`px-6 py-3 font-medium border-b-2 transition ${
            activeTab === 'files'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-blue-600'
          }`}
        >
          📁 Archivos Sintéticos
        </button>
        <button
          onClick={() => setActiveTab('vectorization')}
          className={`px-6 py-3 font-medium border-b-2 transition ${
            activeTab === 'vectorization'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-blue-600'
          }`}
        >
          🧬 Vectorización OpenAI
        </button>
      </div>

      {/* Warning Alert */}
      <div className="bg-red-50 border border-red-300 rounded-lg p-4 flex gap-3">
        <div className="text-red-600 text-xl">⚠️</div>
        <div>
          <p className="font-semibold text-red-900">Solo para entornos de desarrollo/staging</p>
          <p className="text-sm text-red-700">
            Esta funcionalidad está bloqueada en producción.
          </p>
        </div>
      </div>

      {/* TAB: Generación */}
      {activeTab === 'generation' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Panel de Configuración */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-2">Configuración de Generación</h2>
            <p className="text-gray-600 text-sm mb-6">
              Personaliza los documentos sintéticos a generar
            </p>

            <div className="space-y-6">
              {/* Cantidad */}
              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium">Cantidad de documentos</label>
                  <span className="text-sm font-bold">{count}</span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="500"
                  step="10"
                  value={count}
                  onChange={(e) => setCount(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Rango: 10-500 documentos (estimado: {(count * 0.5).toFixed(0)}s)
                </p>
              </div>

              {/* Template */}
              <div>
                <label className="text-sm font-medium block mb-2">
                  Template de Distribución
                </label>
                <select
                  value={selectedTemplate}
                  onChange={(e) => setSelectedTemplate(e.target.value)}
                  className="w-full p-2 border rounded-lg"
                >
                  {templates.map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </select>
                {templates.find(t => t.id === selectedTemplate) && (
                  <p className="text-xs text-gray-500 mt-1">
                    {templates.find(t => t.id === selectedTemplate)?.description}
                  </p>
                )}
              </div>

              {/* Auto Upload */}
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <label className="text-sm font-medium block">Subir automáticamente</label>
                  <p className="text-xs text-gray-500">
                    Los documentos se añadirán a la aplicación
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoUpload}
                    onChange={(e) => setAutoUpload(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              {/* Preview Distribution */}
              {previewDist && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium mb-3">Vista previa de distribución:</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {Object.entries(previewDist.distribution).map(([cat, count]) => (
                      <div key={cat} className="flex justify-between">
                        <span className="text-gray-600 capitalize">{cat}:</span>
                        <span className="font-medium">{count as number} ({previewDist.percentages[cat]})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Botón Generar */}
              <button
                onClick={handleGenerate}
                disabled={generating}
                className={`w-full py-3 px-4 rounded-lg font-medium flex items-center justify-center gap-2 ${
                  generating
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {generating ? (
                  <>
                    <span className="animate-spin">⟳</span>
                    Generando...
                  </>
                ) : (
                  <>
                    📄 Generar Documentos
                  </>
                )}
              </button>

              {/* Progreso Actual */}
              {currentTask && (currentTask.status === 'running' || currentTask.status === 'pending') && (
                <div className="p-4 border rounded-lg space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progreso:</span>
                    <span>{currentTask.documents_generated}/{currentTask.total_documents}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-blue-600 h-2.5 rounded-full transition-all"
                      style={{ width: `${currentTask.progress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 text-center">
                    {currentTask.progress}% completado
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Historial de Tareas */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-2">Historial de Generaciones</h2>
            <p className="text-gray-600 text-sm mb-6">
              Tareas recientes de generación de datos
            </p>

            {tasks.length === 0 ? (
              <div className="text-center text-gray-500 py-12">
                <p className="text-lg mb-2">📭</p>
                <p>No hay tareas aún.</p>
                <p className="text-sm">Genera tus primeros documentos.</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {tasks.map((task) => (
                  <div
                    key={task.task_id}
                    className="p-4 border rounded-lg space-y-2 hover:bg-gray-50 transition"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-medium">
                          {task.documents_generated} / {task.total_documents} documentos
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(task.created_at).toLocaleString()}
                        </p>
                      </div>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${getStatusBg(
                          task.status
                        )} ${getStatusColor(task.status)}`}
                      >
                        {task.status.toUpperCase()}
                      </span>
                    </div>

                    {task.status === 'running' && (
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${task.progress}%` }}
                        ></div>
                      </div>
                    )}

                    {task.status === 'completed' && task.documents_uploaded && (
                      <p className="text-xs text-green-600">
                        ✓ {task.documents_uploaded} documentos subidos
                      </p>
                    )}

                    {task.error && (
                      <p className="text-xs text-red-600">Error: {task.error}</p>
                    )}

                    <div className="flex gap-2">
                      {task.status === 'completed' && (
                        <button
                          onClick={() => viewFile(task)}
                          className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1"
                        >
                          📁 Ver Archivos
                        </button>
                      )}
                      <button
                        onClick={() => deleteTask(task.task_id)}
                        className="text-xs text-red-600 hover:text-red-800 flex items-center gap-1"
                      >
                        🗑️ Eliminar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB: Visualización de Archivos Sintéticos */}
      {activeTab === 'files' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lista de archivos */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">📁 Archivos Generados</h2>
            {syntheticFiles.length === 0 ? (
              <div className="text-center text-gray-500 py-12">
                <p className="text-lg mb-2">📂</p>
                <p>No hay archivos cargados</p>
                <p className="text-sm">Selecciona una tarea completada</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {syntheticFiles.map((file, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedFile(file)}
                    className={`w-full text-left p-3 rounded-lg border transition ${
                      selectedFile?.filename === file.filename
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <p className="text-sm font-medium truncate">{file.filename}</p>
                    <div className="flex gap-2 mt-1">
                      <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                        {file.category}
                      </span>
                      <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-700 rounded">
                        {(file.size / 1024).toFixed(1)} KB
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Visualizador de archivo */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
            {selectedFile ? (
              <div className="space-y-4">
                <div>
                  <h2 className="text-xl font-semibold mb-2">📄 {selectedFile.filename}</h2>
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full">
                      {selectedFile.category}
                    </span>
                    <span className="text-xs px-3 py-1 bg-purple-100 text-purple-700 rounded-full">
                      {selectedFile.metadata.risk_level} riesgo
                    </span>
                    <span className="text-xs px-3 py-1 bg-green-100 text-green-700 rounded-full">
                      {selectedFile.metadata.chunks} chunks
                    </span>
                    <span className="text-xs px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full">
                      {selectedFile.metadata.entities.length} entidades
                    </span>
                  </div>
                </div>

                {/* Metadata */}
                <div className="border-t pt-4">
                  <h3 className="font-semibold text-sm mb-2">📊 Metadata</h3>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-gray-600">Tamaño:</p>
                      <p className="font-medium">{(selectedFile.size / 1024).toFixed(2)} KB</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Fecha:</p>
                      <p className="font-medium">{new Date(selectedFile.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-gray-600 mb-1">Entidades detectadas:</p>
                      <div className="flex flex-wrap gap-1">
                        {selectedFile.metadata.entities.map((entity, idx) => (
                          <span key={idx} className="text-xs px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded">
                            {entity}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Preview del contenido */}
                <div className="border-t pt-4">
                  <h3 className="font-semibold text-sm mb-2">👁️ Vista previa</h3>
                  <div className="bg-gray-50 p-4 rounded-lg max-h-[400px] overflow-y-auto">
                    <pre className="text-xs font-mono whitespace-pre-wrap text-gray-700">
                      {selectedFile.preview_text}
                    </pre>
                  </div>
                </div>

                {/* Botón para vectorizar */}
                <div className="border-t pt-4">
                  <button
                    onClick={() => {
                      setVectorizingText(selectedFile.preview_text.substring(0, 500));
                      setActiveTab('vectorization');
                    }}
                    className="w-full py-2 px-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition flex items-center justify-center gap-2"
                  >
                    🧬 Vectorizar este documento
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-20">
                <p className="text-lg mb-2">📄</p>
                <p>Selecciona un archivo para ver detalles</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB: Vectorización con OpenAI */}
      {activeTab === 'vectorization' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Panel de configuración */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-2">🧬 Vectorización con OpenAI</h2>
            <p className="text-gray-600 text-sm mb-6">
              Genera embeddings usando el modelo de OpenAI
            </p>

            <div className="space-y-4">
              {/* API Key */}
              <div>
                <label className="text-sm font-medium block mb-2">
                  🔑 API Key de OpenAI
                </label>
                <input
                  type="password"
                  value={openaiApiKey}
                  onChange={(e) => setOpenaiApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full p-2 border rounded-lg"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Tu API key se guarda localmente en el navegador
                </p>
              </div>

              {/* Texto a vectorizar */}
              <div>
                <label className="text-sm font-medium block mb-2">
                  📝 Texto a vectorizar
                </label>
                <textarea
                  value={vectorizingText}
                  onChange={(e) => setVectorizingText(e.target.value)}
                  placeholder="Ingresa el texto que deseas convertir en embeddings..."
                  rows={8}
                  className="w-full p-3 border rounded-lg resize-none"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Caracteres: {vectorizingText.length} | Tokens estimados: {Math.ceil(vectorizingText.length / 4)}
                </p>
              </div>

              {/* Botón vectorizar */}
              <button
                onClick={vectorizeText}
                disabled={vectorizing || !openaiApiKey || !vectorizingText}
                className={`w-full py-3 px-4 rounded-lg font-medium flex items-center justify-center gap-2 ${
                  vectorizing || !openaiApiKey || !vectorizingText
                    ? 'bg-gray-400 cursor-not-allowed text-white'
                    : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700'
                }`}
              >
                {vectorizing ? (
                  <>
                    <span className="animate-spin">⟳</span>
                    Vectorizando...
                  </>
                ) : (
                  <>
                    🧬 Generar Embeddings
                  </>
                )}
              </button>

              {/* Info del modelo */}
              <div className="p-3 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
                <p className="text-xs font-medium text-purple-900 mb-1">📌 Modelo utilizado:</p>
                <p className="text-xs text-purple-700">
                  <strong>text-embedding-3-small</strong> (1536 dimensiones)
                </p>
                <p className="text-xs text-purple-600 mt-2">
                  Ideal para búsqueda semántica, clustering y análisis de similitud
                </p>
              </div>
            </div>
          </div>

          {/* Panel de resultados */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">📊 Resultados del Embedding</h2>

            {embeddingResult ? (
              <div className="space-y-4">
                {/* Métricas */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-xs text-blue-600 mb-1">Dimensiones</p>
                    <p className="text-2xl font-bold text-blue-900">{embeddingResult.dimension}</p>
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg">
                    <p className="text-xs text-green-600 mb-1">Modelo</p>
                    <p className="text-sm font-bold text-green-900">{embeddingResult.model}</p>
                  </div>
                </div>

                {/* Texto original */}
                <div>
                  <h3 className="text-sm font-semibold mb-2">📝 Texto original:</h3>
                  <div className="p-3 bg-gray-50 rounded-lg max-h-32 overflow-y-auto">
                    <p className="text-xs text-gray-700">{embeddingResult.text}</p>
                  </div>
                </div>

                {/* Vector (primeros valores) */}
                <div>
                  <h3 className="text-sm font-semibold mb-2">🔢 Vector (primeras 20 dimensiones):</h3>
                  <div className="p-3 bg-gray-900 rounded-lg max-h-48 overflow-y-auto">
                    <pre className="text-xs font-mono text-green-400">
                      {JSON.stringify(embeddingResult.embedding.slice(0, 20), null, 2)}
                    </pre>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Mostrando 20 de {embeddingResult.dimension} dimensiones
                  </p>
                </div>

                {/* Visualización de distribución */}
                <div>
                  <h3 className="text-sm font-semibold mb-2">📈 Distribución de valores:</h3>
                  <div className="p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                    <div className="space-y-1">
                      {[
                        { label: 'Min', value: Math.min(...embeddingResult.embedding).toFixed(4), color: 'text-red-600' },
                        { label: 'Max', value: Math.max(...embeddingResult.embedding).toFixed(4), color: 'text-green-600' },
                        { label: 'Media', value: (embeddingResult.embedding.reduce((a, b) => a + b) / embeddingResult.embedding.length).toFixed(4), color: 'text-blue-600' }
                      ].map(stat => (
                        <div key={stat.label} className="flex justify-between text-xs">
                          <span className="text-gray-600">{stat.label}:</span>
                          <span className={`font-mono font-bold ${stat.color}`}>{stat.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Mini gráfico de barras */}
                <div>
                  <h3 className="text-sm font-semibold mb-2">📊 Visualización (sample):</h3>
                  <div className="p-3 bg-gray-50 rounded-lg space-y-1">
                    {embeddingResult.embedding.slice(0, 15).map((val, idx) => {
                      const normalized = ((val + 1) / 2) * 100; // Normalizar de [-1,1] a [0,100]
                      return (
                        <div key={idx} className="flex items-center gap-2">
                          <span className="text-xs w-6 text-gray-500">{idx}</span>
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                              style={{ width: `${normalized}%` }}
                            />
                          </div>
                          <span className="text-xs font-mono w-16 text-right text-gray-700">
                            {val.toFixed(3)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Botones de acción */}
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(JSON.stringify(embeddingResult.embedding));
                      alert('✅ Vector copiado al portapapeles');
                    }}
                    className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
                  >
                    📋 Copiar Vector
                  </button>
                  <button
                    onClick={() => {
                      const data = JSON.stringify(embeddingResult, null, 2);
                      const blob = new Blob([data], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = 'embedding.json';
                      a.click();
                    }}
                    className="flex-1 py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm"
                  >
                    💾 Descargar JSON
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-20">
                <p className="text-4xl mb-4">🧬</p>
                <p className="text-lg mb-2">Sin embeddings generados</p>
                <p className="text-sm">Configura tu API key e ingresa un texto para vectorizar</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
