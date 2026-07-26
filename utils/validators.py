"""
SQL Security and Safety Validators.

Analyzes SQL statements for potential risk, dangerous operations
(DROP, TRUNCATE, mass DELETE/UPDATE without WHERE clause), and determines
whether explicit user confirmation is required prior to execution.
"""

import re
from typing import Any

from services.sql_executor import classify_sql
from utils.logger import setup_logger

logger = setup_logger(__name__)

# High risk operation keywords
CRITICAL_KEYWORDS = ["DROP", "TRUNCATE", "ALTER"]
HIGH_RISK_KEYWORDS = ["DELETE", "UPDATE"]
MEDIUM_RISK_KEYWORDS = ["INSERT"]


def analyze_sql_risk(sql: str) -> dict[str, Any]:
    """Analyze a SQL statement for potential security and operational risks.

    Args:
        sql: The raw or generated SQL query string.

    Returns:
        Dict containing:
            - sql: The cleaned SQL query.
            - operation: Operation type (SELECT, INSERT, UPDATE, DELETE, DDL, UNKNOWN).
            - risk_level: SAFE, LOW, MEDIUM, HIGH, CRITICAL.
            - requires_confirmation: True if user approval is required before execution.
            - warnings: List of warning strings detailing why risk was assigned.
    """
    cleaned = sql.strip()
    operation = classify_sql(cleaned)
    upper_sql = cleaned.upper()

    warnings: list[str] = []
    risk_level = "SAFE"
    requires_confirmation = False

    # 1. Check for Critical DDL operations
    if any(re.search(rf"\b{kw}\b", upper_sql) for kw in CRITICAL_KEYWORDS):
        risk_level = "CRITICAL"
        requires_confirmation = True
        if "DROP DATABASE" in upper_sql or "DROP SCHEMA" in upper_sql:
            warnings.append("⚠️ CRITICAL: Statement attempts to DROP a database/schema!")
        elif "DROP TABLE" in upper_sql:
            warnings.append("⚠️ CRITICAL: Statement attempts to DROP a table structure!")
        elif "TRUNCATE" in upper_sql:
            warnings.append("⚠️ CRITICAL: Statement attempts to TRUNCATE all table data!")
        elif "ALTER" in upper_sql:
            warnings.append("⚠️ CRITICAL: Statement modifies table schema (ALTER)!")

    # 2. Check for DELETE operations
    elif operation == "DELETE" or "DELETE FROM" in upper_sql:
        requires_confirmation = True
        has_where = bool(re.search(r"\bWHERE\b", upper_sql))

        if not has_where:
            risk_level = "CRITICAL"
            warnings.append("⚠️ CRITICAL: DELETE operation without WHERE clause! This will delete ALL rows in the table.")
        else:
            risk_level = "HIGH"
            warnings.append("⚡ HIGH RISK: DELETE operation will permanently remove records.")

    # 3. Check for UPDATE operations
    elif operation == "UPDATE" or re.search(r"\bUPDATE\b", upper_sql):
        requires_confirmation = True
        has_where = bool(re.search(r"\bWHERE\b", upper_sql))

        if not has_where:
            risk_level = "HIGH"
            warnings.append("⚡ HIGH RISK: UPDATE operation without WHERE clause! This will modify ALL rows in the table.")
        else:
            risk_level = "MEDIUM"
            warnings.append("⚠️ MEDIUM RISK: UPDATE operation will modify existing records.")

    # 4. Check for INSERT operations
    elif operation == "INSERT" or "INSERT INTO" in upper_sql:
        requires_confirmation = True
        risk_level = "LOW"
        warnings.append("ℹ️ LOW RISK: INSERT operation will add new records.")

    # 5. Read-only SELECT operations
    else:
        risk_level = "SAFE"
        requires_confirmation = False

    logger.info("SQL Safety Analysis: type=%s, risk=%s, requires_confirm=%s", operation, risk_level, requires_confirmation)

    return {
        "sql": cleaned,
        "operation": operation,
        "risk_level": risk_level,
        "requires_confirmation": requires_confirmation,
        "warnings": warnings,
    }
