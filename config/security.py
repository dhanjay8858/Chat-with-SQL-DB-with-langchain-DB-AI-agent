"""
Security Configuration & Policy Enforcement Engine.

Manages application security modes (Read-Only vs Admin), validates incoming SQL queries
against enterprise security policies, and blocks destructive operations (DROP DATABASE,
DROP TABLE, TRUNCATE, and mass DELETE/UPDATE without WHERE clauses).
"""

import re
import streamlit as st
from typing import Any

from services.sql_executor import classify_sql, is_write_operation
from utils.logger import setup_logger

logger = setup_logger(__name__)

MODE_READ_ONLY = "🔒 Read Only (Analyst)"
MODE_ADMIN = "👤 Admin (Full Access)"


def init_security_state() -> None:
    """Initialize security mode in Streamlit session state if not already set."""
    if "security_mode" not in st.session_state:
        st.session_state["security_mode"] = MODE_ADMIN


def get_current_security_mode() -> str:
    """Get the active security mode.

    Returns:
        String mode (MODE_READ_ONLY or MODE_ADMIN).
    """
    init_security_state()
    return st.session_state.get("security_mode", MODE_ADMIN)


def is_read_only() -> bool:
    """Check if Read-Only mode is currently active.

    Returns:
        True if Read-Only mode is active, False otherwise.
    """
    return get_current_security_mode() == MODE_READ_ONLY


def validate_query_security(sql: str) -> tuple[bool, str]:
    """Validate a SQL statement against active security policies.

    Args:
        sql: The target SQL statement.

    Returns:
        Tuple of (is_allowed, policy_message).
    """
    cleaned = sql.strip()
    upper_sql = cleaned.upper()
    op_type = classify_sql(cleaned)
    mode = get_current_security_mode()

    # 1. Read-Only Policy Check
    if mode == MODE_READ_ONLY and is_write_operation(cleaned):
        logger.warning("Security Blocked (Read-Only Mode): %s", cleaned)
        return (
            False,
            "🔒 **Read-Only Mode Active**: Database modification queries "
            f"(`{op_type}`) are prohibited in Read-Only Mode. "
            "Switch to Admin Mode in the sidebar to perform data modifications.",
        )

    # 2. Strict Destructive DDL Prevention (Forbidden in both modes)
    forbidden_ddl = ["DROP DATABASE", "DROP SCHEMA", "DROP TABLE", "TRUNCATE"]
    for kw in forbidden_ddl:
        if kw in upper_sql:
            logger.warning("Security Blocked (Destructive DDL): %s", cleaned)
            return (
                False,
                f"🚫 **Security Policy Violation**: Operations containing `{kw}` are strictly "
                "forbidden to protect system data integrity.",
            )

    # 3. Mass Action Prevention (DELETE/UPDATE without WHERE clause)
    if op_type == "DELETE" or "DELETE FROM" in upper_sql:
        if not re.search(r"\bWHERE\b", upper_sql):
            logger.warning("Security Blocked (Mass DELETE without WHERE): %s", cleaned)
            return (
                False,
                "⚠️ **Mass DELETE Blocked**: Execution of `DELETE` without a `WHERE` clause "
                "is prohibited because it would wipe all rows in the table. "
                "Please specify a target condition.",
            )

    if op_type == "UPDATE" or re.search(r"\bUPDATE\b", upper_sql):
        if not re.search(r"\bWHERE\b", upper_sql):
            logger.warning("Security Blocked (Mass UPDATE without WHERE): %s", cleaned)
            return (
                False,
                "⚠️ **Mass UPDATE Blocked**: Execution of `UPDATE` without a `WHERE` clause "
                "is prohibited because it would overwrite all rows in the table. "
                "Please specify a target condition.",
            )

    return True, "Query complies with security policy."
