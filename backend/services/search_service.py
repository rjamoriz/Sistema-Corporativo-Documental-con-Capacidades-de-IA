"""
Servicio de Búsqueda Híbrida
Combina búsqueda léxica (BM25 en OpenSearch) y semántica (vectores en pgvector)
usando Reciprocal Rank Fusion (RRF)
"""
from typing import Dict, List, Optional
from uuid import UUID

from opensearchpy import OpenSearch, RequestsHttpConnection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import numpy as np

from core.logging_config import logger
from core.config import settings
from models.database_models import Document, DocumentChunk
from models.schemas import SearchResult, SearchResponse
from services.extract_service import extract_service


class SearchService:
    """Servicio para búsqueda híbrida de documentos"""
    
    def __init__(self):
        # Cliente de OpenSearch
        self.opensearch_client = OpenSearch(
            hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
            http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
            use_ssl=settings.OPENSEARCH_USE_SSL,
            verify_certs=False,
            connection_class=RequestsHttpConnection
        )
        
        self.index_name = settings.OPENSEARCH_INDEX
        self._ensure_index_exists()
        
        # Pesos para fusión de rankings
        self.bm25_weight = 0.4
        self.semantic_weight = 0.6
        self.k_rrf = 60  # Constante para RRF
    
    def _ensure_index_exists(self):
        """Crea el índice de OpenSearch si no existe"""
        try:
            if not self.opensearch_client.indices.exists(index=self.index_name):
                # Mapping para el índice
                mapping = {
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "spanish_analyzer": {
                                    "type": "standard",
                                    "stopwords": "_spanish_"
                                }
                            }
                        },
                        "index": {
                            "number_of_shards": 2,
                            "number_of_replicas": 1
                        }
                    },
                    "mappings": {
                        "properties": {
                            "document_id": {"type": "keyword"},
                            "chunk_id": {"type": "keyword"},
                            "content": {
                                "type": "text",
                                "analyzer": "spanish_analyzer",
                                "fields": {
                                    "keyword": {"type": "keyword"}
                                }
                            },
                            "filename": {"type": "text"},
                            "classification": {"type": "keyword"},
                            "uploaded_by": {"type": "keyword"},
                            "uploaded_at": {"type": "date"},
                            "metadata": {"type": "object", "enabled": False}
                        }
                    }
                }
                
                self.opensearch_client.indices.create(index=self.index_name, body=mapping)
                logger.info(f"Created OpenSearch index: {self.index_name}")
        except Exception as e:
            logger.error(f"Error creating OpenSearch index: {e}")
            raise
    
    async def index_document(self, document: Document, chunks: List[DocumentChunk]):
        """
        Indexa un documento y sus chunks en OpenSearch
        
        Args:
            document: Documento a indexar
            chunks: Chunks del documento
        """
        try:
            for chunk in chunks:
                doc_body = {
                    "document_id": str(document.id),
                    "chunk_id": str(chunk.id),
                    "content": chunk.content,
                    "filename": document.filename,
                    "classification": document.classification.value,
                    "uploaded_by": str(document.uploaded_by),
                    "uploaded_at": document.uploaded_at.isoformat(),
                    "metadata": document.metadata_
                }
                
                self.opensearch_client.index(
                    index=self.index_name,
                    id=str(chunk.id),
                    body=doc_body
                )
            
            logger.info(f"Indexed {len(chunks)} chunks for document {document.id}")
            
        except Exception as e:
            logger.error(f"Error indexing document {document.id}: {e}", exc_info=True)
            raise
    
    async def hybrid_search(
        self,
        query: str,
        db: AsyncSession,
        limit: int = 10,
        filters: Optional[Dict] = None,
        user_id: Optional[UUID] = None
    ) -> SearchResponse:
        """
        Realiza búsqueda híbrida combinando BM25 y búsqueda semántica
        
        Args:
            query: Consulta de búsqueda
            db: Sesión de base de datos
            limit: Número de resultados
            filters: Filtros adicionales (clasificación, fechas, etc.)
            user_id: ID del usuario para control de acceso
            
        Returns:
            SearchResponse: Resultados de búsqueda
        """
        try:
            # 1. Búsqueda léxica (BM25)
            lexical_results = await self._lexical_search(query, limit * 2, filters, user_id)
            
            # 2. Búsqueda semántica (vectores)
            semantic_results = await self._semantic_search(query, db, limit * 2, filters, user_id)
            
            # 3. Fusión de resultados con RRF
            fused_results = self._reciprocal_rank_fusion(
                lexical_results,
                semantic_results,
                limit
            )
            
            # 4. Enriquecer con información de documentos
            enriched_results = await self._enrich_results(fused_results, db)
            
            logger.info(f"Hybrid search for '{query}' returned {len(enriched_results)} results")
            
            return SearchResponse(
                query=query,
                total=len(enriched_results),
                results=enriched_results,
                search_type="hybrid"
            )
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}", exc_info=True)
            return SearchResponse(query=query, total=0, results=[], search_type="error")
    
    async def _lexical_search(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict],
        user_id: Optional[UUID]
    ) -> List[Dict]:
        """Búsqueda léxica con BM25 en OpenSearch"""
        try:
            # Construir query de OpenSearch
            search_body = {
                "size": limit,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["content^2", "filename"],
                                    "type": "best_fields",
                                    "operator": "or"
                                }
                            }
                        ],
                        "filter": []
                    }
                },
                "highlight": {
                    "fields": {
                        "content": {
                            "fragment_size": 150,
                            "number_of_fragments": 3
                        }
                    }
                }
            }
            
            # Aplicar filtros
            if filters:
                if "classification" in filters:
                    search_body["query"]["bool"]["filter"].append(
                        {"term": {"classification": filters["classification"]}}
                    )
                if "date_from" in filters:
                    search_body["query"]["bool"]["filter"].append(
                        {"range": {"uploaded_at": {"gte": filters["date_from"]}}}
                    )
                if "date_to" in filters:
                    search_body["query"]["bool"]["filter"].append(
                        {"range": {"uploaded_at": {"lte": filters["date_to"]}}}
                    )
            
            # Control de acceso (si se especifica usuario)
            if user_id:
                search_body["query"]["bool"]["filter"].append(
                    {"term": {"uploaded_by": str(user_id)}}
                )
            
            # Ejecutar búsqueda
            response = self.opensearch_client.search(
                index=self.index_name,
                body=search_body
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "chunk_id": hit["_id"],
                    "document_id": hit["_source"]["document_id"],
                    "score": hit["_score"],
                    "content": hit["_source"]["content"],
                    "highlights": hit.get("highlight", {}).get("content", []),
                    "source": "lexical"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Lexical search failed: {e}", exc_info=True)
            return []
    
    async def _semantic_search(
        self,
        query: str,
        db: AsyncSession,
        limit: int,
        filters: Optional[Dict],
        user_id: Optional[UUID]
    ) -> List[Dict]:
        """Búsqueda semántica con pgvector"""
        try:
            # Generar embedding de la query
            query_embedding = extract_service._generate_embeddings([query])[0]
            
            # Construir query SQL con pgvector
            query_sql = """
            SELECT 
                dc.id as chunk_id,
                dc.document_id,
                dc.content,
                dc.embedding <-> :query_embedding as distance,
                1 - (dc.embedding <-> :query_embedding) as similarity,
                d.filename,
                d.classification
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.deleted_at IS NULL
            """
            
            # Aplicar filtros
            params = {"query_embedding": query_embedding.tolist(), "limit": limit}
            
            if filters:
                if "classification" in filters:
                    query_sql += " AND d.classification = :classification"
                    params["classification"] = filters["classification"]
                if "date_from" in filters:
                    query_sql += " AND d.uploaded_at >= :date_from"
                    params["date_from"] = filters["date_from"]
                if "date_to" in filters:
                    query_sql += " AND d.uploaded_at <= :date_to"
                    params["date_to"] = filters["date_to"]
            
            if user_id:
                query_sql += " AND d.uploaded_by = :user_id"
                params["user_id"] = str(user_id)
            
            query_sql += " ORDER BY distance LIMIT :limit"
            
            # Ejecutar query
            result = await db.execute(text(query_sql), params)
            rows = result.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "chunk_id": str(row.chunk_id),
                    "document_id": str(row.document_id),
                    "score": float(row.similarity),
                    "content": row.content,
                    "distance": float(row.distance),
                    "source": "semantic"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}", exc_info=True)
            return []
    
    def _reciprocal_rank_fusion(
        self,
        lexical_results: List[Dict],
        semantic_results: List[Dict],
        limit: int
    ) -> List[Dict]:
        """
        Fusiona resultados usando Reciprocal Rank Fusion (RRF)
        
        Score(d) = Σ (1 / (k + rank(d)))
        """
        # Diccionario para acumular scores
        chunk_scores = {}
        chunk_data = {}
        
        # Procesar resultados léxicos
        for rank, result in enumerate(lexical_results, start=1):
            chunk_id = result["chunk_id"]
            rrf_score = 1 / (self.k_rrf + rank)
            
            if chunk_id not in chunk_scores:
                chunk_scores[chunk_id] = 0
                chunk_data[chunk_id] = result
            
            chunk_scores[chunk_id] += self.bm25_weight * rrf_score
        
        # Procesar resultados semánticos
        for rank, result in enumerate(semantic_results, start=1):
            chunk_id = result["chunk_id"]
            rrf_score = 1 / (self.k_rrf + rank)
            
            if chunk_id not in chunk_scores:
                chunk_scores[chunk_id] = 0
                chunk_data[chunk_id] = result
            
            chunk_scores[chunk_id] += self.semantic_weight * rrf_score
        
        # Ordenar por score combinado
        sorted_chunks = sorted(
            chunk_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # Construir resultados finales
        fused_results = []
        for chunk_id, score in sorted_chunks:
            result = chunk_data[chunk_id].copy()
            result["fused_score"] = score
            fused_results.append(result)
        
        return fused_results
    
    async def _enrich_results(
        self,
        results: List[Dict],
        db: AsyncSession
    ) -> List[SearchResult]:
        """Enriquece resultados con información completa de documentos"""
        enriched = []
        
        for result in results:
            # Obtener documento completo
            doc_result = await db.execute(
                select(Document).where(Document.id == result["document_id"])
            )
            document = doc_result.scalar_one_or_none()
            
            if document:
                enriched.append(SearchResult(
                    document_id=document.id,
                    filename=document.filename,
                    classification=document.classification,
                    score=result["fused_score"],
                    chunk_content=result["content"],
                    highlights=result.get("highlights", []),
                    uploaded_at=document.uploaded_at,
                    metadata=document.metadata_
                ))
        
        return enriched
    
    async def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Obtiene sugerencias de autocompletado"""
        try:
            search_body = {
                "size": 0,
                "suggest": {
                    "text": query,
                    "simple_phrase": {
                        "phrase": {
                            "field": "content",
                            "size": limit,
                            "gram_size": 3,
                            "direct_generator": [{
                                "field": "content",
                                "suggest_mode": "always"
                            }]
                        }
                    }
                }
            }
            
            response = self.opensearch_client.search(
                index=self.index_name,
                body=search_body
            )
            
            suggestions = []
            for option in response["suggest"]["simple_phrase"][0]["options"]:
                suggestions.append(option["text"])
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []


# Instancia singleton del servicio
search_service = SearchService()
