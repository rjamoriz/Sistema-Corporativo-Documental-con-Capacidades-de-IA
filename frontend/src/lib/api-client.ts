import apiClient from '@/lib/api';
import type {
  Document,
  SearchRequest,
  SearchResponse,
  SearchResult,
  RAGRequest,
  RAGResponse,
  RiskAssessment,
  ComplianceCheck,
  DashboardStats,
} from '@/types';

// Documents API
export const documentsApi = {
  uploadDocument: async (file: File, userId: string): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    
    const response = await apiClient.post<Document>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getDocument: async (documentId: string): Promise<Document> => {
    const response = await apiClient.get<Document>(`/documents/${documentId}`);
    return response.data;
  },

  listDocuments: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    category?: string;
  }): Promise<Document[]> => {
    const response = await apiClient.get<Document[]>('/documents', { params });
    return response.data;
  },

  deleteDocument: async (documentId: string): Promise<void> => {
    await apiClient.delete(`/documents/${documentId}`);
  },

  downloadDocument: async (documentId: string): Promise<Blob> => {
    const response = await apiClient.get(`/documents/${documentId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Search API
export const searchApi = {
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>('/search', request);
    return response.data;
  },

  getSimilar: async (documentId: string, limit?: number): Promise<SearchResult[]> => {
    const response = await apiClient.get<SearchResult[]>(`/search/similar/${documentId}`, {
      params: { limit },
    });
    return response.data;
  },
};

// RAG API
export const ragApi = {
  ask: async (request: RAGRequest): Promise<RAGResponse> => {
    const response = await apiClient.post<RAGResponse>('/rag/ask', request);
    return response.data;
  },

  askStream: async (
    request: RAGRequest,
    onChunk: (chunk: string) => void,
    onComplete: (response: RAGResponse) => void
  ): Promise<void> => {
    const response = await fetch(`${apiClient.defaults.baseURL}/rag/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
      },
      body: JSON.stringify({ ...request, stream: true }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No reader available');
    }

    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            continue;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.chunk) {
              onChunk(parsed.chunk);
            }
            if (parsed.complete) {
              onComplete(parsed);
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e);
          }
        }
      }
    }
  },
};

// Risk API
export const riskApi = {
  assessRisk: async (documentId: string): Promise<RiskAssessment> => {
    const response = await apiClient.post<RiskAssessment>(`/risk/assess/${documentId}`);
    return response.data;
  },

  getRiskAssessment: async (documentId: string): Promise<RiskAssessment> => {
    const response = await apiClient.get<RiskAssessment>(`/risk/${documentId}`);
    return response.data;
  },

  listHighRiskDocuments: async (threshold?: number): Promise<Document[]> => {
    const response = await apiClient.get<Document[]>('/risk/high', {
      params: { threshold },
    });
    return response.data;
  },
};

// Compliance API
export const complianceApi = {
  checkCompliance: async (documentId: string): Promise<ComplianceCheck> => {
    const response = await apiClient.post<ComplianceCheck>(`/compliance/check/${documentId}`);
    return response.data;
  },

  getComplianceCheck: async (documentId: string): Promise<ComplianceCheck> => {
    const response = await apiClient.get<ComplianceCheck>(`/compliance/${documentId}`);
    return response.data;
  },

  processDSR: async (
    requestType: string,
    userId: string,
    documentIds?: string[]
  ): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post('/compliance/dsr', {
      request_type: requestType,
      user_id: userId,
      document_ids: documentIds,
    });
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/dashboard/stats');
    return response.data;
  },
};

// Auth API
export const authApi = {
  login: async (email: string, password: string): Promise<{ access_token: string; user: any }> => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<any> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};
