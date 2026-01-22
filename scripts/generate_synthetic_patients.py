"""
Generate synthetic patient population
Creates diverse patient profiles for similarity matching
"""

import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.memory_agent import MemoryAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Synthetic data templates
COMMON_CONDITIONS = [
    "Type 2 Diabetes",
    "Hypertension",
    "Coronary Artery Disease",
    "Asthma",
    "COPD",
    "Chronic Pain",
    "Depression",
    "Anxiety",
    "Arthritis",
    "Hyperlipidemia"
]

COMMON_MEDICATIONS = [
    "Metformin", "Lisinopril", "Amlodipine", "Atorvastatin",
    "Aspirin", "Omeprazole", "Levothyroxine", "Losartan",
    "Metoprolol", "Simvastatin", "Warfarin", "Clopidogrel",
    "Prednisone", "Furosemide", "Ibuprofen", "Gabapentin"
]

COMMON_SYMPTOMS = [
    "headache", "fatigue", "dizziness", "nausea",
    "shortness of breath", "chest pain", "joint pain",
    "stomach pain", "back pain", "insomnia",
    "anxiety", "depression", "cough", "fever"
]

def generate_patient_profile(patient_num: int) -> dict:
    """Generate a single synthetic patient"""
    age = random.randint(40, 75)
    
    # Random conditions (1-3)
    num_conditions = random.randint(1, 3)
    conditions = random.sample(COMMON_CONDITIONS, num_conditions)
    
    # Medications based on conditions (2-5)
    num_meds = random.randint(2, 5)
    medications = random.sample(COMMON_MEDICATIONS, num_meds)
    
    # Symptoms (2-4)
    num_symptoms = random.randint(2, 4)
    symptoms = random.sample(COMMON_SYMPTOMS, num_symptoms)
    
    # Build summary for embedding
    summary = f"Age {age} with {', '.join(conditions)}. "
    summary += f"Taking {', '.join(medications)}. "
    summary += f"Experiencing {', '.join(symptoms)}."
    
    return {
        "patient_id": f"synthetic_{patient_num:03d}",
        "age": age,
        "conditions": conditions,
        "medications": medications,
        "symptoms": symptoms,
        "summary": summary
    }

def main():
    """Generate and store synthetic patients"""
    logger.info("=" * 60)
    logger.info("Generating Synthetic Patient Population")
    logger.info("=" * 60)
    
    try:
        memory = MemoryAgent()
        
        # Generate 50 synthetic patients
        num_patients = 50
        logger.info(f"\nGenerating {num_patients} synthetic patients...")
        
        for i in range(1, num_patients + 1):
            profile = generate_patient_profile(i)
            memory.store_synthetic_patient(profile)
            
            if i % 10 == 0:
                logger.info(f"  ✓ Generated {i}/{num_patients} patients")
        
        logger.info(f"\n✅ Successfully generated {num_patients} synthetic patients")
        logger.info("\n" + "=" * 60)
        logger.info("Synthetic population ready for similarity matching!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ Failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()