# src/__init__.py
"""CareTrace AI - Multi-Agent Healthcare Safety System"""

__version__ = "1.0.0"
__author__ = "CareTrace AI Team"

# src/agents/__init__.py
"""Agent implementations for CareTrace AI"""

from .agents.ingestion_agent import IngestionAgent
from .agents.memory_agent import MemoryAgent
from .agents.safety_agent import SafetyAgent
from .agents.pattern_agent import PatternAgent
from .agents.population_agent import PopulationAgent

__all__ = [
    "IngestionAgent",
    "MemoryAgent",
    "SafetyAgent",
    "PatternAgent",
    "PopulationAgent"
]

# src/db/__init__.py
"""Database layer for CareTrace AI"""

from .db.qdrant_client import QdrantConnection
from .db.collections import create_collections

__all__ = [
    "QdrantConnection",
    "create_collections"
]

# src/utils/__init__.py
"""Utility functions for CareTrace AI"""

from .utils.logger import setup_logger
from .utils.helpers import (
    format_timestamp,
    get_relative_time,
    clean_drug_name,
    extract_keywords_from_text,
    severity_to_color,
    create_summary_stats,
    validate_patient_id,
    truncate_text
)
from .utils.timeline_manager import (
    validate_event_edit,
    create_audit_log,
    format_event_for_display,
    bulk_delete_events,
    export_timeline_to_dict,
    filter_timeline_by_date_range,
    get_timeline_statistics
)

__all__ = [
    "setup_logger",
    "format_timestamp",
    "get_relative_time",
    "clean_drug_name",
    "extract_keywords_from_text",
    "severity_to_color",
    "create_summary_stats",
    "validate_patient_id",
    "truncate_text",
    "validate_event_edit",
    "create_audit_log",
    "format_event_for_display",
    "bulk_delete_events",
    "export_timeline_to_dict",
    "filter_timeline_by_date_range",
    "get_timeline_statistics"
]