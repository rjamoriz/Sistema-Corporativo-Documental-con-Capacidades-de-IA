import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ShieldExclamationIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
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

const RISK_COLORS = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#ef4444',
  critical: '#7f1d1d',
};

const RisksPage: React.FC = () => {
  const { data: riskData, isLoading, error } = useQuery({
    queryKey: ['risk-dashboard'],
    queryFn: async () => {
      try {
        const response = await apiClient.get('/risk/dashboard');
        return response.data;
      } catch (err) {
        return {
          total_documents: 0,
          risk_distribution: {
            low: 0,
            medium: 0,
            high: 0,
            critical: 0,
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
        <p className="text-red-700">Error al cargar datos de riesgos</p>
      </div>
    );
  }

  const riskDistribution = [
    { name: 'Bajo', value: riskData?.risk_distribution.low || 0, color: RISK_COLORS.low },
    { name: 'Medio', value: riskData?.risk_distribution.medium || 0, color: RISK_COLORS.medium },
    { name: 'Alto', value: riskData?.risk_distribution.high || 0, color: RISK_COLORS.high },
    { name: 'Crítico', value: riskData?.risk_distribution.critical || 0, color: RISK_COLORS.critical },
  ];

  const totalRiskDocuments = riskDistribution.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Análisis de Riesgos</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <p className="text-sm font-medium text-gray-600">Total Documentos</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{totalRiskDocuments}</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-600">Riesgo Bajo</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{riskData?.risk_distribution.low || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-600">Riesgo Alto</p>
          <p className="text-3xl font-bold text-orange-600 mt-2">{riskData?.risk_distribution.high || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-600">Riesgo Crítico</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{riskData?.risk_distribution.critical || 0}</p>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribución de Riesgo</h3>
        {totalRiskDocuments > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={riskDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6">
                {riskDistribution.map((entry, index) => (
                  <Cell key={cell-} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-8">
            <InformationCircleIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No hay datos de riesgo disponibles</p>
          </div>
        )}
      </div>

      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">Acerca del Análisis de Riesgos</h3>
        <p className="text-sm text-blue-700">
          El sistema analiza documentos en 6 dimensiones: Legal (25%), Financiero (30%),
          Operacional (20%), ESG (10%), Privacidad (10%) y Ciberseguridad (5%).
        </p>
      </div>
    </div>
  );
};

export default RisksPage;
