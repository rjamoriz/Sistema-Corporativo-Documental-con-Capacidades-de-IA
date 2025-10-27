/**
 * OntologyExplorer Component
 * 
 * Explorador interactivo de la ontología TEFinancia OWL
 * - Árbol jerárquico de clases
 * - Visualización de propiedades y restricciones
 * - Navegación por jerarquía de herencia
 * - Búsqueda y filtrado de clases
 */
import { useState, useEffect } from 'react';
import { ChevronRight, ChevronDown, FileText, AlertCircle, Search, Info } from 'lucide-react';
import { apiClient } from '../lib/api';

interface OntologyClass {
  uri: string;
  name: string;
  label: string;
  comment?: string;
  parent_classes: string[];
  subclasses: string[];
  properties: Property[];
  restrictions: Restriction[];
}

interface Property {
  uri: string;
  name: string;
  label: string;
  type: 'ObjectProperty' | 'DatatypeProperty';
  domain: string[];
  range: string[];
}

interface Restriction {
  property: string;
  type: string;
  value?: any;
  cardinality?: {
    min?: number;
    max?: number;
  };
}

interface ClassTreeNode {
  class_info: OntologyClass;
  children: ClassTreeNode[];
  expanded?: boolean;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export default function OntologyExplorer() {
  const [hierarchy, setHierarchy] = useState<ClassTreeNode[]>([]);
  const [selectedClass, setSelectedClass] = useState<OntologyClass | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadOntologyHierarchy();
  }, []);

  const loadOntologyHierarchy = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`${API_BASE}/ontology/hierarchy`);
      
      // La respuesta tiene formato: {root: {...}, total_classes: 33}
      // Convertimos el root a un array con un solo elemento
      const rootNode = response.data.root;
      if (rootNode) {
        // Convertir el nodo raíz en el formato esperado por el componente
        const convertNode = (node: any): ClassTreeNode => ({
          class_info: {
            uri: node.uri,
            name: node.name,
            label: node.label,
            comment: '',
            parent_classes: [],
            subclasses: [],
            properties: [],
            restrictions: []
          },
          children: (node.children || []).map(convertNode)
        });
        
        setHierarchy([convertNode(rootNode)]);
      }
      setError(null);
    } catch (err) {
      console.error('Error loading ontology:', err);
      setError('Error al cargar la ontología');
    } finally {
      setLoading(false);
    }
  };

  const loadClassDetails = async (className: string) => {
    try {
      const response = await apiClient.get(`${API_BASE}/ontology/classes/${className}`);
      setSelectedClass(response.data);
    } catch (err) {
      console.error('Error loading class details:', err);
    }
  };

  const toggleNode = (nodeName: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeName)) {
      newExpanded.delete(nodeName);
    } else {
      newExpanded.add(nodeName);
    }
    setExpandedNodes(newExpanded);
  };

  const renderClassTree = (nodes: ClassTreeNode[], depth = 0) => {
    if (!nodes || nodes.length === 0) return null;

    return nodes
      .filter(node => 
        !searchQuery || 
        node.class_info.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.class_info.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
      .map((node) => {
        const isExpanded = expandedNodes.has(node.class_info.name);
        const hasChildren = node.children && node.children.length > 0;
        const isSelected = selectedClass?.name === node.class_info.name;

        return (
          <div key={node.class_info.uri} style={{ marginLeft: `${depth * 16}px` }}>
            <div
              className={`flex items-center gap-2 p-2 rounded hover:bg-gray-100 cursor-pointer ${
                isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : ''
              }`}
              onClick={() => {
                loadClassDetails(node.class_info.name);
                if (hasChildren) toggleNode(node.class_info.name);
              }}
            >
              <div className="w-4">
                {hasChildren ? (
                  isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-500" />
                  )
                ) : (
                  <span className="w-4 h-4 inline-block" />
                )}
              </div>
              
              <FileText className="w-4 h-4 text-blue-600" />
              
              <span className="font-medium text-sm">{node.class_info.label}</span>
              
              {node.class_info.restrictions.length > 0 && (
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                  {node.class_info.restrictions.length} restricciones
                </span>
              )}
            </div>

            {isExpanded && hasChildren && renderClassTree(node.children, depth + 1)}
          </div>
        );
      });
  };

  const renderPropertyDetails = (property: Property) => (
    <div key={property.uri} className="border-l-2 border-blue-200 pl-3 py-2">
      <div className="flex items-center gap-2">
        <span className="font-medium text-sm">{property.label}</span>
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
          {property.type === 'ObjectProperty' ? 'Relación' : 'Dato'}
        </span>
      </div>
      
      {property.range.length > 0 && (
        <div className="text-xs text-gray-600 mt-1">
          → {property.range.join(', ')}
        </div>
      )}
    </div>
  );

  const renderRestriction = (restriction: Restriction) => {
    let description = '';
    
    if (restriction.type.includes('Cardinality')) {
      const { min, max } = restriction.cardinality || {};
      if (min !== undefined && max !== undefined && min === max) {
        description = `Exactamente ${min}`;
      } else if (min !== undefined) {
        description = `Mínimo ${min}`;
      } else if (max !== undefined) {
        description = `Máximo ${max}`;
      }
    } else if (restriction.type.includes('Value')) {
      description = `Valor: ${restriction.value}`;
    } else if (restriction.type.includes('AllValuesFrom')) {
      description = `Todos los valores de tipo: ${restriction.value}`;
    } else if (restriction.type.includes('SomeValuesFrom')) {
      description = `Algunos valores de tipo: ${restriction.value}`;
    }

    return (
      <div key={`${restriction.property}-${restriction.type}`} 
           className="flex items-start gap-2 text-sm bg-yellow-50 p-2 rounded">
        <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
        <div>
          <span className="font-medium">{restriction.property}</span>
          <span className="text-gray-600 ml-2">{description}</span>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando ontología...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-red-800">
          <AlertCircle className="w-5 h-5" />
          <span className="font-medium">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-12 gap-6 h-full">
      {/* Panel izquierdo: Árbol de clases */}
      <div className="col-span-5 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold mb-3">Jerarquía de Clases</h2>
          
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar clase..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {renderClassTree(hierarchy)}
        </div>
      </div>

      {/* Panel derecho: Detalles de clase */}
      <div className="col-span-7 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {selectedClass ? (
          <div className="p-6 overflow-y-auto h-full">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900">{selectedClass.label}</h2>
              <p className="text-sm text-gray-500 mt-1 font-mono">{selectedClass.name}</p>
            </div>

            {selectedClass.comment && (
              <div className="mb-6 bg-blue-50 border-l-4 border-blue-500 p-4">
                <div className="flex items-start gap-2">
                  <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-gray-700">{selectedClass.comment}</p>
                </div>
              </div>
            )}

            {/* Clases padre */}
            {selectedClass.parent_classes.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Hereda de:</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedClass.parent_classes.map((parent) => (
                    <span key={parent} className="bg-purple-100 text-purple-800 text-xs px-3 py-1 rounded-full">
                      {parent.split('#').pop()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Propiedades */}
            {selectedClass.properties.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Propiedades ({selectedClass.properties.length})</h3>
                <div className="space-y-2">
                  {selectedClass.properties.map(renderPropertyDetails)}
                </div>
              </div>
            )}

            {/* Restricciones OWL */}
            {selectedClass.restrictions.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  Restricciones OWL ({selectedClass.restrictions.length})
                </h3>
                <div className="space-y-2">
                  {selectedClass.restrictions.map(renderRestriction)}
                </div>
              </div>
            )}

            {/* Subclases */}
            {selectedClass.subclasses.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Subclases:</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedClass.subclasses.map((subclass) => (
                    <button
                      key={subclass}
                      onClick={() => loadClassDetails(subclass.split('#').pop() || '')}
                      className="bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full hover:bg-green-200 transition-colors"
                    >
                      {subclass.split('#').pop()}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Selecciona una clase para ver sus detalles</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
