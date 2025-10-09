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
    <div className="container mx-auto p-6 space-y-6" style={{ maxWidth: '1200px' }}>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">🧪 Generador de Datos Sintéticos</h1>
        <p className="text-gray-600">
          Genera documentos de prueba para desarrollo y testing
        </p>
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

                  <button
                    onClick={() => deleteTask(task.task_id)}
                    className="text-xs text-red-600 hover:text-red-800 flex items-center gap-1"
                  >
                    🗑️ Eliminar
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
