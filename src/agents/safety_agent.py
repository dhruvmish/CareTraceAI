"""
SafetyAgent: Detects drug-drug interactions

Responsibilities:
- Check new medications against patient's current drugs
- Query drug_interactions collection via MemoryAgent
- Generate safety alerts with severity and evidence
- Does NOT make medical decisions (only flags potential issues)
"""

from typing import List, Dict, Any, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class SafetyAgent:
    """Agent responsible for drug interaction checking"""
    
    def __init__(self, memory_agent):
        """
        Initialize with reference to MemoryAgent
        
        Args:
            memory_agent: Instance of MemoryAgent for data access
        """
        self.memory = memory_agent
        logger.info("✅ SafetyAgent initialized")
    
    def check_new_medication(
        self, 
        patient_id: str, 
        new_drug: str
    ) -> Dict[str, Any]:
        """
        Check if a new medication has interactions with patient's current drugs
        
        Args:
            patient_id: Patient identifier
            new_drug: Name of medication being considered
        
        Returns:
            Dict with interactions found, severity, and recommendations
        """
        logger.info(f"Checking safety for {new_drug} (patient: {patient_id})")
        
        # Step 1: Get patient's current medications
        current_drugs = self._get_patient_medications(patient_id)
        
        if not current_drugs:
            logger.info("No current medications found - no interactions")
            return {
                "safe": True,
                "new_drug": new_drug,
                "current_drugs": [],
                "interactions": [],
                "message": "No current medications on record."
            }
        
        # Step 2: Check interactions
        interactions = self._find_interactions(new_drug, current_drugs)
        
        # Step 3: Generate report
        if not interactions:
            return {
                "safe": True,
                "new_drug": new_drug,
                "current_drugs": current_drugs,
                "interactions": [],
                "message": f"No known interactions found between {new_drug} and current medications."
            }
        else:
            max_severity = self._get_max_severity(interactions)
            return {
                "safe": False,
                "new_drug": new_drug,
                "current_drugs": current_drugs,
                "interactions": interactions,
                "max_severity": max_severity,
                "message": f"⚠️ Found {len(interactions)} potential interaction(s). Maximum severity: {max_severity.upper()}"
            }
    
    def _get_patient_medications(self, patient_id: str) -> List[str]:
        """
        Extract unique drug names from patient's prescription history
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            List of drug names
        """
        prescriptions = self.memory.get_patient_history(
            patient_id=patient_id,
            event_type="prescription"
        )
        
        drugs = set()
        for rx in prescriptions:
            drugs.update(rx.get("drugs", []))
        
        return sorted(list(drugs))
    
    def _find_interactions(
        self, 
        new_drug: str, 
        current_drugs: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Check if new drug interacts with any current drugs
        
        Args:
            new_drug: Medication being added
            current_drugs: Patient's current medications
        
        Returns:
            List of interaction records
        """
        all_interactions = self.memory.get_all_drug_interactions()
        
        found = []
        new_drug_lower = new_drug.lower()
        current_drugs_lower = [d.lower() for d in current_drugs]
        
        for interaction in all_interactions:
            drug_a = interaction["drug_a"].lower()
            drug_b = interaction["drug_b"].lower()
            
            # Check if interaction involves new_drug and any current drug
            if (drug_a == new_drug_lower and drug_b in current_drugs_lower) or \
               (drug_b == new_drug_lower and drug_a in current_drugs_lower):
                found.append(interaction)
        
        logger.info(f"Found {len(found)} interactions for {new_drug}")
        return found
    
    def _get_max_severity(self, interactions: List[Dict[str, Any]]) -> str:
        """
        Determine highest severity level from interactions
        
        Args:
            interactions: List of interaction records
        
        Returns:
            "severe" | "moderate" | "mild"
        """
        severity_order = {"severe": 3, "moderate": 2, "mild": 1}
        
        max_level = "mild"
        max_value = 1
        
        for interaction in interactions:
            severity = interaction.get("severity", "mild").lower()
            value = severity_order.get(severity, 1)
            if value > max_value:
                max_value = value
                max_level = severity
        
        return max_level
    
    def get_interaction_details(
        self, 
        drug_a: str, 
        drug_b: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific drug pair
        
        Args:
            drug_a: First drug name
            drug_b: Second drug name
        
        Returns:
            Interaction record or None
        """
        all_interactions = self.memory.get_all_drug_interactions()
        
        drug_a_lower = drug_a.lower()
        drug_b_lower = drug_b.lower()
        
        for interaction in all_interactions:
            ia = interaction["drug_a"].lower()
            ib = interaction["drug_b"].lower()
            
            if (ia == drug_a_lower and ib == drug_b_lower) or \
               (ia == drug_b_lower and ib == drug_a_lower):
                return interaction
        
        return None