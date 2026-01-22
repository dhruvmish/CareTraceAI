"""
PopulationAgent: Finds similar patients for evidence-based insights

Responsibilities:
- Search synthetic patient population
- Find patients with similar conditions/medications/symptoms
- Provide population-level evidence for safety decisions
- Uses MemoryAgent for all similarity search
"""

from typing import List, Dict, Any
from src.config import SIMILARITY_THRESHOLD
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PopulationAgent:
    """Agent responsible for population-level analysis"""
    
    def __init__(self, memory_agent):
        """
        Initialize with reference to MemoryAgent
        
        Args:
            memory_agent: Instance of MemoryAgent for data access
        """
        self.memory = memory_agent
        logger.info("✅ PopulationAgent initialized")
    
    def find_similar_patients(
        self, 
        patient_id: str, 
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        Find patients with similar medical profiles
        
        Args:
            patient_id: Target patient identifier
            limit: Number of similar patients to return
        
        Returns:
            Dict with similar patients and similarity scores
        """
        logger.info(f"Finding similar patients for {patient_id}")
        
        # Build query from patient's current state
        query_summary = self._build_patient_summary(patient_id)
        
        if not query_summary:
            return {
                "found_similar": False,
                "message": "Insufficient patient data to find similar cases"
            }
        
        # Search synthetic population
        similar = self.memory.search_similar_patients(
            query_text=query_summary,
            limit=limit + 1  # +1 because patient might match themselves
        )
        
        # Filter out the patient themselves (if in synthetic data)
        similar = [
            p for p in similar 
            if p.get("patient_id") != patient_id
        ][:limit]
        
        if not similar:
            return {
                "found_similar": False,
                "message": "No similar patients found in population"
            }
        
        # Filter by similarity threshold
        relevant = [
            p for p in similar 
            if p.get("similarity_score", 0) >= SIMILARITY_THRESHOLD
        ]
        
        if not relevant:
            return {
                "found_similar": False,
                "similar_patients": similar,
                "message": f"Found {len(similar)} patients but none above similarity threshold ({SIMILARITY_THRESHOLD})"
            }
        
        return {
            "found_similar": True,
            "similar_patients": relevant,
            "message": f"✅ Found {len(relevant)} similar patient(s) with high similarity scores"
        }
    
    def get_population_insights(
        self, 
        patient_id: str, 
        focus: str
    ) -> Dict[str, Any]:
        """
        Get specific population insights based on focus area
        
        Args:
            patient_id: Target patient
            focus: "medications" | "symptoms" | "conditions"
        
        Returns:
            Population-level insights
        """
        logger.info(f"Getting population insights (focus: {focus}) for {patient_id}")
        
        similar_result = self.find_similar_patients(patient_id, limit=5)
        
        if not similar_result.get("found_similar"):
            return similar_result
        
        similar_patients = similar_result["similar_patients"]
        
        if focus == "medications":
            return self._analyze_medication_patterns(similar_patients)
        elif focus == "symptoms":
            return self._analyze_symptom_patterns(similar_patients)
        elif focus == "conditions":
            return self._analyze_condition_patterns(similar_patients)
        else:
            return {
                "error": f"Unknown focus area: {focus}"
            }
    
    def _build_patient_summary(self, patient_id: str) -> str:
        """
        Build a text summary of patient's medical profile
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Summary string for embedding
        """
        # Get patient history
        symptoms = self.memory.get_patient_history(
            patient_id=patient_id,
            event_type="symptom",
            limit=10
        )
        
        prescriptions = self.memory.get_patient_history(
            patient_id=patient_id,
            event_type="prescription",
            limit=5
        )
        
        if not symptoms and not prescriptions:
            return ""
        
        # Extract medications
        medications = set()
        for rx in prescriptions:
            medications.update(rx.get("drugs", []))
        
        # Extract symptom keywords
        symptom_texts = [s["text"] for s in symptoms]
        
        # Build summary
        summary_parts = []
        
        if medications:
            summary_parts.append(f"Medications: {', '.join(medications)}")
        
        if symptom_texts:
            # Combine recent symptoms
            recent_symptoms = " ".join(symptom_texts[:3])
            summary_parts.append(f"Recent symptoms: {recent_symptoms}")
        
        return ". ".join(summary_parts)
    
    def _analyze_medication_patterns(
        self, 
        similar_patients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze medication patterns across similar patients"""
        all_meds = []
        for patient in similar_patients:
            all_meds.extend(patient.get("medications", []))
        
        from collections import Counter
        med_counts = Counter(all_meds)
        
        common_meds = med_counts.most_common(5)
        
        return {
            "insight_type": "medications",
            "common_medications": [
                {"drug": med, "frequency": count}
                for med, count in common_meds
            ],
            "message": f"Among {len(similar_patients)} similar patients, most common medications are: {', '.join([m[0] for m in common_meds[:3]])}"
        }
    
    def _analyze_symptom_patterns(
        self, 
        similar_patients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze symptom patterns across similar patients"""
        all_symptoms = []
        for patient in similar_patients:
            all_symptoms.extend(patient.get("symptoms", []))
        
        from collections import Counter
        symptom_counts = Counter(all_symptoms)
        
        common_symptoms = symptom_counts.most_common(5)
        
        return {
            "insight_type": "symptoms",
            "common_symptoms": [
                {"symptom": sym, "frequency": count}
                for sym, count in common_symptoms
            ],
            "message": f"Among {len(similar_patients)} similar patients, most common symptoms are: {', '.join([s[0] for s in common_symptoms[:3]])}"
        }
    
    def _analyze_condition_patterns(
        self, 
        similar_patients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze medical conditions across similar patients"""
        all_conditions = []
        for patient in similar_patients:
            all_conditions.extend(patient.get("conditions", []))
        
        from collections import Counter
        condition_counts = Counter(all_conditions)
        
        common_conditions = condition_counts.most_common(5)
        
        return {
            "insight_type": "conditions",
            "common_conditions": [
                {"condition": cond, "frequency": count}
                for cond, count in common_conditions
            ],
            "message": f"Among {len(similar_patients)} similar patients, most common conditions are: {', '.join([c[0] for c in common_conditions[:3]])}"
        }