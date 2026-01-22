"""
Qdrant collection schemas and initialization
Defines the structure of all 3 required collections
"""

from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any
from src.db.qdrant_client import QdrantConnection
from src.config import (
    EMBEDDING_DIM,
    COLLECTION_PATIENT_EVENTS,
    COLLECTION_DRUG_INTERACTIONS,
    COLLECTION_SYNTHETIC_PATIENTS
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def create_collections():
    """
    Initialize all required Qdrant collections
    Safe to run multiple times (checks if exists)
    """
    client = QdrantConnection.get_client()
    
    collections = [
        {
            "name": COLLECTION_PATIENT_EVENTS,
            "description": "Patient symptom reports and prescription events",
            "vector_size": EMBEDDING_DIM
        },
        {
            "name": COLLECTION_DRUG_INTERACTIONS,
            "description": "Known drug-drug interactions database",
            "vector_size": EMBEDDING_DIM
        },
        {
            "name": COLLECTION_SYNTHETIC_PATIENTS,
            "description": "Synthetic patient population for similarity matching",
            "vector_size": EMBEDDING_DIM
        }
    ]
    
    for coll in collections:
        try:
            if not client.collection_exists(coll["name"]):
                client.create_collection(
                    collection_name=coll["name"],
                    vectors_config=VectorParams(
                        size=coll["vector_size"],
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created collection: {coll['name']}")
            else:
                logger.info(f"⏭️  Collection already exists: {coll['name']}")
        except Exception as e:
            logger.error(f"❌ Failed to create {coll['name']}: {str(e)}")
            raise

def get_patient_event_schema() -> Dict[str, Any]:
    """
    Schema for patient_events collection
    
    Payload structure:
    - patient_id: str
    - event_type: "symptom" | "prescription"
    - text: str (symptom description or drug list)
    - timestamp: str (ISO format)
    - drugs: List[str] (for prescriptions)
    - metadata: dict (additional context)
    """
    return {
        "patient_id": "string",
        "event_type": "string",
        "text": "string",
        "timestamp": "string",
        "drugs": "list[string]",
        "metadata": "dict"
    }

def get_drug_interaction_schema() -> Dict[str, Any]:
    """
    Schema for drug_interactions collection
    
    Payload structure:
    - drug_a: str
    - drug_b: str
    - severity: "mild" | "moderate" | "severe"
    - explanation: str
    - evidence: str (source/citation)
    """
    return {
        "drug_a": "string",
        "drug_b": "string",
        "severity": "string",
        "explanation": "string",
        "evidence": "string"
    }

def get_synthetic_patient_schema() -> Dict[str, Any]:
    """
    Schema for synthetic_patient_profiles collection
    
    Payload structure:
    - patient_id: str
    - age: int
    - conditions: List[str]
    - medications: List[str]
    - symptoms: List[str]
    - summary: str (for embedding)
    """
    return {
        "patient_id": "string",
        "age": "int",
        "conditions": "list[string]",
        "medications": "list[string]",
        "symptoms": "list[string]",
        "summary": "string"
    }

def delete_all_collections():
    """Delete all collections (use with caution!)"""
    client = QdrantConnection.get_client()
    
    for coll_name in [COLLECTION_PATIENT_EVENTS, 
                      COLLECTION_DRUG_INTERACTIONS, 
                      COLLECTION_SYNTHETIC_PATIENTS]:
        try:
            if client.collection_exists(coll_name):
                client.delete_collection(coll_name)
                logger.warning(f"🗑️  Deleted collection: {coll_name}")
        except Exception as e:
            logger.error(f"Failed to delete {coll_name}: {str(e)}")