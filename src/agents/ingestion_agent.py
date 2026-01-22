"""
IngestionAgent: Converts raw inputs into structured events

Responsibilities:
- Transcribe audio files using Whisper
- Extract text from prescription images using OCR
- Structure data into semantic events
- Does NOT store data (delegates to MemoryAgent)
"""

import whisper
from PIL import Image
import pytesseract
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import re
from src.utils.logger import setup_logger
from src.config import WHISPER_MODEL

logger = setup_logger(__name__)

class IngestionAgent:
    """Agent responsible for converting raw inputs to structured data"""
    
    def __init__(self):
        """Initialize Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {WHISPER_MODEL}")
            self.whisper_model = whisper.load_model(WHISPER_MODEL)
            logger.info("✅ IngestionAgent initialized")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {str(e)}")
            raise
    
    def process_audio(self, audio_path: Path, patient_id: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            patient_id: Patient identifier
        
        Returns:
            Structured event dict
        
        Raises:
            FileNotFoundError: If audio file doesn't exist
            Exception: If transcription fails
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            logger.info(f"Transcribing audio: {audio_path.name}")
            result = self.whisper_model.transcribe(str(audio_path))
            text = result["text"].strip()
            language = result.get("language", "unknown")
            
            logger.info(f"✅ Transcribed ({language}): {text[:50]}...")
            
            return {
                "patient_id": patient_id,
                "event_type": "symptom",
                "text": text,
                "timestamp": datetime.utcnow().isoformat(),
                "drugs": [],
                "metadata": {
                    "source": "audio",
                    "filename": audio_path.name,
                    "language": language
                }
            }
        except Exception as e:
            logger.error(f"❌ Transcription failed: {str(e)}")
            raise
    
    def process_prescription(self, image_path: Path, patient_id: str) -> Dict[str, Any]:
        """
        Extract text from prescription image using OCR
        
        Args:
            image_path: Path to prescription image
            patient_id: Patient identifier
        
        Returns:
            Structured event dict with extracted drugs
        
        Raises:
            FileNotFoundError: If image doesn't exist
            Exception: If OCR fails
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            logger.info(f"Processing prescription: {image_path.name}")
            image = Image.open(image_path)
            raw_text = pytesseract.image_to_string(image)
            
            # Extract drug names (basic pattern matching)
            drugs = self._extract_drug_names(raw_text)
            
            logger.info(f"✅ Extracted drugs: {drugs}")
            
            return {
                "patient_id": patient_id,
                "event_type": "prescription",
                "text": raw_text.strip(),
                "timestamp": datetime.utcnow().isoformat(),
                "drugs": drugs,
                "metadata": {
                    "source": "prescription_image",
                    "filename": image_path.name
                }
            }
        except Exception as e:
            logger.error(f"❌ OCR failed: {str(e)}")
            raise
    
    def _extract_drug_names(self, text: str) -> List[str]:
        """
        Extract drug names from OCR text
        Uses simple pattern matching (in production, use NER)
        
        Args:
            text: Raw OCR text
        
        Returns:
            List of extracted drug names
        """
        # Common drug name patterns (simplified)
        # In production, use a medical NER model or drug database
        known_drugs = [
            "aspirin", "ibuprofen", "paracetamol", "acetaminophen",
            "metformin", "lisinopril", "amlodipine", "atorvastatin",
            "warfarin", "clopidogrel", "omeprazole", "levothyroxine",
            "simvastatin", "losartan", "metoprolol", "furosemide",
            "prednisone", "amoxicillin", "azithromycin", "ciprofloxacin"
        ]
        
        drugs = []
        text_lower = text.lower()
        
        for drug in known_drugs:
            if drug in text_lower:
                drugs.append(drug.capitalize())
        
        # Also look for capitalized words that might be drug names
        # Pattern: Capitalized word followed by dosage (e.g., "Aspirin 100mg")
        pattern = r'\b([A-Z][a-z]+(?:in|ol|ide|one|cin)?)\s*\d+\s*(?:mg|ML|tablet)'
        matches = re.findall(pattern, text)
        
        for match in matches:
            if match.capitalize() not in drugs:
                drugs.append(match.capitalize())
        
        return list(set(drugs))  # Remove duplicates
    
    def create_manual_event(
        self, 
        patient_id: str, 
        event_type: str, 
        text: str, 
        drugs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a structured event from manual input (for UI)
        
        Args:
            patient_id: Patient identifier
            event_type: "symptom" or "prescription"
            text: Event description
            drugs: List of drug names (for prescriptions)
        
        Returns:
            Structured event dict
        """
        return {
            "patient_id": patient_id,
            "event_type": event_type,
            "text": text,
            "timestamp": datetime.utcnow().isoformat(),
            "drugs": drugs or [],
            "metadata": {
                "source": "manual_entry"
            }
        }