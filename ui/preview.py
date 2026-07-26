"""
Table data preview component.

Renders an interactive preview of table data using the Interactive Data Grid.
"""

import streamlit as st
from langchain_community.utilities import SQLDatabase

from database.inspector import get_table_preview_df
from ui.data_grid import render_interactive_grid


def render_table_preview(
    db: SQLDatabase,
    table_name: str,
    default_limit: int = 100,
) -> None:
    """Render an interactive data preview grid for a database table.

    Args:
        db: A configured SQLDatabase instance.
        table_name: The name of the table to preview.
        default_limit: Maximum rows to fetch for preview.
    """
    df = get_table_preview_df(db, table_name, limit=default_limit)

    if df.empty:
        st.info("This table has no data.")
        return

    render_interactive_grid(
        df,
        key=f"preview_grid_{table_name}",
        default_page_size=10,
        show_controls=True,
        show_download=True,
    )
