import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { dashboardApi } from '@/lib/api-client';
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
  Legend,
  ResponsiveContainer,
} from 'recharts';

const RISK_COLORS = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#ef4444',
  critical: '#7f1d1d',
};

const COMPLIANCE_COLORS = {
  compliant: '#10b981',
  non_compliant: '#ef4444',
  pending: '#6b7280',
};

interface StatCardProps {
  title: string;
  value: number | string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  subtitle?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, color, subtitle }) => {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-3xl font-bold ${color} mt-2`}>{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full ${color.replace('text-', 'bg-').replace(/\d00$/, '100')}`}>
          <Icon className={`w-8 h-8 ${color}`} />
        </div>
      </div>
    </div>
  );
};

export const Dashboard: React.FC = () => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardApi.getStats,
    refetchInterval: 30000, // Refetch every 30 seconds
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
        <p className="text-red-700">Error al cargar estadísticas: {(error as Error).message}</p>
      </div>
    );
  }

  if (!stats) return null;

  // Prepare chart data
  const categoryData = Object.entries(stats.documents_by_category).map(([name, value]) => ({
    name,
    value,
  }));

  const riskData = [
    { name: 'Bajo', value: stats.risk_distribution.low, color: RISK_COLORS.low },
    { name: 'Medio', value: stats.risk_distribution.medium, color: RISK_COLORS.medium },
    { name: 'Alto', value: stats.risk_distribution.high, color: RISK_COLORS.high },
    { name: 'Crítico', value: stats.risk_distribution.critical, color: RISK_COLORS.critical },
  ];

  const complianceData = [
    { name: 'Cumple', value: stats.compliance_summary.compliant, color: COMPLIANCE_COLORS.compliant },
    { name: 'No cumple', value: stats.compliance_summary.non_compliant, color: COMPLIANCE_COLORS.non_compliant },
    { name: 'Pendiente', value: stats.compliance_summary.pending, color: COMPLIANCE_COLORS.pending },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Documentos"
          value={stats.total_documents}
          icon={DocumentTextIcon}
          color="text-blue-600"
        />
        <StatCard
          title="Total Chunks"
          value={stats.total_chunks.toLocaleString()}
          icon={DocumentTextIcon}
          color="text-purple-600"
          subtitle="Fragmentos indexados"
        />
        <StatCard
          title="Entidades Extraídas"
          value={stats.total_entities.toLocaleString()}
          icon={CheckCircleIcon}
          color="text-green-600"
        />
        <StatCard
          title="Documentos Recientes"
          value={stats.recent_uploads.length}
          icon={ClockIcon}
          color="text-orange-600"
          subtitle="Últimas 24 horas"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Distribución por Categoría
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Distribución de Riesgo
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compliance Status */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Estado de Cumplimiento
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={complianceData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {complianceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Uploads */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Documentos Recientes
          </h3>
          <div className="space-y-3 max-h-[300px] overflow-y-auto">
            {stats.recent_uploads.length > 0 ? (
              stats.recent_uploads.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <DocumentTextIcon className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {doc.filename}
                      </p>
                      <p className="text-xs text-gray-500">
                        {doc.category || 'Sin categoría'}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`
                      badge flex-shrink-0
                      ${doc.status === 'INDEXED' ? 'badge-success' : ''}
                      ${doc.status === 'PROCESSING' ? 'badge-warning' : ''}
                      ${doc.status === 'FAILED' ? 'badge-danger' : ''}
                      ${doc.status === 'PENDING' ? 'badge-info' : ''}
                    `}
                  >
                    {doc.status}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500 text-center py-8">
                No hay documentos recientes
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Risk Alerts */}
      {stats.risk_distribution.critical > 0 && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-start gap-3">
            <ExclamationTriangleIcon className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900 mb-1">
                ⚠️ Alerta de Riesgo Crítico
              </h3>
              <p className="text-sm text-red-700">
                Hay {stats.risk_distribution.critical} documento(s) con riesgo crítico que
                requieren atención inmediata. Revise estos documentos en la sección de Riesgos.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
