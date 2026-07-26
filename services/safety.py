"""
Safety Middleware Service.

Provides security checks, impact explanations, and confirmation state management
for database operations. Intercepts write and DDL SQL statements to enforce
the Safe Execution Layer workflow.
"""

from typing import Any, Optional
from langchain_community.utilities import SQLDatabase

from database.crud import get_affected_table
from utils.validators import analyze_sql_risk
from utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_impact_explanation(sql: str, risk_analysis: dict[str, Any]) -> str:
    """Generate a human-readable explanation of what the SQL statement will do.

    Args:
        sql: The SQL statement.
        risk_analysis: Output from analyze_sql_risk.

    Returns:
        String explanation of query purpose and database impact.
    """
    op = risk_analysis.get("operation", "UNKNOWN")
    table = get_affected_table(sql) or "database table"
    warnings = risk_analysis.get("warnings", [])

    explanation_lines = []

    if op == "INSERT":
        explanation_lines.append(f"This query will **INSERT new record(s)** into `{table}`.")
    elif op == "UPDATE":
        explanation_lines.append(f"This query will **UPDATE existing row(s)** in `{table}`.")
    elif op == "DELETE":
        explanation_lines.append(f"This query will **DELETE record(s)** from `{table}`.")
    elif op == "DDL":
        explanation_lines.append(f"This query will **MODIFY STRUCTURAL DEFINITION** of `{table}`.")
    else:
        explanation_lines.append(f"This query will perform a **{op}** operation on `{table}`.")

    if warnings:
        explanation_lines.append("\n**Safety Warnings:**")
        for w in warnings:
            explanation_lines.append(f"- {w}")

    return "\n".join(explanation_lines)


def evaluate_query_safety(sql: str) -> dict[str, Any]:
    """Evaluate a SQL statement and build safety metadata.

    Args:
        sql: The target SQL query.

    Returns:
        Dict with risk_analysis, explanation, and action metadata.
    """
    risk = analyze_sql_risk(sql)
    explanation = generate_impact_explanation(sql, risk)

    return {
        "sql": sql,
        "risk_level": risk["risk_level"],
        "requires_confirmation": risk["requires_confirmation"],
        "warnings": risk["warnings"],
        "operation": risk["operation"],
        "explanation": explanation,
    }
