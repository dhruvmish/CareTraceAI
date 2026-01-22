"""
Configuration module for CareTrace AI
Loads environment variables and provides system-wide settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
AUDIO_DIR = DATA_DIR / "audio"
PRESCRIPTIONS_DIR = DATA_DIR / "prescriptions"
PATIENT_STORIES_DIR = DATA_DIR / "patient_stories"
SYNTHETIC_PATIENTS_DIR = DATA_DIR / "synthetic_patients"

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Embedding configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 dimension

# Audio processing
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Collection names
COLLECTION_PATIENT_EVENTS = "patient_events"
COLLECTION_DRUG_INTERACTIONS = "drug_interactions"
COLLECTION_SYNTHETIC_PATIENTS = "synthetic_patient_profiles"

# Safety thresholds
PATTERN_REPEAT_THRESHOLD = 2  # Number of times a symptom must repeat to flag
SIMILARITY_THRESHOLD = 0.7    # Minimum similarity for patient matching

# Create directories if they don't exist
for directory in [AUDIO_DIR, PRESCRIPTIONS_DIR, PATIENT_STORIES_DIR, SYNTHETIC_PATIENTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)