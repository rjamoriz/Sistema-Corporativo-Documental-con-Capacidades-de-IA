import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MagnifyingGlassIcon, FunnelIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { searchApi } from '@/lib/api-client';
import type { SearchRequest, SearchResult } from '@/types';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const CATEGORIES = [
  'LEGAL',
  'FINANCIAL',
  'HR',
  'TECHNICAL',
  'MARKETING',
  'OPERATIONS',
  'COMPLIANCE',
  'SENSITIVE',
  'OTHER',
];

interface SearchResultItemProps {
  result: SearchResult;
  onDocumentClick: (documentId: string) => void;
}

const SearchResultItem: React.FC<SearchResultItemProps> = ({ result, onDocumentClick }) => {
  return (
    <div
      className="card hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onDocumentClick(result.document_id)}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <DocumentTextIcon className="w-5 h-5 text-gray-400 flex-shrink-0" />
          <h3 className="font-semibold text-gray-900">{result.document_filename}</h3>
        </div>
        <span className="text-sm text-primary-600 font-medium">
          Score: {result.score.toFixed(2)}
        </span>
      </div>

      {result.category && (
        <span className="badge badge-info mb-3">{result.category}</span>
      )}

      <p className="text-sm text-gray-700 line-clamp-3 mb-3">{result.chunk_content}</p>

      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>
          Página: {result.page_number || 'N/A'} | Chunk: {result.chunk_index}
        </span>
        <span>{format(new Date(result.created_at), 'dd MMM yyyy', { locale: es })}</span>
      </div>
    </div>
  );
};

export const SearchComponent: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState<'hybrid' | 'semantic' | 'keyword'>('hybrid');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchRequest['filters']>({});
  const [page, setPage] = useState(1);

  const {
    data: searchResults,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['search', query, searchMode, filters, page],
    queryFn: () =>
      searchApi.search({
        query,
        search_mode: searchMode,
        filters,
        page,
        page_size: 10,
      }),
    enabled: query.length > 0,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    refetch();
  };

  const handleDocumentClick = (documentId: string) => {
    // Navigate to document viewer (to be implemented)
    console.log('View document:', documentId);
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Búsqueda de Documentos</h2>

        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Buscar documentos..."
                className="input pl-10"
              />
            </div>
            <button type="submit" className="btn-primary">
              Buscar
            </button>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`btn ${showFilters ? 'btn-primary' : 'btn-secondary'}`}
            >
              <FunnelIcon className="w-5 h-5" />
            </button>
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setSearchMode('hybrid')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                searchMode === 'hybrid'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Híbrida
            </button>
            <button
              type="button"
              onClick={() => setSearchMode('semantic')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                searchMode === 'semantic'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Semántica
            </button>
            <button
              type="button"
              onClick={() => setSearchMode('keyword')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                searchMode === 'keyword'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Palabras clave
            </button>
          </div>

          {showFilters && (
            <div className="border-t pt-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Categorías
                  </label>
                  <select
                    multiple
                    value={filters.category || []}
                    onChange={(e) =>
                      setFilters({
                        ...filters,
                        category: Array.from(e.target.selectedOptions, (option) => option.value),
                      })
                    }
                    className="input"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Rango de fechas
                  </label>
                  <div className="space-y-2">
                    <input
                      type="date"
                      value={filters.date_from || ''}
                      onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
                      className="input"
                    />
                    <input
                      type="date"
                      value={filters.date_to || ''}
                      onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
                      className="input"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Riesgo mínimo
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={filters.risk_min || ''}
                    onChange={(e) =>
                      setFilters({ ...filters, risk_min: parseFloat(e.target.value) })
                    }
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Riesgo máximo
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={filters.risk_max || ''}
                    onChange={(e) =>
                      setFilters({ ...filters, risk_max: parseFloat(e.target.value) })
                    }
                    className="input"
                  />
                </div>
              </div>
            </div>
          )}
        </form>
      </div>

      {isLoading && (
        <div className="card text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Buscando...</p>
        </div>
      )}

      {error && (
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-700">Error al buscar: {(error as Error).message}</p>
        </div>
      )}

      {searchResults && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {searchResults.total} resultados encontrados en {searchResults.took_ms}ms
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50"
              >
                Anterior
              </button>
              <span className="px-4 py-2 text-sm font-medium text-gray-700">
                Página {page}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={searchResults.results.length < searchResults.page_size}
                className="btn-secondary disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {searchResults.results.map((result, index) => (
              <SearchResultItem
                key={`${result.chunk_id}-${index}`}
                result={result}
                onDocumentClick={handleDocumentClick}
              />
            ))}
          </div>
        </div>
      )}

      {searchResults && searchResults.results.length === 0 && (
        <div className="card text-center py-12">
          <p className="text-gray-600">No se encontraron resultados</p>
        </div>
      )}
    </div>
  );
};
