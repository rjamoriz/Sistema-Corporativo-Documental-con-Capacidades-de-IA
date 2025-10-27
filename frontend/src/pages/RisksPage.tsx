import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  ShieldExclamationIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  CpuChipIcon,
  DocumentMagnifyingGlassIcon,
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
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
} from 'recharts';

const RISK_COLORS = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#ef4444',
  critical: '#7f1d1d',
};

const AI_RISK_COLORS = {
  MINIMAL: '#10b981',
  LIMITED: '#3b82f6',
  HIGH: '#f59e0b',
  UNACCEPTABLE: '#ef4444',
};

const RisksPage: React.FC = () => {
  const [showAIAssessment, setShowAIAssessment] = useState(false);
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<string>('HIGH');
  const [aiUseCase, setAIUseCase] = useState({
    use_case_title: '',
    use_case_description: '',
    sector: '',
    involves_biometrics: false,
    involves_critical_infrastructure: false,
    involves_law_enforcement: false,
    involves_employment: false,
  });

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

  // NEW: Get AI Act requirements
  const { data: aiActRequirements, isLoading: loadingAIAct } = useQuery({
    queryKey: ['ai-act-requirements', selectedRiskLevel],
    queryFn: async () => {
      const response = await apiClient.get(`/risk/eu/ai-act/requirements?risk_level=${selectedRiskLevel}`);
      return response.data;
    },
  });

  // NEW: AI Use Case Assessment mutation
  const assessAIUseCaseMutation = useMutation({
    mutationFn: async (data: typeof aiUseCase) => {
      const response = await apiClient.post('/risk/eu/ai-act/assess-use-case', data);
      return response.data;
    },
  });

  const handleAssessAIUseCase = async () => {
    if (!aiUseCase.use_case_title || !aiUseCase.use_case_description) {
      alert('Por favor complete título y descripción del caso de uso');
      return;
    }

    assessAIUseCaseMutation.mutate(aiUseCase);
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

  const riskLevels = ['UNACCEPTABLE', 'HIGH',
    </div>
  );
};

export default RisksPage;
