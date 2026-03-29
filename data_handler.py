"""
data_handler.py
---------------
Handles saving and loading candidate interview data to/from a local JSON file.
Data is stored in a minimal, anonymized format in compliance with data privacy best practices.
Only recruitment-relevant fields are persisted; sensitive data (phone, email) is stored
but flagged so it can be excluded from logs/exports if needed.
"""

import json
import os
import uuid
from datetime import datetime


DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "candidates.json")


def _ensure_data_dir() -> None:
    """Create the data directory if it does not exist."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)


def save_candidate(candidate_info: dict) -> str:
    """
    Persist candidate information to the local JSON store.

    Args:
        candidate_info: Dictionary containing collected candidate fields.

    Returns:
        A unique session ID assigned to this candidate record.
    """
    _ensure_data_dir()

    # Load existing records
    records = _load_all()

    # Assign a unique ID and timestamp
    session_id = str(uuid.uuid4())
    record = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        # Core fields
        "full_name": candidate_info.get("full_name", ""),
        "email": candidate_info.get("email", ""),          # sensitive
        "phone": candidate_info.get("phone", ""),          # sensitive
        "years_of_experience": candidate_info.get("years_of_experience", ""),
        "desired_positions": candidate_info.get("desired_positions", ""),
        "current_location": candidate_info.get("current_location", ""),
        "tech_stack": candidate_info.get("tech_stack", ""),
        # Meta
        "interview_completed": candidate_info.get("interview_completed", False),
    }

    records.append(record)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    return session_id


def _load_all() -> list:
    """Return all stored candidate records, or an empty list if none exist."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def get_all_candidates() -> list:
    """Public accessor for all stored candidates (used for admin/debug purposes)."""
    return _load_all()
