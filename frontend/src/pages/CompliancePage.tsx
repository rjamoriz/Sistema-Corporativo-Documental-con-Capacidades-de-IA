import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ChartBarIcon,
  InformationCircleIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import apiClient from '@/lib/api';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const COMPLIANCE_COLORS = {
  compliant: '#10b981',
  non_compliant: '#ef4444',
  pending: '#6b7280',
  partial: '#f59e0b',
};

const SEVERITY_COLORS = {
  high: '#ef4444',
  medium: '#f59e0b',
  low: '#10b981',
};

const CompliancePage: React.FC = () => {
  const [selectedRegulation, setSelectedRegulation] = useState<string>('GDPR');
  const [documentTitle, setDocumentTitle] = useState<string>('');
  const [documentContent, setDocumentContent] = useState<string>('');
  const [showComplianceChecker, setShowComplianceChecker] = useState(false);

  const { data: complianceData, isLoading, error } = useQuery({
    queryKey: ['compliance-dashboard'],
    queryFn: async () => {
      try {
        const response = await apiClient.get('/compliance/dashboard');
        return response.data;
      } catch (err) {
        return {
          total_documents: 0,
          compliance_summary: {
            compliant: 0,
            non_compliant: 0,
            pending: 0,
          },
        };
      }
    },
  });

  // NEW: Get GDPR requirements
  const { data: gdprRequirements, isLoading: loadingGDPR } = useQuery({
    queryKey: ['gdpr-requirements'],
    queryFn: async () => {
      const response = await apiClient.get('/compliance/eu/gdpr-requirements');
      return response.data;
    },
    enabled: selectedRegulation === 'GDPR',
  });

  // NEW: Document compliance check mutation
  const checkComplianceMutation = useMutation({
    mutationFn: async (data: { document_title: string; document_content: string; regulations: string[] }) => {
      const response = await apiClient.post('/compliance/eu/check-document', data);
      return response.data;
    },
  });

  const handleCheckCompliance = async () => {
    if (!documentTitle || !documentContent) {
      alert('Por favor ingrese título y contenido del documento');
      return;
    }

    checkComplianceMutation.mutate({
      document_title: documentTitle,
      document_content: documentContent,
      regulations: ['GDPR', 'AI_ACT'],
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border-red-200">
        <p className="text-red-700">Error al cargar datos de cumplimiento</p>
      </div>
    );
  }

  const complianceDistribution = [
    { name: 'Cumple', value: complianceData?.compliance_summary.compliant || 0, color: COMPLIANCE_COLORS.compliant },
    { name: 'No cumple', value: complianceData?.compliance_summary.non_compliant || 0, color: COMPLIANCE_COLORS.non_compliant },
    { name: 'Pendiente', value: complianceData?.compliance_summary.pending || 0, color: COMPLIANCE_COLORS.pending },
  ];

  const totalComplianceDocuments = complianceDistribution.reduce((sum, item) => sum + item.value, 0);

  const regulations = [
    { id: 'GDPR', name: 'GDPR', description: 'Reglamento General de Protección de Datos', eu: true },
    { id: 'AI_ACT', name: 'AI Act', description: 'Reglamento de Inteligencia Artificial', eu: true },
    { id: 'iso27001', name: 'ISO 27001', description: 'Seguridad de la Información', eu: false },
    { id: 'sarbanes', name: 'Sarbanes-Oxley', description: 'Ley de Reforma Contable', eu: false },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Cumplimiento Normativo</h1>
        <button
          onClick={() => setShowComplianceChecker(!showComplianceChecker)}
          className="btn btn-primary"
        >
          <DocumentTextIcon className="w-5 h-5 mr-2" />
          Verificar Documento
        </button>
      </div>

      {/* NEW: Real-time Compliance Checker */}
      {showComplianceChecker && (
        <div className="card bg-blue-50 border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
            <ShieldCheckIcon className="w-6 h-6 mr-2" />
            Verificador de Cumplimiento en Tiempo Real
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Título del Documento
              </label>
              <input
                type="text"
                value={documentTitle}
                onChange={(e) => setDocumentTitle(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ej: Política de Privacidad v2.1"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contenido del Documento
              </label>
              <textarea
                value={documentContent}
                onChange={(e) => setDocumentContent(e.target.value)}
                rows={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Pegue aquí el contenido del documento a verificar..."
              />
            </div>

            <button
              onClick={handleCheckCompliance}
              disabled={checkComplianceMutation.isPending}
              className="btn btn-primary w-full"
            >
              {checkComplianceMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Verificando...
                </>
              ) : (
                <>
                  <CheckCircleIcon className="w-5 h-5 mr-2" />
                  Verificar Cumplimiento
                </>
              )}
            </button>

            {/* Compliance Results */}
            {checkComplianceMutation.data && (
              <div className="mt-4 space-y-4">
                <div className={`p-4 rounded-lg ${
                  checkComplianceMutation.data.compliance_status === 'compliant' 
                    ? 'bg-green-50 border border-green-200'
                    : checkComplianceMutation.data.compliance_status === 'partial'
                    ? 'bg-yellow-50 border border-yellow-200'
                    : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center mb-2">
                    {checkComplianceMutation.data.compliance_status === 'compliant' ? (
                      <CheckCircleIcon className="w-6 h-6 text-green-600 mr-2" />
                    ) : (
                      <ExclamationTriangleIcon className="w-6 h-6 text-red-600 mr-2" />
                    )}
                    <h4 className="font-semibold text-gray-900">
                      Estado: {checkComplianceMutation.data.compliance_status.toUpperCase()}
                    </h4>
                  </div>
                  <p className="text-sm text-gray-700">{checkComplianceMutation.data.summary}</p>
                </div>

                {/* Violations */}
                {checkComplianceMutation.data.violations && checkComplianceMutation.data.violations.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-gray-900">Violaciones Detectadas:</h4>
                    {checkComplianceMutation.data.violations.map((violation: any, idx: number) => (
                      <div key={idx} className={`p-3 rounded-lg border ${
                        violation.severity === 'high' 
                          ? 'bg-red-50 border-red-200'
                          : violation.severity === 'medium'
                          ? 'bg-yellow-50 border-yellow-200'
                          : 'bg-blue-50 border-blue-200'
                      }`}>
                        <div className="flex items-start">
                          <span className={`inline-block px-2 py-1 text-xs font-semibold rounded mr-2 ${
                            violation.severity === 'high'
                              ? 'bg-red-100 text-red-800'
                              : violation.severity === 'medium'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {violation.severity.toUpperCase()}
                          </span>
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{violation.regulation} - {violation.article}</p>
                            <p className="text-sm text-gray-700 mt-1">{violation.description}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Recommendations */}
                {checkComplianceMutation.data.recommendations && checkComplianceMutation.data.recommendations.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-gray-900">Recomendaciones:</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {checkComplianceMutation.data.recommendations.map((rec: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-700">{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <p className="text-sm font-medium text-gray-600">Total Documentos</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{totalComplianceDocuments}</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-600">Cumple</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{complianceData?.compliance_summary.compliant || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-600">No Cumple</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{complianceData?.compliance_summary.non_compliant || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-600">Pendiente</p>
          <p className="text-3xl font-bold text-gray-600 mt-2">{complianceData?.compliance_summary.pending || 0}</p>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Estado de Cumplimiento</h3>
        {totalComplianceDocuments > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={complianceDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6">
                {complianceDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-8">
            <InformationCircleIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No hay datos de cumplimiento disponibles</p>
          </div>
        )}
      </div>

      {/* NEW: GDPR Requirements Display */}
      {selectedRegulation === 'GDPR' && gdprRequirements && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Requisitos GDPR - Artículos Clave
          </h3>
          <div className="space-y-3">
            {gdprRequirements.key_articles?.map((article: any, idx: number) => (
              <div key={idx} className={`p-4 rounded-lg border ${
                article.risk_level === 'CRITICAL' 
                  ? 'bg-red-50 border-red-200'
                  : article.risk_level === 'HIGH'
                  ? 'bg-orange-50 border-orange-200'
                  : 'bg-blue-50 border-blue-200'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">{article.article}</h4>
                  <span className={`px-2 py-1 text-xs font-semibold rounded ${
                    article.risk_level === 'CRITICAL'
                      ? 'bg-red-100 text-red-800'
                      : article.risk_level === 'HIGH'
                      ? 'bg-orange-100 text-orange-800'
                      : 'bg-blue-100 text-blue-800'
                  }`}>
                    {article.risk_level}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-2">{article.title}</p>
                <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                  {article.requirements?.map((req: string, reqIdx: number) => (
                    <li key={reqIdx}>{req}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Normativas Monitorizadas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {regulations.map((reg) => (
            <button
              key={reg.id}
              onClick={() => setSelectedRegulation(reg.id)}
              className={`p-4 rounded-lg text-left transition-colors ${
                selectedRegulation === reg.id
                  ? 'bg-blue-100 border-2 border-blue-500'
                  : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center justify-between">
                <h4 className="font-semibold text-gray-900">{reg.name}</h4>
                {reg.eu && (
                  <span className="px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded">
                    EU
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 mt-1">{reg.description}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">
          ✨ Nuevo: Verificación EU Regulatory en Tiempo Real
        </h3>
        <p className="text-sm text-blue-700">
          El sistema ahora integra EUR-Lex para verificar cumplimiento con GDPR y AI Act.
          Utilice el verificador de documentos para análisis instantáneo de compliance.
        </p>
      </div>
    </div>
  );
};

export default CompliancePage;
