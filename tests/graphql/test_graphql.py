"""
GraphQL API Tests
Comprehensive test suite for GraphQL schema, queries, and mutations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import List, Dict, Any

# Mock Strawberry for testing without full integration
import sys
from unittest.mock import Mock

# Mock strawberry module
strawberry_mock = Mock()
sys.modules['strawberry'] = strawberry_mock
sys.modules['strawberry.fastapi'] = Mock()
sys.modules['strawberry.types'] = Mock()
sys.modules['strawberry.dataloader'] = Mock()
sys.modules['strawberry.file_uploads'] = Mock()
sys.modules['strawberry.scalars'] = Mock()

# Now we can import our GraphQL modules
from backend.api.graphql.types import (
    DocumentStatus,
    EntityType,
    AnnotationType,
)


class TestGraphQLTypes:
    """Test GraphQL type definitions"""
    
    def test_document_status_enum(self):
        """Test DocumentStatus enum values"""
        assert hasattr(DocumentStatus, 'PENDING')
        assert hasattr(DocumentStatus, 'PROCESSING')
        assert hasattr(DocumentStatus, 'COMPLETED')
        assert hasattr(DocumentStatus, 'ERROR')
    
    def test_entity_type_enum(self):
        """Test EntityType enum values"""
        assert hasattr(EntityType, 'PERSON')
        assert hasattr(EntityType, 'ORGANIZATION')
        assert hasattr(EntityType, 'MONEY')
        assert hasattr(EntityType, 'CONTRACT')
    
    def test_annotation_type_enum(self):
        """Test AnnotationType enum values"""
        assert hasattr(AnnotationType, 'HIGHLIGHT')
        assert hasattr(AnnotationType, 'STICKY_NOTE')
        assert hasattr(AnnotationType, 'REDACTION')
        assert hasattr(AnnotationType, 'COMMENT')


class TestGraphQLQueries:
    """Test GraphQL query resolvers"""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock GraphQL context"""
        context = MagicMock()
        
        # Mock services
        context.get = MagicMock(side_effect=lambda key, default=None: {
            "document_service": AsyncMock(),
            "entity_service": AsyncMock(),
            "annotation_service": AsyncMock(),
            "search_service": AsyncMock(),
            "rag_service": AsyncMock(),
            "current_user": MagicMock(id="user-1", email="test@example.com"),
        }.get(key, default))
        
        return context
    
    @pytest.fixture
    def mock_document(self):
        """Create mock document"""
        return MagicMock(
            id="doc-123",
            filename="test.pdf",
            mime_type="application/pdf",
            size=1024,
            status=DocumentStatus.COMPLETED,
            uploaded_by="user-1",
            uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
            page_count=10,
            confidence_score=0.95,
        )
    
    @pytest.mark.asyncio
    async def test_query_document_by_id(self, mock_context, mock_document):
        """Test querying single document by ID"""
        from backend.api.graphql.resolvers import Query
        
        # Setup mock
        document_service = mock_context.get("document_service")
        document_service.get_by_id.return_value = mock_document
        
        # Execute query
        query = Query()
        result = await query.document(info=mock_context, id="doc-123")
        
        # Assertions
        assert result.id == "doc-123"
        assert result.filename == "test.pdf"
        document_service.get_by_id.assert_called_once_with("doc-123")
    
    @pytest.mark.asyncio
    async def test_query_document_not_found(self, mock_context):
        """Test querying non-existent document"""
        from backend.api.graphql.resolvers import Query
        
        # Setup mock to return None
        document_service = mock_context.get("document_service")
        document_service.get_by_id.return_value = None
        
        # Execute query
        query = Query()
        result = await query.document(info=mock_context, id="nonexistent")
        
        # Assertions
        assert result is None
    
    @pytest.mark.asyncio
    async def test_query_documents_with_filter(self, mock_context, mock_document):
        """Test querying documents with filter"""
        from backend.api.graphql.resolvers import Query
        from backend.api.graphql.types import DocumentFilter
        
        # Setup mock
        document_service = mock_context.get("document_service")
        document_service.list_documents.return_value = [mock_document]
        
        # Create filter
        filter_input = MagicMock(
            status=DocumentStatus.COMPLETED,
            min_confidence=0.8,
        )
        
        # Execute query
        query = Query()
        results = await query.documents(
            info=mock_context,
            filter=filter_input,
            limit=20,
            offset=0,
        )
        
        # Assertions
        assert len(results) == 1
        assert results[0].id == "doc-123"
        document_service.list_documents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_search(self, mock_context, mock_document):
        """Test semantic search query"""
        from backend.api.graphql.resolvers import Query
        
        # Setup mock
        search_service = mock_context.get("search_service")
        search_result = MagicMock(
            document=mock_document,
            score=0.85,
            highlights=["match 1", "match 2"],
            matched_chunks=[],
        )
        search_service.search.return_value = [search_result]
        
        # Execute query
        query = Query()
        results = await query.search(
            info=mock_context,
            query="test search",
            limit=10,
            min_score=0.7,
        )
        
        # Assertions
        assert len(results) == 1
        assert results[0].score == 0.85
        assert len(results[0].highlights) == 2
        search_service.search.assert_called_once_with(
            query="test search",
            limit=10,
            min_score=0.7,
            filter=None,
        )
    
    @pytest.mark.asyncio
    async def test_query_rag(self, mock_context, mock_document):
        """Test RAG query"""
        from backend.api.graphql.resolvers import Query
        
        # Setup mock
        rag_service = mock_context.get("rag_service")
        rag_response = MagicMock(
            answer="The answer is 42",
            sources=[mock_document],
            confidence=0.92,
            chunks_used=[],
        )
        rag_service.query.return_value = rag_response
        
        # Execute query
        query = Query()
        result = await query.rag_query(
            info=mock_context,
            question="What is the answer?",
            max_chunks=5,
            temperature=0.7,
        )
        
        # Assertions
        assert result.answer == "The answer is 42"
        assert result.confidence == 0.92
        assert len(result.sources) == 1
        rag_service.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_entities(self, mock_context):
        """Test querying entities"""
        from backend.api.graphql.resolvers import Query
        
        # Setup mock
        entity_service = mock_context.get("entity_service")
        mock_entity = MagicMock(
            id="entity-1",
            document_id="doc-123",
            type=EntityType.MONEY,
            text="$1,000",
            confidence=0.98,
        )
        entity_service.list_entities.return_value = [mock_entity]
        
        # Execute query
        query = Query()
        results = await query.entities(
            info=mock_context,
            document_id="doc-123",
            type=EntityType.MONEY,
            limit=100,
        )
        
        # Assertions
        assert len(results) == 1
        assert results[0].type == EntityType.MONEY
        assert results[0].text == "$1,000"
    
    @pytest.mark.asyncio
    async def test_query_me(self, mock_context):
        """Test querying current user"""
        from backend.api.graphql.resolvers import Query
        
        # Execute query
        query = Query()
        result = await query.me(info=mock_context)
        
        # Assertions
        assert result is not None
        assert result.id == "user-1"
        assert result.email == "test@example.com"


class TestGraphQLMutations:
    """Test GraphQL mutation resolvers"""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock GraphQL context"""
        context = MagicMock()
        
        # Mock services
        context.get = MagicMock(side_effect=lambda key, default=None: {
            "document_service": AsyncMock(),
            "annotation_service": AsyncMock(),
            "current_user": MagicMock(id="user-1", email="test@example.com"),
        }.get(key, default))
        
        return context
    
    @pytest.mark.asyncio
    async def test_mutation_upload_document(self, mock_context):
        """Test document upload mutation"""
        from backend.api.graphql.resolvers import Mutation
        
        # Setup mocks
        mock_file = AsyncMock()
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read.return_value = b"PDF content"
        
        document_service = mock_context.get("document_service")
        mock_doc = MagicMock(
            id="doc-new",
            filename="test.pdf",
            status=DocumentStatus.PENDING,
        )
        document_service.upload.return_value = mock_doc
        
        # Execute mutation
        mutation = Mutation()
        result = await mutation.upload_document(
            info=mock_context,
            file=mock_file,
            metadata={"category": "test"},
        )
        
        # Assertions
        assert result.success is True
        assert result.document.id == "doc-new"
        assert "uploaded successfully" in result.message
        document_service.upload.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mutation_upload_without_auth(self, mock_context):
        """Test upload without authentication"""
        from backend.api.graphql.resolvers import Mutation
        
        # Remove current user
        mock_context.get = MagicMock(side_effect=lambda key, default=None: {
            "document_service": AsyncMock(),
            "current_user": None,
        }.get(key, default))
        
        mock_file = AsyncMock()
        
        # Execute mutation
        mutation = Mutation()
        result = await mutation.upload_document(
            info=mock_context,
            file=mock_file,
        )
        
        # Assertions
        assert result.success is False
        assert "Authentication required" in result.message
    
    @pytest.mark.asyncio
    async def test_mutation_delete_document(self, mock_context):
        """Test document deletion mutation"""
        from backend.api.graphql.resolvers import Mutation
        
        # Setup mock
        document_service = mock_context.get("document_service")
        document_service.get_by_id.return_value = MagicMock(id="doc-123")
        document_service.delete = AsyncMock()
        
        # Execute mutation
        mutation = Mutation()
        result = await mutation.delete_document(
            info=mock_context,
            id="doc-123",
        )
        
        # Assertions
        assert result.success is True
        assert "deleted successfully" in result.message
        document_service.delete.assert_called_once_with("doc-123")
    
    @pytest.mark.asyncio
    async def test_mutation_delete_nonexistent_document(self, mock_context):
        """Test deleting non-existent document"""
        from backend.api.graphql.resolvers import Mutation
        
        # Setup mock to return None
        document_service = mock_context.get("document_service")
        document_service.get_by_id.return_value = None
        
        # Execute mutation
        mutation = Mutation()
        result = await mutation.delete_document(
            info=mock_context,
            id="nonexistent",
        )
        
        # Assertions
        assert result.success is False
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_mutation_add_annotation(self, mock_context):
        """Test adding annotation mutation"""
        from backend.api.graphql.resolvers import Mutation
        
        # Setup mock
        annotation_service = mock_context.get("annotation_service")
        mock_annotation = MagicMock(
            id="annot-1",
            type=AnnotationType.HIGHLIGHT,
        )
        annotation_service.create.return_value = mock_annotation
        
        # Create input
        annotation_input = MagicMock(
            document_id="doc-123",
            type=AnnotationType.HIGHLIGHT,
            content="Test annotation",
            page_number=1,
            position={"x": 100, "y": 200, "width": 300, "height": 50},
            color="#FFEB3B",
        )
        
        # Execute mutation
        mutation = Mutation()
        result = await mutation.add_annotation(
            info=mock_context,
            input=annotation_input,
        )
        
        # Assertions
        assert result.success is True
        assert result.annotation.id == "annot-1"
        annotation_service.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mutation_update_annotation(self, mock_context):
        """Test updating annotation mutation"""
        from backend.api.graphql.resolvers import Mutation
        
        # Setup mock
        annotation_service = mock_context.get("annotation_service")
        
        # Existing annotation (owned by current user)
        existing = MagicMock(
            id="annot-1",
            user_id="user-1",
        )
        annotation_service.get_by_id.return_value = existing
        
        # Updated annotation
        updated = MagicMock(
            id="annot-1",
            content="Updated content",
        )
        annotation_service.update.return_value = updated
        
        # Create input
        update_input = MagicMock(
            content="Updated content",
            position=None,
            color="#4CAF50",
        )
        
        # Execute mutation
        mutation = Mutation()
        result = await mutation.update_annotation(
            info=mock_context,
            id="annot-1",
            input=update_input,
        )
        
        # Assertions
        assert result.success is True
        assert result.annotation.content == "Updated content"
    
    @pytest.mark.asyncio
    async def test_mutation_update_annotation_wrong_owner(self, mock_context):
        """Test updating annotation owned by different user"""
        from backend.api.graphql.resolvers import Mutation
        
        # Setup mock
        annotation_service = mock_context.get("annotation_service")
        
        # Existing annotation (owned by different user)
        existing = MagicMock(
            id="annot-1",
            user_id="other-user",
        )
        annotation_service.get_by_id.return_value = existing
        
        update_input = MagicMock()
        
        # Execute mutation
        mutation = Mutation()
        result = await mutation.update_annotation(
            info=mock_context,
            id="annot-1",
            input=update_input,
        )
        
        # Assertions
        assert result.success is False
        assert "your own annotations" in result.message
    
    @pytest.mark.asyncio
    async def test_mutation_delete_annotation(self, mock_context):
        """Test deleting annotation mutation"""
        from backend.api.graphql.resolvers import Mutation
        
        # Setup mock
        annotation_service = mock_context.get("annotation_service")
        
        existing = MagicMock(
            id="annot-1",
            user_id="user-1",
        )
        annotation_service.get_by_id.return_value = existing
        annotation_service.delete = AsyncMock()
        
        # Execute mutation
        mutation = Mutation()
        result = await mutation.delete_annotation(
            info=mock_context,
            id="annot-1",
        )
        
        # Assertions
        assert result.success is True
        assert "deleted successfully" in result.message
        annotation_service.delete.assert_called_once_with("annot-1")


class TestGraphQLDataLoaders:
    """Test DataLoader implementations"""
    
    @pytest.mark.asyncio
    async def test_user_dataloader(self):
        """Test UserDataLoader batches requests"""
        from backend.api.graphql.dataloaders import UserDataLoader
        
        # Mock user service
        user_service = AsyncMock()
        mock_users = [
            MagicMock(id="user-1", email="user1@example.com"),
            MagicMock(id="user-2", email="user2@example.com"),
        ]
        user_service.get_by_ids.return_value = mock_users
        
        # Create loader
        loader = UserDataLoader(user_service)
        
        # Load users
        result = await loader.load_users(["user-1", "user-2"])
        
        # Assertions
        assert len(result) == 2
        assert result[0].id == "user-1"
        assert result[1].id == "user-2"
        user_service.get_by_ids.assert_called_once_with(["user-1", "user-2"])
    
    @pytest.mark.asyncio
    async def test_entity_dataloader(self):
        """Test EntityDataLoader batches requests"""
        from backend.api.graphql.dataloaders import EntityDataLoader
        
        # Mock entity service
        entity_service = AsyncMock()
        mock_entities = [
            MagicMock(id="ent-1", document_id="doc-1"),
            MagicMock(id="ent-2", document_id="doc-1"),
            MagicMock(id="ent-3", document_id="doc-2"),
        ]
        entity_service.get_by_document_ids.return_value = mock_entities
        
        # Create loader
        loader = EntityDataLoader(entity_service)
        
        # Load entities
        result = await loader.load_entities(["doc-1", "doc-2"])
        
        # Assertions
        assert len(result) == 2
        assert len(result[0]) == 2  # doc-1 has 2 entities
        assert len(result[1]) == 1  # doc-2 has 1 entity


class TestGraphQLContext:
    """Test GraphQL context creation"""
    
    def test_context_creation(self):
        """Test creating GraphQL context"""
        from backend.api.graphql.context import GraphQLContext
        
        # Mock request
        request = MagicMock()
        
        # Mock services
        services = {
            "document_service": MagicMock(),
            "entity_service": MagicMock(),
        }
        
        # Mock user
        user = MagicMock(id="user-1")
        
        # Create context
        context = GraphQLContext(
            request=request,
            services=services,
            current_user=user,
        )
        
        # Assertions
        assert context.request == request
        assert context.current_user == user
        assert context.get("current_user") == user
        assert context.get("document_service") is not None


# Integration test marker
@pytest.mark.integration
class TestGraphQLIntegration:
    """Integration tests for GraphQL API (requires running server)"""
    
    @pytest.mark.skip(reason="Requires running server")
    async def test_graphql_endpoint(self):
        """Test GraphQL endpoint is accessible"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/graphql/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
    
    @pytest.mark.skip(reason="Requires running server")
    async def test_graphql_query(self):
        """Test executing GraphQL query"""
        import httpx
        
        query = """
            query {
                me {
                    email
                }
            }
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/graphql/",
                json={"query": query},
                headers={"Authorization": "Bearer test-token"},
            )
            assert response.status_code == 200
