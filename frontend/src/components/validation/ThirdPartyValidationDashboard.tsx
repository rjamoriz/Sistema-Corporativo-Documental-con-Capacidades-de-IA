/**
 * Dashboard de Validación de Terceros
 * 
 * Muestra estadísticas en tiempo real de validaciones contra:
 * - Listas de sanciones (OFAC, EU, World Bank)
 * - Registros mercantiles
 * - Scoring ESG
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  IconButton,
  Tooltip,
  TextField,
  MenuItem,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import axios from 'axios';

// ============================================================================
// Interfaces
// ============================================================================

interface ValidationStats {
  total_entities_validated: number;
  entities_flagged: number;
  flagged_percentage: number;
  total_documents_validated: number;
}

interface ValidationResult {
  id: number;
  entity_name: string;
  entity_type: string;
  is_sanctioned: boolean;
  confidence: number;
  sources_checked: string[];
  checked_at: string;
}

interface RecentValidation {
  document_id: number;
  document_name?: string;
  entities_validated: number;
  entities_flagged: number;
  validated_at: string;
}

interface TrendData {
  date: string;
  validations: number;
  flagged: number;
}

interface SourceDistribution {
  source: string;
  count: number;
}

// ============================================================================
// Componente Principal
// ============================================================================

const ThirdPartyValidationDashboard: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estados de datos
  const [stats, setStats] = useState<ValidationStats | null>(null);
  const [recentValidations, setRecentValidations] = useState<RecentValidation[]>([]);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [sourceDistribution, setSourceDistribution] = useState<SourceDistribution[]>([]);
  const [flaggedEntities, setFlaggedEntities] = useState<ValidationResult[]>([]);
  
  // Estados de UI
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d'>('30d');
  const [selectedSource, setSelectedSource] = useState<string>('all');
  const [detailsOpen, setDetailsOpen] = useState<boolean>(false);
  const [selectedEntity, setSelectedEntity] = useState<ValidationResult | null>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

  // ============================================================================
  // Data Fetching
  // ============================================================================

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch stats
      const statsRes = await axios.get(`${API_BASE_URL}/validation/stats`);
      setStats(statsRes.data);

      // Fetch recent validations
      const recentRes = await axios.get(`${API_BASE_URL}/validation/history?limit=10`);
      setRecentValidations(recentRes.data);

      // Fetch trends (mock data - implementar endpoint real)
      const trendsData = generateMockTrends(selectedPeriod);
      setTrends(trendsData);

      // Fetch source distribution (mock data)
      const sourcesData = [
        { source: 'OFAC', count: 45 },
        { source: 'EU_SANCTIONS', count: 32 },
        { source: 'WORLD_BANK', count: 18 },
      ];
      setSourceDistribution(sourcesData);

      // Fetch flagged entities
      // En producción: filtrar por is_sanctioned=true
      const flaggedRes = await axios.get(`${API_BASE_URL}/validation/results?flagged=true&limit=20`);
      setFlaggedEntities(flaggedRes.data || []);

    } catch (err: any) {
      setError(err.message || 'Error cargando datos del dashboard');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh cada 5 minutos
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [selectedPeriod]);

  // ============================================================================
  // Helper Functions
  // ============================================================================

  const generateMockTrends = (period: string): TrendData[] => {
    const days = period === '7d' ? 7 : period === '30d' ? 30 : 90;
    const data: TrendData[] = [];
    const today = new Date();

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      data.push({
        date: date.toISOString().split('T')[0],
        validations: Math.floor(Math.random() * 50) + 10,
        flagged: Math.floor(Math.random() * 5),
      });
    }

    return data;
  };

  const getRiskColor = (confidence: number): string => {
    if (confidence >= 0.8) return '#f44336'; // Red - High risk
    if (confidence >= 0.5) return '#ff9800'; // Orange - Medium risk
    return '#4caf50'; // Green - Low risk
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleEntityClick = (entity: ValidationResult) => {
    setSelectedEntity(entity);
    setDetailsOpen(true);
  };

  const exportToCSV = () => {
    // Implementar export a CSV
    console.log('Exporting to CSV...');
  };

  // ============================================================================
  // Render Loading/Error States
  // ============================================================================

  if (loading && !stats) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        <Typography variant="h6">Error cargando dashboard</Typography>
        <Typography>{error}</Typography>
        <Button onClick={fetchDashboardData} startIcon={<RefreshIcon />} sx={{ mt: 1 }}>
          Reintentar
        </Button>
      </Alert>
    );
  }

  // ============================================================================
  // Main Render
  // ============================================================================

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          🛡️ Dashboard de Validación de Terceros
        </Typography>
        <Box>
          <Tooltip title="Actualizar datos">
            <IconButton onClick={fetchDashboardData} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Exportar a CSV">
            <IconButton onClick={exportToCSV}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#e3f2fd' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Validaciones
              </Typography>
              <Typography variant="h3" fontWeight="bold">
                {stats?.total_entities_validated.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary" mt={1}>
                Entidades validadas
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#ffebee' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Entidades Flagged
              </Typography>
              <Typography variant="h3" fontWeight="bold" color="error">
                {stats?.entities_flagged || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary" mt={1}>
                {stats?.flagged_percentage.toFixed(2)}% del total
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#e8f5e9' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Documentos Validados
              </Typography>
              <Typography variant="h3" fontWeight="bold" color="success.main">
                {stats?.total_documents_validated || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary" mt={1}>
                Procesados completos
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#fff3e0' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Tasa de Cumplimiento
              </Typography>
              <Typography variant="h3" fontWeight="bold" color="warning.main">
                {(100 - (stats?.flagged_percentage || 0)).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary" mt={1}>
                Entidades limpias
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} mb={4}>
        {/* Trends Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" fontWeight="bold">
                  Tendencia de Validaciones
                </Typography>
                <TextField
                  select
                  size="small"
                  value={selectedPeriod}
                  onChange={(e) => setSelectedPeriod(e.target.value as any)}
                  sx={{ width: 120 }}
                >
                  <MenuItem value="7d">7 días</MenuItem>
                  <MenuItem value="30d">30 días</MenuItem>
                  <MenuItem value="90d">90 días</MenuItem>
                </TextField>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="validations"
                    stroke="#2196f3"
                    name="Validaciones"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="flagged"
                    stroke="#f44336"
                    name="Flagged"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Source Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" mb={2}>
                Distribución por Fuente
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sourceDistribution}
                    dataKey="count"
                    nameKey="source"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    <Cell fill="#2196f3" />
                    <Cell fill="#4caf50" />
                    <Cell fill="#ff9800" />
                  </Pie>
                  <RechartsTooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Flagged Entities Table */}
      <Card mb={4}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            ⚠️ Entidades Sancionadas Recientes
          </Typography>
          
          {flaggedEntities.length === 0 ? (
            <Alert severity="success" icon={<CheckCircleIcon />}>
              No hay entidades sancionadas en el período seleccionado
            </Alert>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                    <TableCell><strong>Entidad</strong></TableCell>
                    <TableCell><strong>Tipo</strong></TableCell>
                    <TableCell><strong>Confianza</strong></TableCell>
                    <TableCell><strong>Fuentes</strong></TableCell>
                    <TableCell><strong>Fecha</strong></TableCell>
                    <TableCell><strong>Acciones</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {flaggedEntities.map((entity) => (
                    <TableRow
                      key={entity.id}
                      sx={{
                        bgcolor: entity.confidence >= 0.8 ? '#ffebee' : '#fff3e0',
                        '&:hover': { bgcolor: '#f5f5f5' },
                      }}
                    >
                      <TableCell>
                        <Typography fontWeight="bold">{entity.entity_name}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={entity.entity_type} size="small" />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <LinearProgress
                            variant="determinate"
                            value={entity.confidence * 100}
                            sx={{
                              width: 60,
                              height: 8,
                              borderRadius: 4,
                              bgcolor: '#e0e0e0',
                              '& .MuiLinearProgress-bar': {
                                bgcolor: getRiskColor(entity.confidence),
                              },
                            }}
                          />
                          <Typography variant="body2">
                            {(entity.confidence * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={0.5} flexWrap="wrap">
                          {entity.sources_checked.map((source) => (
                            <Chip
                              key={source}
                              label={source}
                              size="small"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="textSecondary">
                          {formatDate(entity.checked_at)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Ver detalles">
                          <IconButton
                            size="small"
                            onClick={() => handleEntityClick(entity)}
                          >
                            <InfoIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Recent Validations */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            📄 Validaciones Recientes de Documentos
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                  <TableCell><strong>Documento</strong></TableCell>
                  <TableCell><strong>Entidades</strong></TableCell>
                  <TableCell><strong>Flagged</strong></TableCell>
                  <TableCell><strong>Estado</strong></TableCell>
                  <TableCell><strong>Fecha</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentValidations.map((validation) => (
                  <TableRow key={validation.document_id}>
                    <TableCell>
                      Documento #{validation.document_id}
                    </TableCell>
                    <TableCell>{validation.entities_validated}</TableCell>
                    <TableCell>
                      <Chip
                        label={validation.entities_flagged}
                        color={validation.entities_flagged > 0 ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {validation.entities_flagged > 0 ? (
                        <Chip
                          icon={<WarningIcon />}
                          label="Requiere atención"
                          color="error"
                          size="small"
                        />
                      ) : (
                        <Chip
                          icon={<CheckCircleIcon />}
                          label="Aprobado"
                          color="success"
                          size="small"
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {formatDate(validation.validated_at)}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Entity Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Detalles de Validación: {selectedEntity?.entity_name}
        </DialogTitle>
        <DialogContent>
          {selectedEntity && (
            <Box>
              <Grid container spacing={2} mt={1}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Tipo de Entidad
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {selectedEntity.entity_type}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Nivel de Confianza
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {(selectedEntity.confidence * 100).toFixed(1)}%
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary" mb={1}>
                    Fuentes Consultadas
                  </Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    {selectedEntity.sources_checked.map((source) => (
                      <Chip key={source} label={source} color="primary" />
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">
                    Fecha de Validación
                  </Typography>
                  <Typography variant="body1">
                    {formatDate(selectedEntity.checked_at)}
                  </Typography>
                </Grid>
              </Grid>
              
              {selectedEntity.is_sanctioned && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    <strong>⚠️ ALERTA:</strong> Esta entidad ha sido encontrada en listas de sanciones.
                    Se requiere revisión manual antes de proceder con cualquier transacción.
                  </Typography>
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Cerrar</Button>
          <Button variant="contained" color="primary">
            Exportar Reporte
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ThirdPartyValidationDashboard;
