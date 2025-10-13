"""
GraphQL Context
Provides context for GraphQL resolvers including services and dataloaders.
"""

from typing import Dict, Any, Optional
from fastapi import Request
from .dataloaders import create_dataloaders


class GraphQLContext:
    """GraphQL execution context"""
    
    def __init__(
        self,
        request: Request,
        services: Dict[str, Any],
        current_user: Optional[Any] = None,
    ):
        """
        Initialize GraphQL context.
        
        Args:
            request: FastAPI request object
            services: Dictionary of application services
            current_user: Current authenticated user (if any)
        """
        self.request = request
        self.current_user = current_user
        
        # Add services to context
        self.document_service = services.get("document_service")
        self.entity_service = services.get("entity_service")
        self.chunk_service = services.get("chunk_service")
        self.annotation_service = services.get("annotation_service")
        self.validation_service = services.get("validation_service")
        self.search_service = services.get("search_service")
        self.rag_service = services.get("rag_service")
        self.user_service = services.get("user_service")
        
        # Create dataloaders
        self.dataloaders = create_dataloaders({
            "user_service": self.user_service,
            "entity_service": self.entity_service,
            "chunk_service": self.chunk_service,
            "annotation_service": self.annotation_service,
            "validation_service": self.validation_service,
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from context by key.
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Context value or default
        """
        if key == "current_user":
            return self.current_user
        elif key == "request":
            return self.request
        elif key.endswith("_service"):
            return getattr(self, key, default)
        elif key.endswith("_loader"):
            return self.dataloaders.get(key, default)
        return default


async def get_graphql_context(
    request: Request,
    # Services will be injected here
    document_service: Any = None,
    entity_service: Any = None,
    chunk_service: Any = None,
    annotation_service: Any = None,
    validation_service: Any = None,
    search_service: Any = None,
    rag_service: Any = None,
    user_service: Any = None,
    current_user: Optional[Any] = None,
) -> GraphQLContext:
    """
    Create GraphQL context for each request.
    
    Args:
        request: FastAPI request
        *_service: Application services
        current_user: Authenticated user
        
    Returns:
        GraphQL context
    """
    services = {
        "document_service": document_service,
        "entity_service": entity_service,
        "chunk_service": chunk_service,
        "annotation_service": annotation_service,
        "validation_service": validation_service,
        "search_service": search_service,
        "rag_service": rag_service,
        "user_service": user_service,
    }
    
    return GraphQLContext(
        request=request,
        services=services,
        current_user=current_user,
    )
