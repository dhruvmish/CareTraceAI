"""
Setup script: Initialize Qdrant collections
Run this FIRST before using the system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.qdrant_client import QdrantConnection
from src.db.collections import create_collections
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Initialize all Qdrant collections"""
    logger.info("=" * 60)
    logger.info("CareTrace AI - Qdrant Setup")
    logger.info("=" * 60)
    
    try:
        # Test connection
        logger.info("Testing Qdrant connection...")
        client = QdrantConnection.get_client()
        
        # Create collections
        logger.info("\nCreating collections...")
        create_collections()
        
        # Verify
        collections = client.get_collections()
        logger.info(f"\n✅ Setup complete! Active collections: {len(collections.collections)}")
        for coll in collections.collections:
            logger.info(f"   - {coll.name}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Next steps:")
        logger.info("1. Run: python scripts/generate_synthetic_patients.py")
        logger.info("2. Add audio files to data/audio/")
        logger.info("3. Add prescription images to data/prescriptions/")
        logger.info("4. Run: streamlit run src/ui/app.py")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ Setup failed: {str(e)}")
        logger.error("\nTroubleshooting:")
        logger.error("- Ensure Qdrant is running (docker or cloud)")
        logger.error("- Check your .env file has correct QDRANT_URL")
        logger.error("- For local: docker run -p 6333:6333 qdrant/qdrant")
        sys.exit(1)

if __name__ == "__main__":
    main()