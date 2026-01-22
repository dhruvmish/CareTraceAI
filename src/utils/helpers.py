"""
Utility helper functions
General-purpose functions used across the system
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import re

def format_timestamp(iso_timestamp: str, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    Format ISO timestamp to readable string
    
    Args:
        iso_timestamp: ISO 8601 timestamp string
        format_str: strftime format string
    
    Returns:
        Formatted timestamp string
    """
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime(format_str)
    except (ValueError, AttributeError):
        return iso_timestamp

def get_relative_time(iso_timestamp: str) -> str:
    """
    Get human-readable relative time (e.g., "2 days ago")
    
    Args:
        iso_timestamp: ISO 8601 timestamp string
    
    Returns:
        Relative time string
    """
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.days == 1:
            return "yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        else:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
    except (ValueError, AttributeError):
        return "unknown time"

def clean_drug_name(drug_name: str) -> str:
    """
    Normalize drug name for comparison
    
    Args:
        drug_name: Raw drug name
    
    Returns:
        Cleaned drug name (lowercase, no extra spaces)
    """
    return drug_name.strip().lower()

def extract_keywords_from_text(text: str, min_length: int = 4) -> List[str]:
    """
    Extract meaningful keywords from text
    
    Args:
        text: Input text
        min_length: Minimum keyword length
    
    Returns:
        List of keywords
    """
    # Remove punctuation and convert to lowercase
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him',
        'them', 'us', 'am', 'been', 'being', 'have', 'has'
    }
    
    # Split and filter
    words = text.split()
    keywords = [
        word for word in words
        if len(word) >= min_length and word not in stop_words
    ]
    
    return keywords

def severity_to_color(severity: str) -> str:
    """
    Map severity level to color emoji/indicator
    
    Args:
        severity: "mild" | "moderate" | "severe"
    
    Returns:
        Color emoji
    """
    severity_map = {
        "mild": "🟡",
        "moderate": "🟠",
        "severe": "🔴"
    }
    return severity_map.get(severity.lower(), "⚪")

def create_summary_stats(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics from event list
    
    Args:
        events: List of patient events
    
    Returns:
        Statistics dict
    """
    stats = {
        "total_events": len(events),
        "symptom_count": 0,
        "prescription_count": 0,
        "unique_drugs": set(),
        "date_range": None
    }
    
    if not events:
        return stats
    
    timestamps = []
    
    for event in events:
        if event.get("event_type") == "symptom":
            stats["symptom_count"] += 1
        elif event.get("event_type") == "prescription":
            stats["prescription_count"] += 1
            stats["unique_drugs"].update(event.get("drugs", []))
        
        if event.get("timestamp"):
            try:
                timestamps.append(datetime.fromisoformat(event["timestamp"]))
            except:
                pass
    
    # Convert set to list for JSON serialization
    stats["unique_drugs"] = list(stats["unique_drugs"])
    
    # Calculate date range
    if timestamps:
        stats["date_range"] = {
            "earliest": min(timestamps).isoformat(),
            "latest": max(timestamps).isoformat(),
            "span_days": (max(timestamps) - min(timestamps)).days
        }
    
    return stats

def validate_patient_id(patient_id: str) -> bool:
    """
    Validate patient ID format
    
    Args:
        patient_id: Patient identifier
    
    Returns:
        True if valid format
    """
    # Simple validation: alphanumeric + underscore, 3-50 chars
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return bool(re.match(pattern, patient_id))

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to max length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix