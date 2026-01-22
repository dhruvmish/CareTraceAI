"""
Load demo patient data and drug interactions
Populates the system with realistic demo scenarios
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.memory_agent import MemoryAgent
from src.agents.ingestion_agent import IngestionAgent
from src.config import PATIENT_STORIES_DIR
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Known drug-drug interactions (curated)
DRUG_INTERACTIONS = [
    {
        "drug_a": "Warfarin",
        "drug_b": "Aspirin",
        "severity": "severe",
        "explanation": "Increased risk of bleeding. Both drugs affect blood clotting.",
        "evidence": "FDA drug interaction database"
    },
    {
        "drug_a": "Lisinopril",
        "drug_b": "Ibuprofen",
        "severity": "moderate",
        "explanation": "NSAIDs may reduce the effectiveness of ACE inhibitors and increase kidney stress.",
        "evidence": "Clinical pharmacology literature"
    },
    {
        "drug_a": "Metformin",
        "drug_b": "Furosemide",
        "severity": "moderate",
        "explanation": "Diuretics can increase risk of lactic acidosis with Metformin.",
        "evidence": "Drug interaction compendia"
    },
    {
        "drug_a": "Simvastatin",
        "drug_b": "Amlodipine",
        "severity": "moderate",
        "explanation": "Amlodipine increases Simvastatin levels, raising risk of muscle damage.",
        "evidence": "Pharmacokinetic studies"
    },
    {
        "drug_a": "Clopidogrel",
        "drug_b": "Omeprazole",
        "severity": "moderate",
        "explanation": "Omeprazole reduces Clopidogrel effectiveness for preventing blood clots.",
        "evidence": "FDA warning 2009"
    },
    {
        "drug_a": "Prednisone",
        "drug_b": "Aspirin",
        "severity": "moderate",
        "explanation": "Both increase risk of stomach ulcers and GI bleeding.",
        "evidence": "Clinical guidelines"
    }
]

# Demo patient timelines
DEMO_PATIENTS = [
    {
        "patient_id": "patient_001",
        "name": "Sarah Johnson",
        "events": [
            {
                "type": "prescription",
                "text": "Metformin 500mg twice daily, Lisinopril 10mg daily",
                "drugs": ["Metformin", "Lisinopril"],
                "days_ago": 30
            },
            {
                "type": "symptom",
                "text": "Having headaches for the past 3 days, feeling tired",
                "days_ago": 15
            },
            {
                "type": "symptom",
                "text": "Headache is still there, also feeling dizzy when standing up",
                "days_ago": 12
            },
            {
                "type": "prescription",
                "text": "Ibuprofen 400mg as needed for headaches",
                "drugs": ["Ibuprofen"],
                "days_ago": 10
            },
            {
                "type": "symptom",
                "text": "Headache improved but now having stomach discomfort",
                "days_ago": 5
            }
        ]
    },
    {
        "patient_id": "patient_002",
        "name": "Rajesh Kumar",
        "events": [
            {
                "type": "prescription",
                "text": "Aspirin 100mg daily, Atorvastatin 20mg nightly",
                "drugs": ["Aspirin", "Atorvastatin"],
                "days_ago": 60
            },
            {
                "type": "symptom",
                "text": "Chest pain during walking, shortness of breath",
                "days_ago": 20
            },
            {
                "type": "prescription",
                "text": "Warfarin 5mg daily for atrial fibrillation",
                "drugs": ["Warfarin"],
                "days_ago": 15
            },
            {
                "type": "symptom",
                "text": "Notice bruising easily, small cut took long time to stop bleeding",
                "days_ago": 8
            }
        ]
    },
    {
        "patient_id": "patient_003",
        "name": "Maria Garcia",
        "events": [
            {
                "type": "prescription",
                "text": "Albuterol inhaler as needed",
                "drugs": ["Albuterol"],
                "days_ago": 90
            },
            {
                "type": "symptom",
                "text": "Wheezing and cough getting worse over past week",
                "days_ago": 10
            },
            {
                "type": "prescription",
                "text": "Prednisone 20mg daily for 5 days",
                "drugs": ["Prednisone"],
                "days_ago": 8
            },
            {
                "type": "symptom",
                "text": "Breathing better but having stomach upset and heartburn",
                "days_ago": 4
            }
        ]
    }
]

def load_drug_interactions(memory: MemoryAgent):
    """Load curated drug interactions"""
    logger.info("Loading drug interaction database...")
    
    for interaction in DRUG_INTERACTIONS:
        memory.store_drug_interaction(interaction)
    
    logger.info(f"✅ Loaded {len(DRUG_INTERACTIONS)} drug interactions")

def load_patient_timelines(memory: MemoryAgent, ingestion: IngestionAgent):
    """Load demo patient timelines"""
    logger.info("\nLoading demo patient timelines...")
    
    for patient in DEMO_PATIENTS:
        logger.info(f"\n  Loading patient: {patient['name']} ({patient['patient_id']})")
        
        for event in patient["events"]:
            # Calculate timestamp
            timestamp = (datetime.utcnow() - timedelta(days=event["days_ago"])).isoformat()
            
            # Create event
            event_data = {
                "patient_id": patient["patient_id"],
                "event_type": event["type"],
                "text": event["text"],
                "timestamp": timestamp,
                "drugs": event.get("drugs", []),
                "metadata": {"source": "demo_timeline"}
            }
            
            memory.store_event(event_data)
        
        logger.info(f"    ✓ Loaded {len(patient['events'])} events")
    
    logger.info(f"\n✅ Loaded {len(DEMO_PATIENTS)} patient timelines")

def main():
    """Main ingestion workflow"""
    logger.info("=" * 60)
    logger.info("Ingesting Demo Data")
    logger.info("=" * 60)
    
    try:
        memory = MemoryAgent()
        ingestion = IngestionAgent()
        
        # Load drug interactions
        load_drug_interactions(memory)
        
        # Load patient timelines
        load_patient_timelines(memory, ingestion)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Demo data ingestion complete!")
        logger.info("=" * 60)
        logger.info("\nYou can now:")
        logger.info("1. Run: streamlit run src/ui/app.py")
        logger.info("2. Select a demo patient to view their timeline")
        logger.info("3. Test safety checks and pattern detection")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ Failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()