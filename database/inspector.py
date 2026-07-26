"""
Database schema inspection utilities.

Provides functions to introspect database structure including
tables, columns, constraints, indexes, and relationships
using SQLAlchemy's inspection API.
"""

from typing import Any, Optional

import pandas as pd
from sqlalchemy import inspect, text
from langchain_community.utilities import SQLDatabase

from utils.logger import setup_logger

logger = setup_logger(__name__)


def clear_schema_cache() -> None:
    """Clear all Streamlit data caches when database schema or rows mutate."""
    try:
        import streamlit as st
        st.cache_data.clear()
        logger.info("Cleared Streamlit data cache following database mutation.")
    except Exception as e:
        logger.error("Failed to clear schema cache: %s", e)


def get_database_info(db: SQLDatabase) -> dict[str, Any]:
    """Get basic database metadata.

    Args:
        db: A configured SQLDatabase instance.

    Returns:
        Dictionary with dialect, db_name, and driver info.
    """
    engine = db._engine
    dialect = engine.dialect.name

    if dialect == "sqlite":
        url_db = engine.url.database
        from pathlib import Path as _Path
        db_name = _Path(str(url_db)).name if url_db else "unknown"
    else:
        db_name = engine.url.database or "unknown"

    return {
        "dialect": dialect,
        "db_name": db_name,
        "driver": getattr(engine.dialect, "driver", dialect),
    }


def get_table_names(db: SQLDatabase) -> list[str]:
    """Get all table names in the connected database.

    Args:
        db: A configured SQLDatabase instance.

    Returns:
        Sorted list of table name strings.
    """
    try:
        inspector = inspect(db._engine)
        return sorted(inspector.get_table_names())
    except Exception as e:
        logger.error("Failed to get table names: %s", e)
        return []


def get_row_count(db: SQLDatabase, table_name: str) -> int:
    """Get the row count for a specific table.

    Args:
        db: A configured SQLDatabase instance.
        table_name: The name of the table to count.

    Returns:
        Number of rows in the table, or 0 on error.
    """
    try:
        with db._engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT COUNT(*) FROM `{table_name}`")
            )
            return result.scalar() or 0
    except Exception as e:
        logger.error("Failed to get row count for %s: %s", table_name, e)
        return 0


def get_columns(db: SQLDatabase, table_name: str) -> list[dict[str, Any]]:
    """Get column details for a specific table.

    Args:
        db: A configured SQLDatabase instance.
        table_name: The name of the table.

    Returns:
        List of column dictionaries with name, type, nullable, default.
    """
    try:
        inspector = inspect(db._engine)
        columns = inspector.get_columns(table_name)
        return [
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "default": col.get("default"),
            }
            for col in columns
        ]
    except Exception as e:
        logger.error("Failed to get columns for %s: %s", table_name, e)
        return []


def get_primary_keys(db: SQLDatabase, table_name: str) -> list[str]:
    """Get primary key column names for a table.

    Args:
        db: A configured SQLDatabase instance.
        table_name: The name of the table.

    Returns:
        List of primary key column name strings.
    """
    try:
        inspector = inspect(db._engine)
        pk_constraint = inspector.get_pk_constraint(table_name)
        return pk_constraint.get("constrained_columns", [])
    except Exception as e:
        logger.error("Failed to get primary keys for %s: %s", table_name, e)
        return []


def get_foreign_keys(db: SQLDatabase, table_name: str) -> list[dict[str, Any]]:
    """Get foreign key relationships for a table.

    Args:
        db: A configured SQLDatabase instance.
        table_name: The name of the table.

    Returns:
        List of foreign key dictionaries with constrained_columns,
        referred_table, and referred_columns.
    """
    try:
        inspector = inspect(db._engine)
        return inspector.get_foreign_keys(table_name)
    except Exception as e:
        logger.error("Failed to get foreign keys for %s: %s", table_name, e)
        return []


def get_indexes(db: SQLDatabase, table_name: str) -> list[dict[str, Any]]:
    """Get index information for a table.

    Args:
        db: A configured SQLDatabase instance.
        table_name: The name of the table.

    Returns:
        List of index dictionaries with name, columns, and unique flag.
    """
    try:
        inspector = inspect(db._engine)
        return inspector.get_indexes(table_name)
    except Exception as e:
        logger.error("Failed to get indexes for %s: %s", table_name, e)
        return []


def get_table_schema(db: SQLDatabase, table_name: str) -> dict[str, Any]:
    """Get comprehensive schema information for a table.

    Combines columns, primary keys, foreign keys, indexes,
    and row count into a single dictionary.

    Args:
        db: A configured SQLDatabase instance.
        table_name: The name of the table.

    Returns:
        Dictionary with complete schema metadata.
    """
    columns = get_columns(db, table_name)
    primary_keys = get_primary_keys(db, table_name)
    foreign_keys = get_foreign_keys(db, table_name)
    indexes = get_indexes(db, table_name)
    row_count = get_row_count(db, table_name)

    return {
        "table_name": table_name,
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "indexes": indexes,
        "row_count": row_count,
        "column_count": len(columns),
    }


def get_table_preview_df(
    db: SQLDatabase,
    table_name: str,
    limit: int = 50,
) -> pd.DataFrame:
    """Get a preview of table data as a pandas DataFrame.

    Args:
        db: A configured SQLDatabase instance.
        table_name: The name of the table.
        limit: Maximum number of rows to return (default: 50).

    Returns:
        A pandas DataFrame with the first `limit` rows.
    """
    try:
        with db._engine.connect() as conn:
            df = pd.read_sql(
                text(f"SELECT * FROM `{table_name}` LIMIT :limit"),
                conn,
                params={"limit": limit},
            )
            return df
    except Exception as e:
        logger.error("Failed to get preview for %s: %s", table_name, e)
        return pd.DataFrame()


def get_all_tables_summary(db: SQLDatabase) -> list[dict[str, Any]]:
    """Get a quick summary of all tables in the database.

    Args:
        db: A configured SQLDatabase instance.

    Returns:
        List of dictionaries, each with name, row_count, and column_count.
    """
    tables = get_table_names(db)
    summaries = []
    for table in tables:
        row_count = get_row_count(db, table)
        columns = get_columns(db, table)
        summaries.append({
            "name": table,
            "row_count": row_count,
            "column_count": len(columns),
        })
    return summaries
