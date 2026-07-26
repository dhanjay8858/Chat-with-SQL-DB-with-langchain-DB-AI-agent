"""
CRUD operation utilities.

Provides helper functions for classifying, validating,
and extracting metadata from CRUD SQL operations.
"""

import re
from typing import Optional

from langchain_community.utilities import SQLDatabase

from database.inspector import get_table_names, get_columns
from services.sql_executor import (
    ExecutionResult,
    classify_sql,
    execute_sql,
    is_write_operation,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


def execute_crud(db: SQLDatabase, sql: str) -> ExecutionResult:
    """Execute a CRUD operation with logging.

    Thin wrapper around execute_sql that adds CRUD-specific
    logging and validation.

    Args:
        db: A configured SQLDatabase instance.
        sql: The SQL statement to execute.

    Returns:
        An ExecutionResult with the operation outcome.
    """
    sql_type = classify_sql(sql)
    logger.info("CRUD operation: %s", sql_type)
    return execute_sql(db, sql)


def get_affected_table(sql: str) -> Optional[str]:
    """Extract the target table name from a SQL statement.

    Handles SELECT, INSERT, UPDATE, DELETE statements.

    Args:
        sql: The SQL statement to parse.

    Returns:
        The table name if found, otherwise None.
    """
    cleaned = sql.strip()
    sql_type = classify_sql(cleaned)

    patterns = {
        "SELECT": r"FROM\s+[`\"\[]?(\w+)[`\"\]]?",
        "INSERT": r"INTO\s+[`\"\[]?(\w+)[`\"\]]?",
        "UPDATE": r"UPDATE\s+[`\"\[]?(\w+)[`\"\]]?",
        "DELETE": r"FROM\s+[`\"\[]?(\w+)[`\"\]]?",
    }

    pattern = patterns.get(sql_type)
    if pattern:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def get_table_columns_description(db: SQLDatabase, table_name: str) -> str:
    """Get a human-readable description of table columns.

    Useful for providing context to the AI agent.

    Args:
        db: A configured SQLDatabase instance.
        table_name: The name of the table.

    Returns:
        Formatted string like "NAME (VARCHAR(25)), CLASS (VARCHAR(25)), ..."
    """
    columns = get_columns(db, table_name)
    return ", ".join(f"{c['name']} ({c['type']})" for c in columns)


def validate_crud_tables(db: SQLDatabase, sql: str) -> tuple[bool, str]:
    """Validate that the SQL references existing tables.

    Args:
        db: A configured SQLDatabase instance.
        sql: The SQL statement to validate.

    Returns:
        Tuple of (is_valid, message).
    """
    table = get_affected_table(sql)
    if not table:
        return True, "Could not determine target table."

    existing_tables = [t.upper() for t in get_table_names(db)]
    if table.upper() not in existing_tables:
        return False, f"Table '{table}' does not exist in the database."

    return True, f"Table '{table}' exists."
