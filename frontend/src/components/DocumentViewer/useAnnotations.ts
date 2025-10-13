/**
 * Annotations Hook
 * 
 * Custom hook for managing annotations with GraphQL mutations
 */

import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import {
  Annotation,
  AnnotationInput,
  AnnotationUpdateInput,
} from './types';

const GRAPHQL_ENDPOINT = 'http://localhost:8000/api/graphql/';

interface UseAnnotationsOptions {
  documentId: string;
  onError?: (error: Error) => void;
}

interface UseAnnotationsReturn {
  annotations: Annotation[];
  loading: boolean;
  error: Error | null;
  createAnnotation: (input: AnnotationInput) => Promise<void>;
  updateAnnotation: (id: string, input: AnnotationUpdateInput) => Promise<void>;
  deleteAnnotation: (id: string) => Promise<void>;
  refreshAnnotations: () => Promise<void>;
}

/**
 * GraphQL Mutations
 */
const CREATE_ANNOTATION_MUTATION = `
  mutation CreateAnnotation($input: AnnotationInput!) {
    createAnnotation(input: $input) {
      id
      documentId
      userId
      type
      pageNumber
      position
      content
      color
      createdAt
      updatedAt
    }
  }
`;

const UPDATE_ANNOTATION_MUTATION = `
  mutation UpdateAnnotation($id: ID!, $input: AnnotationUpdateInput!) {
    updateAnnotation(id: $id, input: $input) {
      id
      content
      position
      color
      updatedAt
    }
  }
`;

const DELETE_ANNOTATION_MUTATION = `
  mutation DeleteAnnotation($id: ID!) {
    deleteAnnotation(id: $id)
  }
`;

const GET_ANNOTATIONS_QUERY = `
  query GetAnnotations($documentId: ID!) {
    document(id: $documentId) {
      id
      annotations {
        id
        documentId
        userId
        type
        pageNumber
        position
        content
        color
        createdAt
        updatedAt
      }
    }
  }
`;

/**
 * Execute GraphQL query/mutation
 */
async function executeGraphQL<T = any>(
  query: string,
  variables?: Record<string, any>
): Promise<T> {
  try {
    const response = await fetch(GRAPHQL_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        variables,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    if (result.errors) {
      throw new Error(result.errors[0]?.message || 'GraphQL error');
    }

    return result.data;
  } catch (error) {
    console.error('GraphQL error:', error);
    throw error;
  }
}

/**
 * Hook for managing annotations
 */
export function useAnnotations({
  documentId,
  onError,
}: UseAnnotationsOptions): UseAnnotationsReturn {
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Fetch annotations from server
   */
  const refreshAnnotations = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await executeGraphQL(GET_ANNOTATIONS_QUERY, {
        documentId,
      });

      const fetchedAnnotations = data.document?.annotations || [];
      setAnnotations(fetchedAnnotations.map((a: any) => ({
        ...a,
        createdAt: new Date(a.createdAt),
        updatedAt: new Date(a.updatedAt),
      })));
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch annotations');
      setError(error);
      onError?.(error);
      toast.error('Error al cargar anotaciones');
    } finally {
      setLoading(false);
    }
  }, [documentId, onError]);

  /**
   * Create new annotation
   */
  const createAnnotation = useCallback(async (input: AnnotationInput) => {
    setLoading(true);
    setError(null);

    try {
      const data = await executeGraphQL(CREATE_ANNOTATION_MUTATION, {
        input: {
          ...input,
          // Convert Position object to JSON string if needed
          position: JSON.stringify(input.position),
        },
      });

      const newAnnotation = {
        ...data.createAnnotation,
        createdAt: new Date(data.createAnnotation.createdAt),
        updatedAt: new Date(data.createAnnotation.updatedAt),
        position: typeof data.createAnnotation.position === 'string'
          ? JSON.parse(data.createAnnotation.position)
          : data.createAnnotation.position,
      };

      setAnnotations(prev => [...prev, newAnnotation]);
      toast.success('Anotación creada');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to create annotation');
      setError(error);
      onError?.(error);
      toast.error('Error al crear anotación');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [onError]);

  /**
   * Update existing annotation
   */
  const updateAnnotation = useCallback(async (
    id: string,
    input: AnnotationUpdateInput
  ) => {
    setLoading(true);
    setError(null);

    try {
      const data = await executeGraphQL(UPDATE_ANNOTATION_MUTATION, {
        id,
        input: {
          ...input,
          // Convert Position object to JSON string if needed
          position: input.position ? JSON.stringify(input.position) : undefined,
        },
      });

      const updatedAnnotation = {
        ...data.updateAnnotation,
        updatedAt: new Date(data.updateAnnotation.updatedAt),
        position: typeof data.updateAnnotation.position === 'string'
          ? JSON.parse(data.updateAnnotation.position)
          : data.updateAnnotation.position,
      };

      setAnnotations(prev =>
        prev.map(a => (a.id === id ? { ...a, ...updatedAnnotation } : a))
      );
      toast.success('Anotación actualizada');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update annotation');
      setError(error);
      onError?.(error);
      toast.error('Error al actualizar anotación');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [onError]);

  /**
   * Delete annotation
   */
  const deleteAnnotation = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);

    try {
      await executeGraphQL(DELETE_ANNOTATION_MUTATION, { id });

      setAnnotations(prev => prev.filter(a => a.id !== id));
      toast.success('Anotación eliminada');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete annotation');
      setError(error);
      onError?.(error);
      toast.error('Error al eliminar anotación');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [onError]);

  return {
    annotations,
    loading,
    error,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
    refreshAnnotations,
  };
}

export default useAnnotations;
