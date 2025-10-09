// API Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Document {
  id: string;
  filename: string;
  file_size: number;
  mime_type: string;
  status: DocumentStatus;
  category?: string;
  language?: string;
  page_count?: number;
  user_id: string;
  created_at: string;
  updated_at: string;
  risk_score?: number;
  compliance_status?: string;
}

export enum DocumentStatus {
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  INDEXED = 'INDEXED',
  FAILED = 'FAILED',
}

export interface Chunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  page_number?: number;
  embedding?: number[];
  metadata?: Record<string, any>;
}

export interface Entity {
  id: string;
  document_id: string;
  entity_type: string;
  entity_value: string;
  confidence: number;
  start_pos?: number;
  end_pos?: number;
  context?: string;
}

export interface SearchRequest {
  query: string;
  filters?: {
    category?: string[];
    language?: string[];
    date_from?: string;
    date_to?: string;
    user_id?: string;
    risk_min?: number;
    risk_max?: number;
  };
  page?: number;
  page_size?: number;
  search_mode?: 'hybrid' | 'semantic' | 'keyword';
}

export interface SearchResult {
  document_id: string;
  document_filename: string;
  chunk_id: string;
  chunk_content: string;
  chunk_index: number;
  page_number?: number;
  score: number;
  category?: string;
  created_at: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  page: number;
  page_size: number;
  took_ms: number;
}

export interface RAGRequest {
  query: string;
  document_ids?: string[];
  max_chunks?: number;
  temperature?: number;
  stream?: boolean;
}

export interface RAGResponse {
  answer: string;
  chunks_used: Array<{
    document_id: string;
    chunk_id: string;
    content: string;
    score: number;
  }>;
  metadata: {
    model: string;
    tokens_used: number;
    took_ms: number;
  };
}

export interface RiskAssessment {
  document_id: string;
  overall_score: number;
  dimensions: {
    confidentiality: number;
    integrity: number;
    availability: number;
    legal: number;
    financial: number;
    reputational: number;
  };
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  patterns_detected: string[];
  recommendations: string[];
  assessed_at: string;
}

export interface ComplianceCheck {
  document_id: string;
  gdpr_compliant: boolean;
  personal_data_found: boolean;
  special_categories: string[];
  retention_period?: string;
  legal_basis?: string;
  dsr_applicable: boolean;
  issues: Array<{
    type: string;
    severity: 'LOW' | 'MEDIUM' | 'HIGH';
    description: string;
  }>;
  checked_at: string;
}

export interface UploadProgress {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  documentId?: string;
  error?: string;
}

export interface DashboardStats {
  total_documents: number;
  total_chunks: number;
  total_entities: number;
  documents_by_category: Record<string, number>;
  documents_by_status: Record<string, number>;
  risk_distribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  compliance_summary: {
    compliant: number;
    non_compliant: number;
    pending: number;
  };
  recent_uploads: Document[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  chunks?: Array<{
    document_id: string;
    document_filename: string;
    content: string;
    score: number;
  }>;
  timestamp: Date;
}
