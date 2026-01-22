"""
Migration script: Add point_ids to existing events
Run this if you have events created before the edit/delete feature was added
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.qdrant_client import QdrantConnection
from src.config import COLLECTION_PATIENT_EVENTS
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def migrate_add_point_ids():
    """
    Add point_id to all events that don't have it in their payload
    This is a one-time migration for events created before edit feature
    """
    logger.info("=" * 60)
    logger.info("Migration: Adding point_ids to existing events")
    logger.info("=" * 60)

    try:
        client = QdrantConnection.get_client()

        # Get all events
        logger.info("Retrieving all events...")
        results = client.scroll(
            collection_name=COLLECTION_PATIENT_EVENTS,
            limit=10000,
            with_payload=True,
            with_vectors=False
        )[0]

        logger.info(f"Found {len(results)} total events")

        # Check which events need point_id added to payload
        needs_update = []
        already_has = 0

        for record in results:
            if "point_id" not in record.payload:
                needs_update.append(record)
            else:
                already_has += 1

        logger.info(f"Events already have point_id in payload: {already_has}")
        logger.info(f"Events needing migration: {len(needs_update)}")

        if not needs_update:
            logger.info("✅ All events already have point_ids. No migration needed.")
            return

        # Update events by adding point_id to their payload
        logger.info(f"\nMigrating {len(needs_update)} events...")

        from qdrant_client.models import PointStruct

        points_to_update = []
        for record in needs_update:
            # Add point_id to payload
            updated_payload = record.payload.copy()
            updated_payload["point_id"] = record.id

            point = PointStruct(
                id=record.id,
                vector=record.vector,
                payload=updated_payload
            )
            points_to_update.append(point)

        # Batch upsert
        client.upsert(
            collection_name=COLLECTION_PATIENT_EVENTS,
            points=points_to_update
        )

        logger.info(f"✅ Successfully migrated {len(points_to_update)} events")
        logger.info("\n" + "=" * 60)
        logger.info("Migration complete! All events now have point_ids.")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    migrate_add_point_ids()