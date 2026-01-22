"""
Ingest curated drug-drug interaction knowledge base
"""

from src.agents.memory_agent import MemoryAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

DRUG_INTERACTIONS = [

    # 🔴 SEVERE — Bleeding risk
    {
        "drug_a": "Warfarin",
        "drug_b": "Ibuprofen",
        "severity": "severe",
        "explanation": "NSAIDs like ibuprofen significantly increase bleeding risk when combined with warfarin."
    },
    {
        "drug_a": "Warfarin",
        "drug_b": "Aspirin",
        "severity": "severe",
        "explanation": "Combined anticoagulant and antiplatelet therapy increases risk of major bleeding."
    },
    {
        "drug_a": "Warfarin",
        "drug_b": "Clopidogrel",
        "severity": "severe",
        "explanation": "Dual anticoagulant and antiplatelet therapy greatly increases bleeding complications."
    },

    # 🟠 MODERATE
    {
        "drug_a": "Aspirin",
        "drug_b": "Ibuprofen",
        "severity": "moderate",
        "explanation": "Ibuprofen can interfere with aspirin’s antiplatelet effect and increase GI bleeding risk."
    },
    {
        "drug_a": "Atorvastatin",
        "drug_b": "Clarithromycin",
        "severity": "moderate",
        "explanation": "Clarithromycin increases statin levels, raising risk of muscle toxicity."
    },

    # 🟡 MILD
    {
        "drug_a": "Levothyroxine",
        "drug_b": "Calcium Carbonate",
        "severity": "mild",
        "explanation": "Calcium reduces absorption of levothyroxine when taken together."
    }
]

def main():
    logger.info("============================================================")
    logger.info("Ingesting Drug Interaction Knowledge Base")
    logger.info("============================================================")

    memory = MemoryAgent()

    for interaction in DRUG_INTERACTIONS:
        memory.store_drug_interaction(interaction)

    logger.info(f"✅ Successfully ingested {len(DRUG_INTERACTIONS)} drug interactions")

if __name__ == "__main__":
    main()
