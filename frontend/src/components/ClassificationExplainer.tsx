/**
 * ClassificationExplainer Component
 * 
 * Visualización interactiva del pipeline de clasificación inteligente
 * - Muestra las 5 fases: Taxonomía → ML → Ontología → Validación → Riesgo
 * - Visualiza confianza y blending en cada fase
 * - Timeline con métricas de rendimiento
 * - Explicabilidad total del proceso
 */
import { useState } from 'react';
import { CheckCircle, AlertTriangle, TrendingUp, Clock, Zap, Brain, Shield } from 'lucide-react';

interface ClassificationPhase {
  name: string;
  icon: React.ReactNode;
  status: 'completed' | 'skipped' | 'pending';
  duration?: number;
  confidence?: number;
  data?: any;
}

interface ClassificationResult {
  category: string;
  confidence: number;
  method: string;
  phases_used: string[];
  classification_mode: string;
  
  // Taxonomía
  taxonomy_class?: string;
  taxonomy_label?: string;
  taxonomy_path?: string[];
  
  // ML
  ml_category?: string;
  ml_confidence?: number;
  
  // Ontología
  ontology_class?: string;
  ontology_label?: string;
  ontology_confidence?: number;
  matched_keywords?: string[];
  
  // Validación
  metadata_validation?: {
    is_valid: boolean;
    errors: string[];
    required_fields: string[];
  };
  
  // Riesgo
  inferred_risk_level?: string;
}

interface ClassificationExplainerProps {
  documentId?: string;
  result?: ClassificationResult;
  onModeChange?: (mode: string) => void;
}

const MODES = [
  {
    id: 'fast',
    name: 'Rápido',
    description: 'Solo taxonomía JSON (~10ms)',
    icon: '⚡',
    color: 'green'
  },
  {
    id: 'ml',
    name: 'Balanceado',
    description: 'Taxonomía + ML (~100ms)',
    icon: '🎯',
    color: 'blue'
  },
  {
    id: 'precise',
    name: 'Preciso',
    description: 'Taxonomía + ML + OWL (~500ms)',
    icon: '🔬',
    color: 'purple'
  },
  {
    id: 'intelligent',
    name: 'Inteligente',
    description: 'Adaptativo según confianza',
    icon: '🧠',
    color: 'indigo'
  }
];

export default function ClassificationExplainer({ 
  result,
  onModeChange
}: ClassificationExplainerProps) {
  const [selectedMode, setSelectedMode] = useState('intelligent');

  if (!result) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="text-center text-gray-400">
          <Brain className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg mb-2">Sin clasificación</p>
          <p className="text-sm">Sube un documento para ver el análisis del pipeline</p>
        </div>
      </div>
    );
  }

  const buildPhases = (): ClassificationPhase[] => {
    const phases: ClassificationPhase[] = [];
    const phasesUsed = new Set(result.phases_used || []);

    // Fase 1: Taxonomía (siempre se ejecuta)
    phases.push({
      name: 'Taxonomía JSON',
      icon: <Zap className="w-5 h-5" />,
      status: phasesUsed.has('taxonomy') ? 'completed' : 'pending',
      confidence: result.taxonomy_class ? 0.75 : undefined,
      duration: 10,
      data: {
        class: result.taxonomy_label,
        path: result.taxonomy_path
      }
    });

    // Fase 2: ML
    phases.push({
      name: 'ML Transformers',
      icon: <Brain className="w-5 h-5" />,
      status: phasesUsed.has('ml') ? 'completed' : 'skipped',
      confidence: result.ml_confidence,
      duration: phasesUsed.has('ml') ? 90 : undefined,
      data: {
        category: result.ml_category,
        method: result.method?.includes('transformer') ? 'BETO' : 'Pipeline'
      }
    });

    // Fase 3: Ontología
    phases.push({
      name: 'Ontología OWL',
      icon: <Shield className="w-5 h-5" />,
      status: phasesUsed.has('ontology') ? 'completed' : 'skipped',
      confidence: result.ontology_confidence,
      duration: phasesUsed.has('ontology') ? 400 : undefined,
      data: {
        class: result.ontology_label,
        keywords: result.matched_keywords
      }
    });

    // Fase 4: Validación
    phases.push({
      name: 'Validación OWL',
      icon: <CheckCircle className="w-5 h-5" />,
      status: result.metadata_validation ? 'completed' : 'skipped',
      data: result.metadata_validation
    });

    // Fase 5: Riesgo
    phases.push({
      name: 'Inferencia Riesgo',
      icon: <TrendingUp className="w-5 h-5" />,
      status: result.inferred_risk_level ? 'completed' : 'skipped',
      data: {
        level: result.inferred_risk_level
      }
    });

    return phases;
  };

  const phases = buildPhases();
  const totalTime = phases.reduce((sum, p) => sum + (p.duration || 0), 0);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-300';
      case 'skipped': return 'bg-gray-100 text-gray-600 border-gray-300';
      default: return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    }
  };

  const getRiskColor = (level?: string) => {
    switch (level?.toUpperCase()) {
      case 'ALTO': return 'bg-red-100 text-red-800 border-red-300';
      case 'MEDIO': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'BAJO': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-600 border-gray-300';
    }
  };

  const handleModeChange = (mode: string) => {
    setSelectedMode(mode);
    if (onModeChange) {
      onModeChange(mode);
    }
  };

  return (
    <div className="space-y-6">
      {/* Selectores de modo */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Modo de Clasificación</h3>
        <div className="grid grid-cols-4 gap-4">
          {MODES.map((mode) => (
            <button
              key={mode.id}
              onClick={() => handleModeChange(mode.id)}
              className={`p-4 border-2 rounded-lg text-left transition-all ${
                selectedMode === mode.id
                  ? `border-${mode.color}-500 bg-${mode.color}-50`
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-2">{mode.icon}</div>
              <div className="font-semibold mb-1">{mode.name}</div>
              <div className="text-xs text-gray-600">{mode.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Resumen de clasificación */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">Resultado Final</h3>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="w-4 h-4" />
            <span>{totalTime}ms</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          <div>
            <div className="text-sm text-gray-600 mb-1">Categoría</div>
            <div className="text-2xl font-bold text-gray-900">{result.category}</div>
          </div>
          
          <div>
            <div className="text-sm text-gray-600 mb-1">Confianza</div>
            <div className="flex items-baseline gap-2">
              <div className="text-2xl font-bold text-blue-600">
                {(result.confidence * 100).toFixed(1)}%
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${result.confidence * 100}%` }}
                />
              </div>
            </div>
          </div>
          
          {result.inferred_risk_level && (
            <div>
              <div className="text-sm text-gray-600 mb-1">Nivel de Riesgo</div>
              <div className={`inline-block px-4 py-2 rounded-lg border-2 font-semibold ${getRiskColor(result.inferred_risk_level)}`}>
                {result.inferred_risk_level}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Pipeline de fases */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-6">Pipeline de Clasificación</h3>
        
        <div className="space-y-4">
          {phases.map((phase, idx) => (
            <div key={idx}>
              <div className={`flex items-start gap-4 p-4 rounded-lg border-2 ${getStatusColor(phase.status)}`}>
                <div className="flex-shrink-0 mt-1">
                  {phase.icon}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold">{phase.name}</span>
                    <div className="flex items-center gap-3 text-sm">
                      {phase.duration && (
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {phase.duration}ms
                        </span>
                      )}
                      {phase.confidence !== undefined && (
                        <span className="font-semibold">
                          {(phase.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                      <span className="capitalize">{phase.status}</span>
                    </div>
                  </div>
                  
                  {phase.status === 'completed' && phase.data && (
                    <div className="mt-3 text-sm space-y-1">
                      {phase.name === 'Taxonomía JSON' && phase.data.class && (
                        <>
                          <div><span className="font-medium">Clase:</span> {phase.data.class}</div>
                          {phase.data.path && (
                            <div><span className="font-medium">Ruta:</span> {phase.data.path.join(' → ')}</div>
                          )}
                        </>
                      )}
                      
                      {phase.name === 'ML Transformers' && phase.data.category && (
                        <>
                          <div><span className="font-medium">Categoría:</span> {phase.data.category}</div>
                          <div><span className="font-medium">Modelo:</span> {phase.data.method}</div>
                        </>
                      )}
                      
                      {phase.name === 'Ontología OWL' && phase.data.class && (
                        <>
                          <div><span className="font-medium">Clase OWL:</span> {phase.data.class}</div>
                          {phase.data.keywords && phase.data.keywords.length > 0 && (
                            <div>
                              <span className="font-medium">Keywords:</span>{' '}
                              {phase.data.keywords.join(', ')}
                            </div>
                          )}
                        </>
                      )}
                      
                      {phase.name === 'Validación OWL' && (
                        <>
                          <div className="flex items-center gap-2">
                            {phase.data.is_valid ? (
                              <>
                                <CheckCircle className="w-4 h-4 text-green-600" />
                                <span className="text-green-700 font-medium">Metadatos válidos</span>
                              </>
                            ) : (
                              <>
                                <AlertTriangle className="w-4 h-4 text-red-600" />
                                <span className="text-red-700 font-medium">
                                  {phase.data.errors.length} errores de validación
                                </span>
                              </>
                            )}
                          </div>
                          {!phase.data.is_valid && (
                            <ul className="list-disc list-inside mt-2 text-red-700">
                              {phase.data.errors.map((err: string, i: number) => (
                                <li key={i}>{err}</li>
                              ))}
                            </ul>
                          )}
                        </>
                      )}
                      
                      {phase.name === 'Inferencia Riesgo' && phase.data.level && (
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Nivel inferido:</span>
                          <span className={`px-2 py-1 rounded font-semibold ${getRiskColor(phase.data.level)}`}>
                            {phase.data.level}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {phase.status === 'skipped' && (
                    <div className="mt-2 text-xs text-gray-500 italic">
                      Fase omitida (confianza suficiente en fases anteriores)
                    </div>
                  )}
                </div>
              </div>
              
              {idx < phases.length - 1 && (
                <div className="flex justify-center">
                  <div className="w-0.5 h-4 bg-gray-300" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Blending de confianza */}
      {result.phases_used.length > 1 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Blending de Confianza</h3>
          <div className="space-y-3 text-sm">
            {result.taxonomy_class && result.phases_used.includes('ml') && (
              <div className="flex items-center gap-2">
                <span className="text-gray-600">Taxonomía (50%) + ML (50%) =</span>
                <span className="font-semibold">
                  {((0.75 * 0.5 + (result.ml_confidence || 0) * 0.5) * 100).toFixed(1)}%
                </span>
              </div>
            )}
            
            {result.phases_used.includes('ontology') && (
              <div className="flex items-center gap-2">
                <span className="text-gray-600">Anterior (40%) + Ontología (60%) =</span>
                <span className="font-semibold text-blue-600">
                  {(result.confidence * 100).toFixed(1)}% (final)
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
