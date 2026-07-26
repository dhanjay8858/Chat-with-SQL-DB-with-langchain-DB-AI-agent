"""
Query History Persistence & Logging Module.

Tracks, stores, searches, re-runs, and manages query execution history
backed by a persistent JSON storage file.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from utils.logger import setup_logger

logger = setup_logger(__name__)

HISTORY_FILE = Path(__file__).parent.parent / "query_history.json"


def load_history() -> list[dict[str, Any]]:
    """Load query execution history from JSON file storage.

    Returns:
        List of history item dictionaries.
    """
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to load query history: %s", e)
        return []


def save_history(history: list[dict[str, Any]]) -> None:
    """Save query execution history list to JSON file storage.

    Args:
        history: List of history item dictionaries.
    """
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Failed to save query history: %s", e)


def add_query_log(
    question: str,
    sql: str,
    execution_time_ms: float = 0.0,
    rows_affected: int = 0,
    status: str = "SUCCESS",
) -> dict[str, Any]:
    """Record a new query execution event in history.

    Args:
        question: User's natural language question.
        sql: Executed SQL query statement.
        execution_time_ms: Runtime duration in milliseconds.
        rows_affected: Number of rows returned or modified.
        status: Execution status ('SUCCESS' or 'FAILED').

    Returns:
        The created history entry dictionary.
    """
    history = load_history()

    item = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "sql": sql.strip(),
        "execution_time_ms": round(execution_time_ms, 2),
        "rows_affected": rows_affected,
        "status": status,
    }

    # Prepend newest query first
    history.insert(0, item)
    save_history(history)
    logger.info("Logged query history entry: %s", item["id"])

    return item


def delete_query_log(item_id: str) -> None:
    """Delete a specific query entry from history by ID.

    Args:
        item_id: Unique string ID of the item to remove.
    """
    history = load_history()
    filtered = [h for h in history if h.get("id") != item_id]
    save_history(filtered)
    logger.info("Deleted query history entry: %s", item_id)


def clear_all_history() -> None:
    """Clear all entries from query history."""
    save_history([])
    logger.info("Cleared all query history entries.")


def search_history(search_term: str) -> list[dict[str, Any]]:
    """Search query history by question, SQL text, or status.

    Args:
        search_term: Substring query string.

    Returns:
        Filtered list of matching history entries.
    """
    history = load_history()
    if not search_term:
        return history

    term = search_term.strip().lower()
    results = []

    for item in history:
        if (
            term in item.get("question", "").lower()
            or term in item.get("sql", "").lower()
            or term in item.get("status", "").lower()
            or term in item.get("timestamp", "").lower()
        ):
            results.append(item)

    return results
