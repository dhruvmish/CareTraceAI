"""
PatternAgent: Detects symptom patterns over time

Responsibilities:
- Find repeated symptoms in patient history
- Correlate symptom timing with medication changes
- Flag unusual patterns that may indicate adverse reactions
- Uses MemoryAgent for all data access
"""

from typing import List, Dict, Any
from collections import Counter
from datetime import datetime, timedelta
from src.config import PATTERN_REPEAT_THRESHOLD
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PatternAgent:
    """Agent responsible for temporal pattern detection"""
    
    def __init__(self, memory_agent):
        """
        Initialize with reference to MemoryAgent
        
        Args:
            memory_agent: Instance of MemoryAgent for data access
        """
        self.memory = memory_agent
        logger.info("✅ PatternAgent initialized")
    
    def detect_recurring_symptoms(self, patient_id: str) -> Dict[str, Any]:
        """
        Find symptoms that repeat over time
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Dict with recurring patterns and analysis
        """
        logger.info(f"Analyzing symptom patterns for patient {patient_id}")
        
        # Get all symptom reports
        symptoms = self.memory.get_patient_history(
            patient_id=patient_id,
            event_type="symptom"
        )
        
        if len(symptoms) < 2:
            return {
                "has_patterns": False,
                "message": "Insufficient data to detect patterns (need at least 2 symptom reports)"
            }
        
        # Extract keywords from symptom descriptions
        keyword_occurrences = []
        for symptom in symptoms:
            keywords = self._extract_keywords(symptom["text"])
            timestamp = symptom.get("timestamp", "")
            keyword_occurrences.append({
                "keywords": keywords,
                "timestamp": timestamp,
                "full_text": symptom["text"]
            })
        
        # Count keyword frequencies
        all_keywords = []
        for item in keyword_occurrences:
            all_keywords.extend(item["keywords"])
        
        keyword_counts = Counter(all_keywords)
        
        # Find keywords that appear multiple times
        recurring = {
            kw: count 
            for kw, count in keyword_counts.items() 
            if count >= PATTERN_REPEAT_THRESHOLD
        }
        
        if not recurring:
            return {
                "has_patterns": False,
                "message": "No recurring symptom patterns detected"
            }
        
        # Build detailed pattern report
        patterns = []
        for keyword, count in recurring.items():
            occurrences = [
                item for item in keyword_occurrences 
                if keyword in item["keywords"]
            ]
            patterns.append({
                "symptom_keyword": keyword,
                "occurrence_count": count,
                "dates": [occ["timestamp"] for occ in occurrences],
                "reports": [occ["full_text"] for occ in occurrences]
            })
        
        return {
            "has_patterns": True,
            "recurring_symptoms": patterns,
            "message": f"⚠️ Detected {len(patterns)} recurring symptom pattern(s)"
        }
    
    def correlate_with_medications(
        self, 
        patient_id: str, 
        symptom_keyword: str
    ) -> Dict[str, Any]:
        """
        Check if a symptom coincides with medication timing
        
        Args:
            patient_id: Patient identifier
            symptom_keyword: Specific symptom to analyze
        
        Returns:
            Dict with temporal correlation analysis
        """
        logger.info(f"Correlating '{symptom_keyword}' with medications")
        
        symptoms = self.memory.get_patient_history(
            patient_id=patient_id,
            event_type="symptom"
        )
        
        prescriptions = self.memory.get_patient_history(
            patient_id=patient_id,
            event_type="prescription"
        )
        
        if not prescriptions:
            return {
                "correlation_found": False,
                "message": "No prescription records to correlate"
            }
        
        # Find symptoms matching the keyword
        matching_symptoms = [
            s for s in symptoms 
            if symptom_keyword.lower() in s["text"].lower()
        ]
        
        if not matching_symptoms:
            return {
                "correlation_found": False,
                "message": f"No reports found containing '{symptom_keyword}'"
            }
        
        # Check temporal proximity (within 7 days of prescription)
        correlations = []
        for symptom in matching_symptoms:
            symptom_time = datetime.fromisoformat(symptom["timestamp"])
            
            for rx in prescriptions:
                rx_time = datetime.fromisoformat(rx["timestamp"])
                time_diff = abs((symptom_time - rx_time).days)
                
                if time_diff <= 7:
                    correlations.append({
                        "symptom_text": symptom["text"],
                        "symptom_date": symptom["timestamp"],
                        "prescription_drugs": rx.get("drugs", []),
                        "prescription_date": rx["timestamp"],
                        "days_apart": time_diff
                    })
        
        if not correlations:
            return {
                "correlation_found": False,
                "message": f"No temporal correlation found between '{symptom_keyword}' and prescriptions"
            }
        
        return {
            "correlation_found": True,
            "correlations": correlations,
            "message": f"⚠️ Found {len(correlations)} temporal correlation(s) between symptom and medication timing"
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from symptom text
        Simple approach: filter common words
        
        Args:
            text: Symptom description
        
        Returns:
            List of keywords
        """
        # Stop words to ignore
        stop_words = {
            "i", "am", "have", "been", "having", "feel", "feeling", 
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "my", "me", "is", "was", "are"
        }
        
        # Simple tokenization
        words = text.lower().split()
        
        # Filter and clean
        keywords = [
            word.strip(".,!?;:")
            for word in words
            if len(word) > 3 and word not in stop_words
        ]
        
        return keywords