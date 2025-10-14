import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ChartBarIcon,
  InformationCircleIcon,
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
} from 'recharts';

const COMPLIANCE_COLORS = {
  compliant: '#10b981',
  non_compliant: '#ef4444',
  pending: '#6b7280',
};

const CompliancePage: React.FC = () => {
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
    { id: 'gdpr', name: 'GDPR', description: 'Reglamento General de Protección de Datos' },
    { id: 'lopd', name: 'LOPD', description: 'Ley Orgánica de Protección de Datos' },
    { id: 'iso27001', name: 'ISO 27001', description: 'Seguridad de la Información' },
    { id: 'sarbanes', name: 'Sarbanes-Oxley', description: 'Ley de Reforma Contable' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Cumplimiento Normativo</h1>

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
                  <Cell key={cell-} fill={entry.color} />
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

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Normativas Monitorizadas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {regulations.map((reg) => (
            <div key={reg.id} className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-900">{reg.name}</h4>
              <p className="text-sm text-gray-600">{reg.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">Acerca del Cumplimiento Normativo</h3>
        <p className="text-sm text-blue-700">
          El sistema verifica automáticamente el cumplimiento de documentos con normativas como GDPR,
          LOPD, ISO 27001 y Sarbanes-Oxley.
        </p>
      </div>
    </div>
  );
};

export default CompliancePage;
