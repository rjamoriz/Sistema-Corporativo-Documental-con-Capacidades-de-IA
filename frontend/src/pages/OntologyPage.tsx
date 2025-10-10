/**
 * Ontology Page
 * 
 * Página principal para exploración y análisis de ontología
 * - Pestaña de explorador jerárquico
 * - Pestaña de consola SPARQL
 * - Pestaña de análisis de clasificación
 */
import { useState } from 'react';
import { Database, Code, BarChart3 } from 'lucide-react';
import OntologyExplorer from '../components/OntologyExplorer';
import SPARQLConsole from '../components/SPARQLConsole';
import ClassificationExplainer from '../components/ClassificationExplainer';

type TabType = 'explorer' | 'sparql' | 'classification';

export default function OntologyPage() {
  const [activeTab, setActiveTab] = useState<TabType>('explorer');

  const tabs = [
    {
      id: 'explorer' as TabType,
      name: 'Explorador',
      icon: Database,
      description: 'Navega por la jerarquía de clases OWL'
    },
    {
      id: 'sparql' as TabType,
      name: 'Consola SPARQL',
      icon: Code,
      description: 'Ejecuta consultas SPARQL sobre la ontología'
    },
    {
      id: 'classification' as TabType,
      name: 'Pipeline de Clasificación',
      icon: BarChart3,
      description: 'Analiza el proceso de clasificación inteligente'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Ontología TEFinancia</h1>
        <p className="mt-2 text-gray-600">
          Exploración y análisis de la ontología OWL de productos financieros
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    group inline-flex items-center gap-2 px-6 py-4 border-b-2 font-medium text-sm
                    transition-colors
                    ${isActive
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-600'}`} />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab content */}
        <div className="p-6 min-h-[600px]">
          {activeTab === 'explorer' && <OntologyExplorer />}
          {activeTab === 'sparql' && <SPARQLConsole />}
          {activeTab === 'classification' && (
            <ClassificationExplainer 
              result={{
                category: 'FINANCIAL',
                confidence: 0.91,
                method: 'taxonomy+ml+ontology',
                phases_used: ['taxonomy', 'ml', 'ontology'],
                classification_mode: 'intelligent',
                taxonomy_class: 'PrestamoHipotecario',
                taxonomy_label: 'Préstamo Hipotecario',
                taxonomy_path: ['ProductoFinanciero', 'Prestamo', 'PrestamoHipotecario'],
                ml_category: 'FINANCIAL',
                ml_confidence: 0.87,
                ontology_class: 'PrestamoHipotecario',
                ontology_label: 'Préstamo Hipotecario',
                ontology_confidence: 0.93,
                matched_keywords: ['préstamo hipotecario', 'hipoteca', 'vivienda'],
                metadata_validation: {
                  is_valid: false,
                  errors: ['importeFinanciado debe ser >= 30000'],
                  required_fields: ['tieneCliente', 'requiereValoracion']
                },
                inferred_risk_level: 'ALTO'
              }}
            />
          )}
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">Ontología OWL 2</h3>
          <p className="text-sm text-blue-800">
            Jerarquía formal de 20+ clases de productos financieros con propiedades y restricciones
          </p>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
          <h3 className="text-sm font-semibold text-purple-900 mb-2">SPARQL 1.1</h3>
          <p className="text-sm text-purple-800">
            Consultas semánticas sobre la ontología con inferencias y razonamiento lógico
          </p>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
          <h3 className="text-sm font-semibold text-green-900 mb-2">Pipeline Inteligente</h3>
          <p className="text-sm text-green-800">
            Clasificación adaptativa: Taxonomía JSON → ML → OWL con optimización automática
          </p>
        </div>
      </div>
    </div>
  );
}
