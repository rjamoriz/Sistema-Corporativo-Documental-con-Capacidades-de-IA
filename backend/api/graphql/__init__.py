"""
GraphQL API Module
Provides GraphQL schema and resolvers for FinancIA document system.
"""

from .schema import schema
from .types import (
    Document,
    Entity,
    Chunk,
    Annotation,
    User,
    DocumentConnection,
    SearchResult,
)
from .resolvers import Query, Mutation

__all__ = [
    "schema",
    "Document",
    "Entity",
    "Chunk",
    "Annotation",
    "User",
    "DocumentConnection",
    "SearchResult",
    "Query",
    "Mutation",
]
