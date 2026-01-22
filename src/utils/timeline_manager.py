"""
Timeline Manager Utility
Helper functions for managing patient timeline events
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_event_edit(original_event: Dict[str, Any], updated_event: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate an event edit before saving

    Args:
        original_event: Original event data
        updated_event: Updated event data

    Returns:
        (is_valid, error_message)
    """
    # Required fields
    required_fields = ["patient_id", "event_type", "text", "timestamp"]

    for field in required_fields:
        if field not in updated_event:
            return False, f"Missing required field: {field}"

    # Patient ID shouldn't change
    if original_event.get("patient_id") != updated_event.get("patient_id"):
        return False, "Cannot change patient_id during edit"

    # Event type shouldn't change
    if original_event.get("event_type") != updated_event.get("event_type"):
        return False, "Cannot change event_type during edit"

    # Text shouldn't be empty
    if not updated_event.get("text", "").strip():
        return False, "Text cannot be empty"

    # Validate drugs for prescriptions
    if updated_event.get("event_type") == "prescription":
        drugs = updated_event.get("drugs", [])
        if not drugs:
            logger.warning("Prescription has no drugs listed")

    return True, ""


def create_audit_log(action: str, event_id: str, patient_id: str, user: str = "system") -> Dict[str, Any]:
    """
    Create an audit log entry for timeline modifications

    Args:
        action: "delete" | "edit" | "create"
        event_id: Point ID of the event
        patient_id: Patient identifier
        user: User who performed the action

    Returns:
        Audit log entry
    """
    return {
        "action": action,
        "event_id": event_id,
        "patient_id": patient_id,
        "user": user,
        "timestamp": datetime.utcnow().isoformat(),
    }


def format_event_for_display(event: Dict[str, Any]) -> str:
    """
    Format event as readable string

    Args:
        event: Event data

    Returns:
        Formatted string
    """
    event_type = event.get("event_type", "unknown").capitalize()
    timestamp = event.get("timestamp", "")
    text = event.get("text", "")

    try:
        dt = datetime.fromisoformat(timestamp)
        date_str = dt.strftime("%Y-%m-%d %H:%M")
    except:
        date_str = timestamp

    if event_type == "Prescription":
        drugs = event.get("drugs", [])
        drugs_str = ", ".join(drugs) if drugs else "None"
        return f"[{date_str}] {event_type}: {drugs_str}"
    else:
        preview = text[:50] + "..." if len(text) > 50 else text
        return f"[{date_str}] {event_type}: {preview}"


def bulk_delete_events(memory_agent, point_ids: List[str]) -> Dict[str, Any]:
    """
    Delete multiple events at once

    Args:
        memory_agent: MemoryAgent instance
        point_ids: List of point IDs to delete

    Returns:
        Result summary
    """
    results = {
        "success": [],
        "failed": [],
        "total": len(point_ids)
    }

    for point_id in point_ids:
        if memory_agent.delete_event(point_id):
            results["success"].append(point_id)
            logger.info(f"Deleted event: {point_id}")
        else:
            results["failed"].append(point_id)
            logger.error(f"Failed to delete event: {point_id}")

    return results


def export_timeline_to_dict(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Export timeline to a structured dictionary for backup/export

    Args:
        events: List of patient events

    Returns:
        Exportable dictionary
    """
    if not events:
        return {"events": [], "count": 0}

    patient_id = events[0].get("patient_id", "unknown")

    export_data = {
        "patient_id": patient_id,
        "export_timestamp": datetime.utcnow().isoformat(),
        "event_count": len(events),
        "events": []
    }

    for event in events:
        # Remove point_id for export (internal identifier)
        export_event = {k: v for k, v in event.items() if k != "point_id"}
        export_data["events"].append(export_event)

    return export_data


def filter_timeline_by_date_range(
        events: List[Dict[str, Any]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter events by date range

    Args:
        events: List of events
        start_date: ISO format date string (inclusive)
        end_date: ISO format date string (inclusive)

    Returns:
        Filtered events
    """
    if not start_date and not end_date:
        return events

    filtered = []

    for event in events:
        try:
            event_date = datetime.fromisoformat(event.get("timestamp", ""))

            if start_date:
                start_dt = datetime.fromisoformat(start_date)
                if event_date < start_dt:
                    continue

            if end_date:
                end_dt = datetime.fromisoformat(end_date)
                if event_date > end_dt:
                    continue

            filtered.append(event)

        except (ValueError, TypeError):
            # Skip events with invalid timestamps
            continue

    return filtered


def get_timeline_statistics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for a patient timeline

    Args:
        events: List of patient events

    Returns:
        Statistics dictionary
    """
    stats = {
        "total_events": len(events),
        "symptoms": 0,
        "prescriptions": 0,
        "unique_drugs": set(),
        "date_range": None,
        "avg_events_per_month": 0
    }

    if not events:
        return stats

    timestamps = []

    for event in events:
        event_type = event.get("event_type")

        if event_type == "symptom":
            stats["symptoms"] += 1
        elif event_type == "prescription":
            stats["prescriptions"] += 1
            stats["unique_drugs"].update(event.get("drugs", []))

        try:
            ts = datetime.fromisoformat(event.get("timestamp", ""))
            timestamps.append(ts)
        except:
            pass

    # Convert set to list
    stats["unique_drugs"] = list(stats["unique_drugs"])

    # Calculate date range
    if timestamps:
        earliest = min(timestamps)
        latest = max(timestamps)
        span_days = (latest - earliest).days

        stats["date_range"] = {
            "earliest": earliest.isoformat(),
            "latest": latest.isoformat(),
            "span_days": span_days
        }

        # Calculate average events per month
        if span_days > 0:
            months = span_days / 30.0
            stats["avg_events_per_month"] = round(len(events) / max(months, 0.1), 2)

    return stats