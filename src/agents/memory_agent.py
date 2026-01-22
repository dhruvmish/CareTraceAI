"""
MemoryAgent: Single source of truth for Qdrant operations

Responsibilities:
- Store events in patient_events collection
- Retrieve patient history
- Search by similarity
- Filter by patient_id, date range, event type
- Delete/Edit events (NEW)
- All other agents must use MemoryAgent to access data
"""

from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
import uuid
from src.db.qdrant_client import QdrantConnection
from src.config import (
    COLLECTION_PATIENT_EVENTS,
    COLLECTION_DRUG_INTERACTIONS,
    COLLECTION_SYNTHETIC_PATIENTS,
    EMBEDDING_MODEL
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class MemoryAgent:
    """Agent responsible for all Qdrant memory operations"""

    def __init__(self):
        """Initialize embedding model and Qdrant client"""
        try:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
            self.encoder = SentenceTransformer(EMBEDDING_MODEL)
            self.client = QdrantConnection.get_client()
            logger.info("✅ MemoryAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MemoryAgent: {str(e)}")
            raise

    def store_event(self, event: Dict[str, Any]) -> str:
        """
        Store a patient event in Qdrant

        Args:
            event: Event dict from IngestionAgent

        Returns:
            Point ID (UUID)
        """
        try:
            # Generate embedding from event text
            embedding = self.encoder.encode(event["text"]).tolist()

            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=event
            )

            self.client.upsert(
                collection_name=COLLECTION_PATIENT_EVENTS,
                points=[point]
            )

            logger.info(f"✅ Stored event for patient {event['patient_id']}: {event['event_type']} (ID: {point_id})")
            return point_id

        except Exception as e:
            logger.error(f"❌ Failed to store event: {str(e)}")
            raise

    def get_patient_history(
        self,
        patient_id: str,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all events for a patient

        Args:
            patient_id: Patient identifier
            event_type: Optional filter ("symptom" or "prescription")
            limit: Maximum number of results

        Returns:
            List of events with point_ids, sorted by timestamp (newest first)
        """
        try:
            # Build filter
            conditions = [
                FieldCondition(key="patient_id", match=MatchValue(value=patient_id))
            ]

            if event_type:
                conditions.append(
                    FieldCondition(key="event_type", match=MatchValue(value=event_type))
                )

            filter_obj = Filter(must=conditions)

            # Search with filter (using scroll to get all matches)
            results = self.client.scroll(
                collection_name=COLLECTION_PATIENT_EVENTS,
                scroll_filter=filter_obj,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )[0]  # scroll returns (records, next_page_offset)

            # Include point_id in each event for deletion/editing
            events = []
            for r in results:
                event = r.payload.copy()
                event['point_id'] = r.id  # Add point_id to payload
                events.append(event)

            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            logger.info(f"Retrieved {len(events)} events for patient {patient_id}")
            return events

        except Exception as e:
            logger.error(f"❌ Failed to retrieve history: {str(e)}")
            return []

    def delete_event(self, point_id: str) -> bool:
        """
        Delete a specific event by point ID

        Args:
            point_id: Qdrant point ID (UUID)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete(
                collection_name=COLLECTION_PATIENT_EVENTS,
                points_selector=[point_id]
            )
            logger.info(f"✅ Deleted event: {point_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete event {point_id}: {str(e)}")
            return False

    def update_event(self, point_id: str, updated_event: Dict[str, Any]) -> bool:
        """
        Update an existing event

        Args:
            point_id: Qdrant point ID to update
            updated_event: New event data

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate new embedding from updated text
            embedding = self.encoder.encode(updated_event["text"]).tolist()

            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=updated_event
            )

            self.client.upsert(
                collection_name=COLLECTION_PATIENT_EVENTS,
                points=[point]
            )

            logger.info(f"✅ Updated event: {point_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update event {point_id}: {str(e)}")
            return False

    def get_event_by_id(self, point_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific event by point ID

        Args:
            point_id: Qdrant point ID

        Returns:
            Event dict or None if not found
        """
        try:
            result = self.client.retrieve(
                collection_name=COLLECTION_PATIENT_EVENTS,
                ids=[point_id],
                with_payload=True,
                with_vectors=False
            )

            if result:
                event = result[0].payload.copy()
                event['point_id'] = result[0].id
                return event
            return None

        except Exception as e:
            logger.error(f"❌ Failed to retrieve event {point_id}: {str(e)}")
            return None

    def search_similar_symptoms(
        self,
        query_text: str,
        patient_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar symptom reports using semantic search

        Args:
            query_text: Symptom description to search for
            patient_id: Optional - limit to specific patient
            limit: Number of results

        Returns:
            List of similar symptom events with scores and point_ids
        """
        try:
            query_embedding = self.encoder.encode(query_text).tolist()

            # Build filter if patient_id provided
            filter_obj = None
            if patient_id:
                filter_obj = Filter(
                    must=[
                        FieldCondition(key="patient_id", match=MatchValue(value=patient_id)),
                        FieldCondition(key="event_type", match=MatchValue(value="symptom"))
                    ]
                )
            else:
                filter_obj = Filter(
                    must=[FieldCondition(key="event_type", match=MatchValue(value="symptom"))]
                )

            results = self.client.search(
                collection_name=COLLECTION_PATIENT_EVENTS,
                query_vector=query_embedding,
                query_filter=filter_obj,
                limit=limit
            )

            matches = [
                {
                    **r.payload,
                    "similarity_score": r.score,
                    "point_id": r.id
                }
                for r in results
            ]

            logger.info(f"Found {len(matches)} similar symptoms")
            return matches

        except Exception as e:
            logger.error(f"❌ Similarity search failed: {str(e)}")
            return []

    def store_drug_interaction(self, interaction: Dict[str, Any]) -> str:
        """
        Store a drug-drug interaction
        Guarantees 'explanation' exists for UI compatibility
        """
        try:
            # 🔒 BACKWARD COMPATIBILITY GUARANTEE
            if "explanation" not in interaction:
                interaction["explanation"] = interaction.get("description", "")

            text = f"{interaction['drug_a']} and {interaction['drug_b']}: {interaction['explanation']}"
            embedding = self.encoder.encode(text).tolist()

            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=interaction
            )

            self.client.upsert(
                collection_name=COLLECTION_DRUG_INTERACTIONS,
                points=[point]
            )

            logger.info(f"✅ Stored interaction: {interaction['drug_a']} ↔ {interaction['drug_b']}")
            return point_id

        except Exception as e:
            logger.error(f"❌ Failed to store interaction: {str(e)}")
            raise

    def get_all_drug_interactions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all drug-drug interactions
        Required by SafetyAgent
        """
        try:
            results = self.client.scroll(
                collection_name=COLLECTION_DRUG_INTERACTIONS,
                limit=1000,
                with_payload=True,
                with_vectors=False
            )[0]

            interactions = []
            for r in results:
                interaction = r.payload.copy()

                # 🔒 HARD GUARANTEE for Streamlit UI
                if "explanation" not in interaction:
                    interaction["explanation"] = interaction.get("description", "")

                interactions.append(interaction)

            logger.info(f"Retrieved {len(interactions)} drug interactions")
            return interactions

        except Exception as e:
            logger.error(f"❌ Failed to retrieve interactions: {str(e)}")
            return []

    def search_similar_patients(self, query_text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Find similar patients based on conditions/medications/symptoms

        Args:
            query_text: Patient summary to match against
            limit: Number of similar patients to return

        Returns:
            List of similar patient profiles with scores
        """
        try:
            query_embedding = self.encoder.encode(query_text).tolist()

            results = self.client.search_points(
                collection_name=COLLECTION_SYNTHETIC_PATIENTS,
                vector=query_embedding,
                limit=limit
            )

            matches = [
                {
                    **r.payload,
                    "similarity_score": r.score
                }
                for r in results
            ]

            logger.info(f"Found {len(matches)} similar patients")
            return matches

        except Exception as e:
            logger.error(f"❌ Patient similarity search failed: {str(e)}")
            return []