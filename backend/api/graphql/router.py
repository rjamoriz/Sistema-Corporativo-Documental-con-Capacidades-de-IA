"""
GraphQL Router
FastAPI router for GraphQL endpoint with Strawberry integration.
"""

from typing import Optional
from fastapi import APIRouter, Request
from strawberry.fastapi import GraphQLRouter as StrawberryGraphQLRouter

from .schema import schema
from .context import get_graphql_context, GraphQLContext


# Custom GraphQL router with context
class FinanciaGraphQLRouter(StrawberryGraphQLRouter):
    """Custom GraphQL router with FinancIA context"""
    
    async def get_context(
        self,
        request: Request,
        response = None,
    ) -> GraphQLContext:
        """
        Get context for GraphQL execution.
        
        Override this method to customize context creation.
        For now, returns a basic context. In production, you would:
        1. Extract authentication from request headers
        2. Inject all required services
        3. Add user permissions
        
        Args:
            request: FastAPI request
            response: FastAPI response (optional)
            
        Returns:
            GraphQL context
        """
        # TODO: Extract user from JWT token in Authorization header
        # auth_header = request.headers.get("Authorization")
        # current_user = await authenticate_user(auth_header)
        
        # For now, mock services (replace with real service injection)
        context = await get_graphql_context(
            request=request,
            # Services should be injected via dependency injection
            # document_service=...,
            # entity_service=...,
            # etc.
        )
        
        return context


# Create the main GraphQL router using Strawberry
# This is the complete GraphQL endpoint
graphql_router = FinanciaGraphQLRouter(
    schema=schema,
    graphiql=True,  # Enable GraphQL Playground in development
    path="/",  # Path relative to where it's mounted
)

# Export as 'router' for compatibility with existing imports
router = graphql_router
