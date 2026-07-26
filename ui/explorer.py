"""
Database Explorer UI panel with Data Quality & Analytics.

Renders the full database explorer experience in the main content area,
including table selection, schema details, constraints, data quality checks, and data preview.
"""

import streamlit as st
import pandas as pd
from typing import Optional
from langchain_community.utilities import SQLDatabase

from database.inspector import (
    get_table_names,
    get_table_schema,
)
from services.ai_insights import (
    check_missing_values,
    check_duplicate_records,
    get_numeric_summary,
)
from ui.preview import render_table_preview


def render_explorer(db: SQLDatabase) -> None:
    """Render the complete Database Explorer panel.

    Displays a table selector, schema overview with metrics,
    column details, constraints, data quality analytics, and data preview grid.

    Args:
        db: A configured SQLDatabase instance.
    """
    st.header("🗂️ Database Explorer")

    tables = get_table_names(db)

    if not tables:
        st.warning("No tables found in the connected database.")
        return

    # ─── Table Selector ───
    selected_table = st.selectbox(
        "Select a table to inspect",
        options=tables,
        key="explorer_table_select",
    )

    if not selected_table:
        return

    schema = get_table_schema(db, selected_table)

    # ─── Overview Metrics ───
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Rows", f"{schema['row_count']:,}")
    col2.metric("📋 Columns", schema["column_count"])
    col3.metric("🔑 Primary Keys", len(schema["primary_keys"]))
    col4.metric("🔗 Foreign Keys", len(schema["foreign_keys"]))

    # ─── Column Details ───
    st.markdown("---")
    st.subheader("📋 Column Details")

    columns_data = []
    for col in schema["columns"]:
        is_pk = "✅" if col["name"] in schema["primary_keys"] else ""
        columns_data.append({
            "Column": col["name"],
            "Type": col["type"],
            "Nullable": "Yes" if col["nullable"] else "No",
            "Default": str(col["default"]) if col["default"] is not None else "—",
            "PK": is_pk,
        })

    if columns_data:
        st.dataframe(
            pd.DataFrame(columns_data),
            width="stretch",
            hide_index=True,
        )

    # ─── Data Quality & Analytics Section ───
    st.markdown("---")
    st.subheader("📈 Data Quality & Column Analytics")

    q_col1, q_col2, q_col3 = st.columns(3)

    # Missing values
    missing_map = check_missing_values(db, selected_table)
    total_missing = sum(missing_map.values())
    q_col1.metric("⚠️ Missing Values (NULL)", total_missing)

    # Duplicate records
    duplicates = check_duplicate_records(db, selected_table)
    q_col2.metric("👯 Duplicate Records", duplicates)

    # Numeric columns count
    numeric_stats = get_numeric_summary(db, selected_table)
    q_col3.metric("🔢 Numeric Columns", len(numeric_stats))

    if numeric_stats:
        with st.expander("📊 Statistical Summary (Min, Max, Avg)", expanded=False):
            num_rows = []
            for col, s in numeric_stats.items():
                num_rows.append({
                    "Column": col,
                    "Min": s["min"],
                    "Max": s["max"],
                    "Average": s["avg"],
                })
            st.dataframe(pd.DataFrame(num_rows), width="stretch", hide_index=True)

    if total_missing > 0:
        with st.expander("⚠️ Missing Values per Column", expanded=False):
            m_rows = [{"Column": k, "NULL Count": v} for k, v in missing_map.items() if v > 0]
            st.dataframe(pd.DataFrame(m_rows), width="stretch", hide_index=True)

    # ─── Constraints Section ───
    st.markdown("---")
    constraint_col1, constraint_col2 = st.columns(2)

    # Primary Keys
    with constraint_col1:
        st.subheader("🔑 Primary Keys")
        if schema["primary_keys"]:
            for pk in schema["primary_keys"]:
                st.code(pk, language=None)
        else:
            st.caption("No primary keys defined.")

    # Foreign Keys
    with constraint_col2:
        st.subheader("🔗 Foreign Keys")
        if schema["foreign_keys"]:
            for fk in schema["foreign_keys"]:
                constrained = ", ".join(fk.get("constrained_columns", []))
                referred_table = fk.get("referred_table", "?")
                referred_cols = ", ".join(fk.get("referred_columns", []))
                st.code(
                    f"{constrained} → {referred_table}({referred_cols})",
                    language=None,
                )
        else:
            st.caption("No foreign keys defined.")

    # ─── Indexes ───
    st.subheader("📇 Indexes")
    if schema["indexes"]:
        indexes_data = []
        for idx in schema["indexes"]:
            indexes_data.append({
                "Name": idx.get("name", "—"),
                "Columns": ", ".join(idx.get("column_names", [])),
                "Unique": "Yes" if idx.get("unique") else "No",
            })
        st.dataframe(
            pd.DataFrame(indexes_data),
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption("No indexes defined.")

    # ─── Data Preview ───
    st.markdown("---")
    st.subheader("👀 Data Preview")
    render_table_preview(db, selected_table)
