/**
 * SPARQLConsole Component
 * 
 * Editor interactivo de consultas SPARQL sobre la ontología TEFinancia
 * - Editor de código con syntax highlighting
 * - Plantillas de consultas predefinidas
 * - Visualización de resultados en tabla
 * - Exportación de resultados a CSV/JSON
 */
import { useState } from 'react';
import { Play, Download, BookOpen, AlertCircle, Table as TableIcon, Code } from 'lucide-react';
import axios from 'axios';

interface SPARQLResult {
  columns: string[];
  rows: Record<string, string>[];
  query_time: number;
}

interface QueryTemplate {
  name: string;
  description: string;
  query: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const QUERY_TEMPLATES: QueryTemplate[] = [
  {
    name: 'Todas las clases',
    description: 'Lista todas las clases de documentos en la ontología',
    query: `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tf: <http://www.tefinancia.com/ontology#>

SELECT ?class ?label ?comment
WHERE {
  ?class rdf:type owl:Class .
  ?class rdfs:label ?label .
  OPTIONAL { ?class rdfs:comment ?comment }
}
ORDER BY ?label`
  },
  {
    name: 'Documentos de préstamo hipotecario',
    description: 'Encuentra todos los documentos clasificados como préstamo hipotecario',
    query: `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX tf: <http://www.tefinancia.com/ontology#>

SELECT ?doc ?importeFinanciado ?plazoMeses ?ltv
WHERE {
  ?doc rdf:type tf:PrestamoHipotecario .
  OPTIONAL { ?doc tf:importeFinanciado ?importeFinanciado }
  OPTIONAL { ?doc tf:plazoMeses ?plazoMeses }
  OPTIONAL { ?doc tf:ltv ?ltv }
}
LIMIT 50`
  },
  {
    name: 'Propiedades de una clase',
    description: 'Lista todas las propiedades definidas para una clase específica',
    query: `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tf: <http://www.tefinancia.com/ontology#>

SELECT ?property ?label ?type ?range
WHERE {
  ?property rdfs:domain tf:ProductoFinanciero .
  ?property rdfs:label ?label .
  ?property rdf:type ?type .
  OPTIONAL { ?property rdfs:range ?range }
  FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
}
ORDER BY ?label`
  },
  {
    name: 'Jerarquía de clases',
    description: 'Muestra la jerarquía de herencia de las clases',
    query: `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?class ?label ?parent ?parentLabel
WHERE {
  ?class rdf:type owl:Class .
  ?class rdfs:label ?label .
  ?class rdfs:subClassOf ?parent .
  ?parent rdfs:label ?parentLabel .
  FILTER(?parent != owl:Thing)
}
ORDER BY ?parentLabel ?label`
  },
  {
    name: 'Restricciones de cardinalidad',
    description: 'Encuentra restricciones de cardinalidad en propiedades',
    query: `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?property ?cardinality
WHERE {
  ?class rdfs:subClassOf ?restriction .
  ?restriction owl:onProperty ?property .
  {
    ?restriction owl:minCardinality ?cardinality .
  } UNION {
    ?restriction owl:maxCardinality ?cardinality .
  } UNION {
    ?restriction owl:cardinality ?cardinality .
  }
}`
  },
  {
    name: 'Documentos de alto riesgo',
    description: 'Busca documentos que cumplen criterios de alto riesgo',
    query: `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX tf: <http://www.tefinancia.com/ontology#>

SELECT ?doc ?type ?ltv ?tae ?sensible
WHERE {
  ?doc rdf:type ?type .
  OPTIONAL { ?doc tf:ltv ?ltv }
  OPTIONAL { ?doc tf:tae ?tae }
  OPTIONAL { ?doc tf:esSensible ?sensible }
  FILTER(
    (?ltv > 80) ||
    (?tae > 10) ||
    (?sensible = true)
  )
}
LIMIT 50`
  }
];

export default function SPARQLConsole() {
  const [query, setQuery] = useState(QUERY_TEMPLATES[0].query);
  const [result, setResult] = useState<SPARQLResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTemplates, setShowTemplates] = useState(true);

  const executeQuery = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const startTime = Date.now();
      const response = await axios.post(`${API_BASE}/ontology/sparql`, {
        query: query
      });
      const endTime = Date.now();
      
      setResult({
        ...response.data,
        query_time: endTime - startTime
      });
    } catch (err: any) {
      console.error('SPARQL query error:', err);
      setError(err.response?.data?.detail || 'Error ejecutando consulta SPARQL');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const loadTemplate = (template: QueryTemplate) => {
    setQuery(template.query);
    setShowTemplates(false);
  };

  const exportResults = (format: 'json' | 'csv') => {
    if (!result) return;

    let content: string;
    let filename: string;

    if (format === 'json') {
      content = JSON.stringify(result.rows, null, 2);
      filename = 'sparql_results.json';
    } else {
      // CSV
      const headers = result.columns.join(',');
      const rows = result.rows.map(row => 
        result.columns.map(col => {
          const value = row[col] || '';
          return value.includes(',') ? `"${value}"` : value;
        }).join(',')
      );
      content = [headers, ...rows].join('\n');
      filename = 'sparql_results.csv';
    }

    const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="grid grid-cols-12 gap-6 h-full">
      {/* Panel izquierdo: Editor */}
      <div className="col-span-5 flex flex-col gap-4">
        {/* Editor de consulta */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex flex-col flex-1">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Editor SPARQL</h2>
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <BookOpen className="w-4 h-4" />
              Plantillas
            </button>
          </div>

          <div className="flex-1 p-4">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full h-full font-mono text-sm border border-gray-300 rounded p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              placeholder="Escribe tu consulta SPARQL aquí..."
              spellCheck={false}
            />
          </div>

          <div className="p-4 border-t border-gray-200 flex gap-2">
            <button
              onClick={executeQuery}
              disabled={loading || !query.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <Play className="w-4 h-4" />
              {loading ? 'Ejecutando...' : 'Ejecutar'}
            </button>

            {result && (
              <>
                <button
                  onClick={() => exportResults('json')}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4" />
                  JSON
                </button>
                <button
                  onClick={() => exportResults('csv')}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4" />
                  CSV
                </button>
              </>
            )}
          </div>
        </div>

        {/* Plantillas */}
        {showTemplates && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-sm font-semibold">Plantillas de consulta</h3>
            </div>
            <div className="max-h-64 overflow-y-auto">
              {QUERY_TEMPLATES.map((template, idx) => (
                <button
                  key={idx}
                  onClick={() => loadTemplate(template)}
                  className="w-full text-left p-4 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
                >
                  <div className="font-medium text-sm mb-1">{template.name}</div>
                  <div className="text-xs text-gray-600">{template.description}</div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Panel derecho: Resultados */}
      <div className="col-span-7 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex flex-col">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">Resultados</h2>
            {result && (
              <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded">
                {result.rows.length} filas en {result.query_time}ms
              </span>
            )}
          </div>
          
          {result && result.rows.length > 0 && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <TableIcon className="w-4 h-4" />
              {result.columns.length} columnas
            </div>
          )}
        </div>

        <div className="flex-1 overflow-auto">
          {error && (
            <div className="m-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start gap-2 text-red-800">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium mb-1">Error en la consulta</div>
                  <div className="text-sm">{error}</div>
                </div>
              </div>
            </div>
          )}

          {!error && !result && !loading && (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center">
                <Code className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg mb-2">Sin resultados</p>
                <p className="text-sm">Ejecuta una consulta SPARQL para ver resultados</p>
              </div>
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Ejecutando consulta...</p>
              </div>
            </div>
          )}

          {result && result.rows.length === 0 && (
            <div className="m-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-center gap-2 text-yellow-800">
                <AlertCircle className="w-5 h-5" />
                <span>La consulta no devolvió resultados</span>
              </div>
            </div>
          )}

          {result && result.rows.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                      #
                    </th>
                    {result.columns.map((col) => (
                      <th
                        key={col}
                        className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-100">
                  {result.rows.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                        {idx + 1}
                      </td>
                      {result.columns.map((col) => (
                        <td key={col} className="px-4 py-3 text-gray-900">
                          {row[col] || <span className="text-gray-400 italic">null</span>}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
