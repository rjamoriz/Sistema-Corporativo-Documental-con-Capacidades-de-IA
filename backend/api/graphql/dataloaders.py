"""
GraphQL DataLoaders
Implements DataLoader pattern to prevent N+1 query problems.
"""

from typing import List, Optional, Dict, Any
from collections import defaultdict
from strawberry.dataloader import DataLoader


class UserDataLoader:
    """DataLoader for users to batch load by IDs"""
    
    def __init__(self, user_service):
        self.user_service = user_service
        self.loader = DataLoader(load_fn=self.load_users)
    
    async def load_users(self, keys: List[str]) -> List[Optional[Any]]:
        """
        Batch load users by IDs.
        
        Args:
            keys: List of user IDs
            
        Returns:
            List of users in same order as keys
        """
        # Fetch all users in one query
        users = await self.user_service.get_by_ids(keys)
        
        # Create lookup dict
        user_map = {user.id: user for user in users}
        
        # Return in same order as keys
        return [user_map.get(key) for key in keys]


class EntityDataLoader:
    """DataLoader for entities by document ID"""
    
    def __init__(self, entity_service):
        self.entity_service = entity_service
        self.loader = DataLoader(load_fn=self.load_entities)
    
    async def load_entities(self, keys: List[str]) -> List[List[Any]]:
        """
        Batch load entities by document IDs.
        
        Args:
            keys: List of document IDs
            
        Returns:
            List of entity lists, one per document
        """
        # Fetch all entities for all documents in one query
        entities = await self.entity_service.get_by_document_ids(keys)
        
        # Group by document_id
        entity_map = defaultdict(list)
        for entity in entities:
            entity_map[entity.document_id].append(entity)
        
        # Return in same order as keys
        return [entity_map.get(key, []) for key in keys]


class ChunkDataLoader:
    """DataLoader for chunks by document ID"""
    
    def __init__(self, chunk_service):
        self.chunk_service = chunk_service
        self.loader = DataLoader(load_fn=self.load_chunks)
    
    async def load_chunks(self, keys: List[str]) -> List[List[Any]]:
        """
        Batch load chunks by document IDs.
        
        Args:
            keys: List of document IDs
            
        Returns:
            List of chunk lists, one per document
        """
        # Fetch all chunks for all documents in one query
        chunks = await self.chunk_service.get_by_document_ids(keys)
        
        # Group by document_id
        chunk_map = defaultdict(list)
        for chunk in chunks:
            chunk_map[chunk.document_id].append(chunk)
        
        # Return in same order as keys
        return [chunk_map.get(key, []) for key in keys]


class AnnotationDataLoader:
    """DataLoader for annotations by document ID"""
    
    def __init__(self, annotation_service):
        self.annotation_service = annotation_service
        self.loader = DataLoader(load_fn=self.load_annotations)
    
    async def load_annotations(self, keys: List[str]) -> List[List[Any]]:
        """
        Batch load annotations by document IDs.
        
        Args:
            keys: List of document IDs
            
        Returns:
            List of annotation lists, one per document
        """
        # Fetch all annotations for all documents in one query
        annotations = await self.annotation_service.get_by_document_ids(keys)
        
        # Group by document_id
        annotation_map = defaultdict(list)
        for annotation in annotations:
            annotation_map[annotation.document_id].append(annotation)
        
        # Return in same order as keys
        return [annotation_map.get(key, []) for key in keys]


class ValidationResultDataLoader:
    """DataLoader for validation results by document ID"""
    
    def __init__(self, validation_service):
        self.validation_service = validation_service
        self.loader = DataLoader(load_fn=self.load_results)
    
    async def load_results(self, keys: List[str]) -> List[List[Any]]:
        """
        Batch load validation results by document IDs.
        
        Args:
            keys: List of document IDs
            
        Returns:
            List of validation result lists, one per document
        """
        # Fetch all results for all documents in one query
        results = await self.validation_service.get_results_by_document_ids(keys)
        
        # Group by document_id
        result_map = defaultdict(list)
        for result in results:
            result_map[result.document_id].append(result)
        
        # Return in same order as keys
        return [result_map.get(key, []) for key in keys]


def create_dataloaders(context: Dict[str, Any]) -> Dict[str, DataLoader]:
    """
    Create all dataloaders for GraphQL context.
    
    Args:
        context: Application context with services
        
    Returns:
        Dict of dataloaders
    """
    dataloaders = {}
    
    # User loader
    if "user_service" in context:
        user_loader = UserDataLoader(context["user_service"])
        dataloaders["user_loader"] = user_loader.loader
    
    # Entity loader
    if "entity_service" in context:
        entity_loader = EntityDataLoader(context["entity_service"])
        dataloaders["entity_loader"] = entity_loader.loader
    
    # Chunk loader
    if "chunk_service" in context:
        chunk_loader = ChunkDataLoader(context["chunk_service"])
        dataloaders["chunk_loader"] = chunk_loader.loader
    
    # Annotation loader
    if "annotation_service" in context:
        annotation_loader = AnnotationDataLoader(context["annotation_service"])
        dataloaders["annotation_loader"] = annotation_loader.loader
    
    # Validation result loader
    if "validation_service" in context:
        validation_loader = ValidationResultDataLoader(context["validation_service"])
        dataloaders["validation_loader"] = validation_loader.loader
    
    return dataloaders
