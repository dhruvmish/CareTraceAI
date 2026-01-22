"""
Qdrant client initialization
Single source of truth for database connection
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from typing import Optional
from src.config import QDRANT_URL, QDRANT_API_KEY, EMBEDDING_DIM
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class QdrantConnection:
    """Singleton Qdrant client"""
    
    _instance: Optional[QdrantClient] = None
    
    @classmethod
    def get_client(cls) -> QdrantClient:
        """
        Get or create Qdrant client
        
        Returns:
            QdrantClient instance
        
        Raises:
            ConnectionError: If cannot connect to Qdrant
        """
        if cls._instance is None:
            try:
                logger.info(f"Connecting to Qdrant at {QDRANT_URL}")
                cls._instance = QdrantClient(
                    url=QDRANT_URL,
                    api_key=QDRANT_API_KEY,
                    timeout=10
                )
                # Test connection
                cls._instance.get_collections()
                logger.info("✅ Successfully connected to Qdrant")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Qdrant: {str(e)}")
                raise ConnectionError(f"Cannot connect to Qdrant at {QDRANT_URL}. "
                                    f"Please check your .env file and ensure Qdrant is running.")
        
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset connection (mainly for testing)"""
        cls._instance = None