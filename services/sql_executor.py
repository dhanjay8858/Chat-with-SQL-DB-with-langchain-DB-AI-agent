"""
Centralized SQL execution engine.

Provides structured SQL execution with timing measurement,
query classification, row counting, and result formatting.
Used by CRUD operations, query history re-runs, and the safety layer.
"""

import re
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import pandas as pd
from sqlalchemy import text
from langchain_community.utilities import SQLDatabase

from database.inspector import clear_schema_cache
from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ExecutionResult:
    """Structured result from SQL execution.

    Attributes:
        sql: The executed SQL statement.
        sql_type: Classification of the SQL (SELECT, INSERT, etc.).
        success: Whether execution completed without error.
        data: DataFrame of results (SELECT queries only).
        rows_affected: Number of rows returned or modified.
        execution_time_ms: Execution duration in milliseconds.
        error: Error message if execution failed.
        message: Human-readable summary of the result.
    """

    sql: str
    sql_type: str
    success: bool
    data: Optional[pd.DataFrame] = None
    rows_affected: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    message: str = ""


def classify_sql(sql: str) -> str:
    """Classify a SQL statement by its operation type.

    Args:
        sql: The SQL statement to classify.

    Returns:
        One of: "SELECT", "INSERT", "UPDATE", "DELETE",
        "DDL", or "UNKNOWN".
    """
    cleaned = sql.strip().upper()

    # Remove leading comments
    cleaned = re.sub(r"^(/\*.*?\*/|--[^\n]*\n)\s*", "", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip()

    if cleaned.startswith("SELECT") or cleaned.startswith("WITH"):
        return "SELECT"
    elif cleaned.startswith("INSERT"):
        return "INSERT"
    elif cleaned.startswith("UPDATE"):
        return "UPDATE"
    elif cleaned.startswith("DELETE"):
        return "DELETE"
    elif cleaned.startswith(("DROP", "ALTER", "TRUNCATE", "CREATE")):
        return "DDL"
    else:
        return "UNKNOWN"


def is_write_operation(sql: str) -> bool:
    """Check if a SQL statement modifies data.

    Args:
        sql: The SQL statement to check.

    Returns:
        True if the statement writes to the database.
    """
    sql_type = classify_sql(sql)
    return sql_type in ("INSERT", "UPDATE", "DELETE", "DDL")


def execute_sql(db: SQLDatabase, sql: str) -> ExecutionResult:
    """Execute a SQL statement and return a structured result.

    Handles both read (SELECT) and write (INSERT/UPDATE/DELETE)
    operations. Measures execution time and counts affected rows.

    Args:
        db: A configured SQLDatabase instance.
        sql: The SQL statement to execute.

    Returns:
        An ExecutionResult with query details and outcome.
    """
    sql_type = classify_sql(sql)
    start_time = time.perf_counter()

    try:
        with db._engine.begin() as conn:
            result = conn.execute(text(sql))
            execution_time = (time.perf_counter() - start_time) * 1000

            if sql_type == "SELECT":
                rows = result.fetchall()
                columns = list(result.keys())
                df = pd.DataFrame(rows, columns=columns)

                logger.info(
                    "SELECT executed: %d rows in %.1f ms",
                    len(df),
                    execution_time,
                )

                return ExecutionResult(
                    sql=sql,
                    sql_type=sql_type,
                    success=True,
                    data=df,
                    rows_affected=len(df),
                    execution_time_ms=round(execution_time, 2),
                    message=f"Returned {len(df)} row(s)",
                )
            else:
                rows_affected = result.rowcount if result.rowcount >= 0 else 0
                clear_schema_cache()

                logger.info(
                    "%s executed: %d row(s) affected in %.1f ms",
                    sql_type,
                    rows_affected,
                    execution_time,
                )

                return ExecutionResult(
                    sql=sql,
                    sql_type=sql_type,
                    success=True,
                    rows_affected=rows_affected,
                    execution_time_ms=round(execution_time, 2),
                    message=f"{sql_type} executed successfully. "
                    f"{rows_affected} row(s) affected.",
                )

    except Exception as e:
        execution_time = (time.perf_counter() - start_time) * 1000
        logger.error("SQL execution failed: %s — %s", sql_type, e)

        return ExecutionResult(
            sql=sql,
            sql_type=sql_type,
            success=False,
            execution_time_ms=round(execution_time, 2),
            error=str(e),
            message=f"Error executing {sql_type}: {e}",
        )
