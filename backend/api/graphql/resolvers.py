"""
GraphQL Resolvers
Implements Query and Mutation resolvers for the GraphQL API.
"""

from typing import List, Optional
from datetime import datetime
import strawberry
from strawberry.types import Info
from strawberry.file_uploads import Upload

from .types import (
    Document,
    Entity,
    Chunk,
    Annotation,
    User,
    DocumentConnection,
    DocumentEdge,
    PageInfo,
    SearchResult,
    RAGResponse,
    UploadResult,
    DeleteResult,
    AnnotationResult,
    DocumentFilter,
    AnnotationInput,
    AnnotationUpdateInput,
    DocumentStatus,
    EntityType,
)


@strawberry.type
class Query:
    """GraphQL Query root"""
    
    @strawberry.field
    async def document(self, info: Info, id: str) -> Optional[Document]:
        """
        Get a single document by ID.
        
        Args:
            id: Document ID
            
        Returns:
            Document or None if not found
            
        Example:
            query {
              document(id: "doc-123") {
                id
                filename
                status
                entities { type text }
              }
            }
        """
        document_service = info.context.get("document_service")
        if document_service:
            doc = await document_service.get_by_id(id)
            return doc
        return None
    
    @strawberry.field
    async def documents(
        self,
        info: Info,
        filter: Optional[DocumentFilter] = None,
        limit: int = 20,
        offset: int = 0,
        order_by: Optional[str] = "uploaded_at",
        order_desc: bool = True,
    ) -> List[Document]:
        """
        Get list of documents with optional filtering.
        
        Args:
            filter: Document filter criteria
            limit: Max number of results (default 20)
            offset: Results offset for pagination
            order_by: Field to order by
            order_desc: Order descending (default True)
            
        Returns:
            List of documents
            
        Example:
            query {
              documents(
                filter: { status: COMPLETED, min_confidence: 0.8 }
                limit: 10
              ) {
                id
                filename
                confidence_score
              }
            }
        """
        document_service = info.context.get("document_service")
        if document_service:
            docs = await document_service.list_documents(
                filter=filter,
                limit=limit,
                offset=offset,
                order_by=order_by,
                order_desc=order_desc,
            )
            return docs
        return []
    
    @strawberry.field
    async def documents_paginated(
        self,
        info: Info,
        first: int = 20,
        after: Optional[str] = None,
        filter: Optional[DocumentFilter] = None,
    ) -> DocumentConnection:
        """
        Get paginated documents using cursor-based pagination.
        
        Args:
            first: Number of items to return
            after: Cursor for pagination
            filter: Document filter criteria
            
        Returns:
            DocumentConnection with edges and pageInfo
            
        Example:
            query {
              documentsPaginated(first: 10, after: "cursor-xyz") {
                edges {
                  cursor
                  node { id filename }
                }
                pageInfo {
                  hasNextPage
                  endCursor
                }
                totalCount
              }
            }
        """
        document_service = info.context.get("document_service")
        if document_service:
            result = await document_service.list_paginated(
                first=first,
                after=after,
                filter=filter,
            )
            
            edges = [
                DocumentEdge(cursor=item["cursor"], node=item["node"])
                for item in result["edges"]
            ]
            
            return DocumentConnection(
                edges=edges,
                page_info=PageInfo(
                    has_next_page=result["page_info"]["has_next_page"],
                    has_previous_page=result["page_info"]["has_previous_page"],
                    start_cursor=result["page_info"].get("start_cursor"),
                    end_cursor=result["page_info"].get("end_cursor"),
                ),
                total_count=result["total_count"],
            )
        
        return DocumentConnection(
            edges=[],
            page_info=PageInfo(has_next_page=False, has_previous_page=False),
            total_count=0,
        )
    
    @strawberry.field
    async def search(
        self,
        info: Info,
        query: str,
        limit: int = 10,
        min_score: float = 0.5,
        filter: Optional[DocumentFilter] = None,
    ) -> List[SearchResult]:
        """
        Search documents using semantic/vector search.
        
        Args:
            query: Search query
            limit: Max results (default 10)
            min_score: Minimum relevance score (0-1)
            filter: Additional document filters
            
        Returns:
            List of search results with scores
            
        Example:
            query {
              search(
                query: "contratos de proveedores"
                limit: 5
                minScore: 0.7
              ) {
                score
                document { id filename }
                highlights
              }
            }
        """
        search_service = info.context.get("search_service")
        if search_service:
            results = await search_service.search(
                query=query,
                limit=limit,
                min_score=min_score,
                filter=filter,
            )
            return results
        return []
    
    @strawberry.field
    async def rag_query(
        self,
        info: Info,
        question: str,
        document_ids: Optional[List[str]] = None,
        max_chunks: int = 5,
        temperature: float = 0.7,
    ) -> RAGResponse:
        """
        Query documents using RAG (Retrieval-Augmented Generation).
        
        Args:
            question: Natural language question
            document_ids: Limit search to specific documents
            max_chunks: Max chunks to use for context
            temperature: LLM temperature (0-1)
            
        Returns:
            RAG response with answer and sources
            
        Example:
            query {
              ragQuery(
                question: "¿Cuál es el monto total de los contratos?"
                maxChunks: 5
              ) {
                answer
                confidence
                sources { id filename }
                chunksUsed { content pageNumber }
              }
            }
        """
        rag_service = info.context.get("rag_service")
        if rag_service:
            response = await rag_service.query(
                question=question,
                document_ids=document_ids,
                max_chunks=max_chunks,
                temperature=temperature,
            )
            return response
        
        # Fallback response
        return RAGResponse(
            answer="RAG service not available",
            sources=[],
            confidence=0.0,
            chunks_used=[],
        )
    
    @strawberry.field
    async def entities(
        self,
        info: Info,
        document_id: Optional[str] = None,
        type: Optional[EntityType] = None,
        limit: int = 100,
    ) -> List[Entity]:
        """
        Get extracted entities, optionally filtered by document or type.
        
        Args:
            document_id: Filter by document
            type: Filter by entity type
            limit: Max results
            
        Returns:
            List of entities
        """
        entity_service = info.context.get("entity_service")
        if entity_service:
            entities = await entity_service.list_entities(
                document_id=document_id,
                type=type,
                limit=limit,
            )
            return entities
        return []
    
    @strawberry.field
    async def annotations(
        self,
        info: Info,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[Annotation]:
        """
        Get annotations, optionally filtered by document or user.
        
        Args:
            document_id: Filter by document
            user_id: Filter by user
            
        Returns:
            List of annotations
        """
        annotation_service = info.context.get("annotation_service")
        if annotation_service:
            annotations = await annotation_service.list_annotations(
                document_id=document_id,
                user_id=user_id,
            )
            return annotations
        return []
    
    @strawberry.field
    async def me(self, info: Info) -> Optional[User]:
        """
        Get current authenticated user.
        
        Returns:
            Current user or None if not authenticated
        """
        user = info.context.get("current_user")
        return user


@strawberry.type
class Mutation:
    """GraphQL Mutation root"""
    
    @strawberry.mutation
    async def upload_document(
        self,
        info: Info,
        file: Upload,
        metadata: Optional[strawberry.scalars.JSON] = None,
    ) -> UploadResult:
        """
        Upload a new document.
        
        Args:
            file: File to upload
            metadata: Optional metadata
            
        Returns:
            Upload result with document
            
        Example:
            mutation {
              uploadDocument(file: $file, metadata: {category: "contracts"}) {
                success
                message
                document { id filename status }
              }
            }
        """
        try:
            document_service = info.context.get("document_service")
            current_user = info.context.get("current_user")
            
            if not current_user:
                return UploadResult(
                    document=None,
                    success=False,
                    message="Authentication required",
                )
            
            if document_service:
                # Read file content
                content = await file.read()
                
                # Upload document
                doc = await document_service.upload(
                    filename=file.filename,
                    content=content,
                    mime_type=file.content_type or "application/octet-stream",
                    uploaded_by=current_user.id,
                    metadata=metadata,
                )
                
                return UploadResult(
                    document=doc,
                    success=True,
                    message=f"Document '{file.filename}' uploaded successfully",
                )
            
            return UploadResult(
                document=None,
                success=False,
                message="Document service not available",
            )
            
        except Exception as e:
            return UploadResult(
                document=None,
                success=False,
                message=f"Upload failed: {str(e)}",
            )
    
    @strawberry.mutation
    async def delete_document(
        self,
        info: Info,
        id: str,
    ) -> DeleteResult:
        """
        Delete a document.
        
        Args:
            id: Document ID to delete
            
        Returns:
            Delete result
            
        Example:
            mutation {
              deleteDocument(id: "doc-123") {
                success
                message
              }
            }
        """
        try:
            document_service = info.context.get("document_service")
            current_user = info.context.get("current_user")
            
            if not current_user:
                return DeleteResult(
                    success=False,
                    message="Authentication required",
                )
            
            if document_service:
                # Check permissions
                doc = await document_service.get_by_id(id)
                if not doc:
                    return DeleteResult(
                        success=False,
                        message=f"Document '{id}' not found",
                    )
                
                # Delete document
                await document_service.delete(id)
                
                return DeleteResult(
                    success=True,
                    message=f"Document '{id}' deleted successfully",
                )
            
            return DeleteResult(
                success=False,
                message="Document service not available",
            )
            
        except Exception as e:
            return DeleteResult(
                success=False,
                message=f"Delete failed: {str(e)}",
            )
    
    @strawberry.mutation
    async def add_annotation(
        self,
        info: Info,
        input: AnnotationInput,
    ) -> AnnotationResult:
        """
        Add annotation to document.
        
        Args:
            input: Annotation input data
            
        Returns:
            Annotation result
            
        Example:
            mutation {
              addAnnotation(input: {
                documentId: "doc-123"
                type: HIGHLIGHT
                pageNumber: 1
                position: {x: 100, y: 200, width: 300, height: 50}
                color: "#FFEB3B"
              }) {
                success
                annotation { id type }
              }
            }
        """
        try:
            annotation_service = info.context.get("annotation_service")
            current_user = info.context.get("current_user")
            
            if not current_user:
                return AnnotationResult(
                    annotation=None,
                    success=False,
                    message="Authentication required",
                )
            
            if annotation_service:
                annotation = await annotation_service.create(
                    document_id=input.document_id,
                    user_id=current_user.id,
                    type=input.type,
                    content=input.content,
                    page_number=input.page_number,
                    position=input.position,
                    color=input.color,
                )
                
                return AnnotationResult(
                    annotation=annotation,
                    success=True,
                    message="Annotation added successfully",
                )
            
            return AnnotationResult(
                annotation=None,
                success=False,
                message="Annotation service not available",
            )
            
        except Exception as e:
            return AnnotationResult(
                annotation=None,
                success=False,
                message=f"Failed to add annotation: {str(e)}",
            )
    
    @strawberry.mutation
    async def update_annotation(
        self,
        info: Info,
        id: str,
        input: AnnotationUpdateInput,
    ) -> AnnotationResult:
        """
        Update existing annotation.
        
        Args:
            id: Annotation ID
            input: Update data
            
        Returns:
            Annotation result
        """
        try:
            annotation_service = info.context.get("annotation_service")
            current_user = info.context.get("current_user")
            
            if not current_user:
                return AnnotationResult(
                    annotation=None,
                    success=False,
                    message="Authentication required",
                )
            
            if annotation_service:
                # Check ownership
                existing = await annotation_service.get_by_id(id)
                if not existing:
                    return AnnotationResult(
                        annotation=None,
                        success=False,
                        message=f"Annotation '{id}' not found",
                    )
                
                if existing.user_id != current_user.id:
                    return AnnotationResult(
                        annotation=None,
                        success=False,
                        message="You can only update your own annotations",
                    )
                
                # Update annotation
                annotation = await annotation_service.update(
                    id=id,
                    content=input.content,
                    position=input.position,
                    color=input.color,
                )
                
                return AnnotationResult(
                    annotation=annotation,
                    success=True,
                    message="Annotation updated successfully",
                )
            
            return AnnotationResult(
                annotation=None,
                success=False,
                message="Annotation service not available",
            )
            
        except Exception as e:
            return AnnotationResult(
                annotation=None,
                success=False,
                message=f"Failed to update annotation: {str(e)}",
            )
    
    @strawberry.mutation
    async def delete_annotation(
        self,
        info: Info,
        id: str,
    ) -> DeleteResult:
        """
        Delete annotation.
        
        Args:
            id: Annotation ID
            
        Returns:
            Delete result
        """
        try:
            annotation_service = info.context.get("annotation_service")
            current_user = info.context.get("current_user")
            
            if not current_user:
                return DeleteResult(
                    success=False,
                    message="Authentication required",
                )
            
            if annotation_service:
                # Check ownership
                existing = await annotation_service.get_by_id(id)
                if not existing:
                    return DeleteResult(
                        success=False,
                        message=f"Annotation '{id}' not found",
                    )
                
                if existing.user_id != current_user.id:
                    return DeleteResult(
                        success=False,
                        message="You can only delete your own annotations",
                    )
                
                # Delete annotation
                await annotation_service.delete(id)
                
                return DeleteResult(
                    success=True,
                    message="Annotation deleted successfully",
                )
            
            return DeleteResult(
                success=False,
                message="Annotation service not available",
            )
            
        except Exception as e:
            return DeleteResult(
                success=False,
                message=f"Failed to delete annotation: {str(e)}",
            )
