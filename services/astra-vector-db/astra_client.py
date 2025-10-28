"""
DataStax Astra DB Client
Handles connection and operations with Astra DB
"""
import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from astrapy.db import AstraDB
from astrapy.ops import AstraDBOps

logger = logging.getLogger(__name__)


class AstraVectorClient:
    """
    Client for DataStax Astra DB Vector Operations
    
    Features:
    - Vector similarity search
    - CRUD operations
    - Metadata filtering
    - Batch operations
    """
    
    def __init__(
        self,
        token: str,
        api_endpoint: str,
        namespace: str = "default_keyspace",
        collection_name: str = "documents"
    ):
        """
        Initialize Astra DB client
        
        Args:
            token: Astra DB application token
            api_endpoint: Astra DB API endpoint
            namespace: Keyspace/namespace name
            collection_name: Collection name for vectors
        """
        self.token = token
        self.api_endpoint = api_endpoint
        self.namespace = namespace
        self.collection_name = collection_name
        
        # Initialize clients
        self.db = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Astra DB connection"""
        try:
            # Initialize AstraDB
            self.db = AstraDB(
                token=self.token,
                api_endpoint=self.api_endpoint,
                namespace=self.namespace
            )
            
            # Get or create collection
            self.collection = self.db.collection(self.collection_name)
            
            logger.info(f"✅ Connected to Astra DB: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Astra DB: {e}")
            raise
    
    def create_collection(self, dimension: int = 1536):
        """
        Create vector collection if it doesn't exist
        
        Args:
            dimension: Vector dimension (default 1536 for OpenAI ada-002)
        """
        try:
            # Create collection with vector support
            self.db.create_collection(
                collection_name=self.collection_name,
                dimension=dimension,
                metric="cosine"  # or "euclidean", "dot_product"
            )
            logger.info(f"✅ Collection created: {self.collection_name}")
            
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"ℹ️ Collection already exists: {self.collection_name}")
            else:
                logger.error(f"❌ Error creating collection: {e}")
                raise
    
    async def insert_document(
        self,
        document_id: str,
        vector: List[float],
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Insert document with vector
        
        Returns:
            Document ID
        """
        try:
            doc = {
                "_id": document_id,
                "$vector": vector,
                "content": content,
                "metadata": metadata,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": None
            }
            
            result = self.collection.insert_one(doc)
            logger.info(f"✅ Document inserted: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"❌ Error inserting document: {e}")
            raise
    
    async def insert_many(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Batch insert documents
        
        Returns:
            List of document IDs
        """
        try:
            # Prepare documents
            docs = []
            for doc in documents:
                docs.append({
                    "_id": doc.get("id", str(uuid.uuid4())),
                    "$vector": doc["vector"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "created_at": datetime.utcnow().isoformat()
                })
            
            result = self.collection.insert_many(docs)
            logger.info(f"✅ Batch inserted: {len(docs)} documents")
            return [doc["_id"] for doc in docs]
            
        except Exception as e:
            logger.error(f"❌ Error in batch insert: {e}")
            raise
    
    async def vector_search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            metadata_filter: Optional metadata filters
        
        Returns:
            List of matching documents with scores
        """
        try:
            # Build query
            query = {
                "sort": {"$vector": query_vector},
                "limit": top_k
            }
            
            # Add metadata filter if provided
            if metadata_filter:
                query["filter"] = metadata_filter
            
            # Execute search
            results = self.collection.find(**query)
            
            # Format results
            formatted_results = []
            for idx, doc in enumerate(results):
                formatted_results.append({
                    "id": doc["_id"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "similarity_score": doc.get("$similarity", 0.0),
                    "rank": idx + 1
                })
            
            logger.info(f"✅ Vector search: {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error in vector search: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        try:
            doc = self.collection.find_one({"_id": document_id})
            return doc if doc else None
            
        except Exception as e:
            logger.error(f"❌ Error getting document: {e}")
            raise
    
    async def update_document(
        self,
        document_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update document
        
        Returns:
            True if successful
        """
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.collection.update_one(
                {"_id": document_id},
                {"$set": updates}
            )
            
            logger.info(f"✅ Document updated: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating document: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document
        
        Returns:
            True if successful
        """
        try:
            result = self.collection.delete_one({"_id": document_id})
            logger.info(f"✅ Document deleted: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting document: {e}")
            raise
    
    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 20,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        List documents with pagination
        
        Returns:
            (documents, total_count)
        """
        try:
            query = metadata_filter or {}
            
            # Get documents
            cursor = self.collection.find(
                query,
                skip=skip,
                limit=limit
            )
            documents = list(cursor)
            
            # Get total count
            total = self.collection.count_documents(query)
            
            logger.info(f"✅ Listed {len(documents)} documents (total: {total})")
            return documents, total
            
        except Exception as e:
            logger.error(f"❌ Error listing documents: {e}")
            raise
    
    async def count_documents(
        self,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count documents"""
        try:
            query = metadata_filter or {}
            count = self.collection.count_documents(query)
            return count
            
        except Exception as e:
            logger.error(f"❌ Error counting documents: {e}")
            raise
    
    async def delete_collection(self):
        """Delete entire collection (use with caution!)"""
        try:
            self.db.delete_collection(self.collection_name)
            logger.warning(f"⚠️ Collection deleted: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"❌ Error deleting collection: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check connection health"""
        try:
            # Try to count documents
            count = self.collection.count_documents({})
            
            return {
                "status": "healthy",
                "connected": True,
                "collection": self.collection_name,
                "document_count": count
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
