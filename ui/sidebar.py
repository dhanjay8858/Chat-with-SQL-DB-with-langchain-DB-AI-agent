"""
Sidebar UI components.

Renders the database selection, credential inputs,
and API key configuration in the Streamlit sidebar.
"""

import streamlit as st
from typing import Any

from langchain_community.utilities import SQLDatabase

from config.settings import LOCALDB, MYSQLDB
from database.inspector import get_database_info, get_all_tables_summary


def render_sidebar() -> dict[str, Any]:
    """Render sidebar UI and return the user's configuration.

    Displays:
        - Database type radio button (SQLite / MySQL)
        - MySQL credential inputs (conditional)
        - Groq API key input

    Returns:
        A dictionary containing:
            - db_url: Database type identifier (LOCALDB or MYSQLDB)
            - mysql_host: MySQL hostname (or None)
            - mysql_user: MySQL username (or None)
            - mysql_password: MySQL password (or None)
            - mysql_db: MySQL database name (or None)
            - groq_api_key: The Groq API key string
    """
    radio_option = [
        "Use SQLite3 DataBase(student.db)",
        "Connect to MYSLQ DataBase",
    ]
    selected_option = st.sidebar.radio(
        "Choose the DB you want to Chat with", options=radio_option
    )

    mysql_host = None
    mysql_user = None
    mysql_password = None
    mysql_db = None

    if selected_option == radio_option[1]:
        db_url = MYSQLDB
        mysql_host = st.sidebar.text_input("Provide MYSQL Hostname", value="localhost")
        mysql_user = st.sidebar.text_input("Provide MYSQL Username", value="root")
        mysql_password = st.sidebar.text_input("provide MYSQL Password", type="password")
        mysql_db = st.sidebar.text_input("Provide MYSQL  Database Name")
    else:
        db_url = LOCALDB

    groq_api_key = st.sidebar.text_input(
        "Provide with the groq API Key :", type="password"
    )

    model_options = [
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
    ]
    selected_model = st.sidebar.selectbox(
        "🤖 Select Groq Model",
        options=model_options,
        index=0,
        help="Choose the LLM model hosted on Groq.",
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("🛡️ Security Mode")
    from config.security import MODE_ADMIN, MODE_READ_ONLY, init_security_state
    init_security_state()

    current_mode = st.session_state.get("security_mode", MODE_ADMIN)
    selected_mode = st.sidebar.radio(
        "Access Level",
        options=[MODE_ADMIN, MODE_READ_ONLY],
        index=0 if current_mode == MODE_ADMIN else 1,
        key="sidebar_security_mode_radio",
    )
    st.session_state["security_mode"] = selected_mode

    return {
        "db_url": db_url,
        "mysql_host": mysql_host,
        "mysql_user": mysql_user,
        "mysql_password": mysql_password,
        "mysql_db": mysql_db,
        "groq_api_key": groq_api_key,
        "selected_model": selected_model,
        "security_mode": selected_mode,
    }


def render_db_info(db: SQLDatabase) -> None:
    """Render database metadata in the sidebar.

    Displays the connected database type, name, total table count,
    and a per-table summary with row and column counts.

    Args:
        db: A configured SQLDatabase instance.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Database Explorer")

    db_info = get_database_info(db)

    dialect_label = db_info["dialect"].upper()
    dialect_icon = "🟢" if dialect_label == "SQLITE" else "🔵"
    st.sidebar.markdown(f"{dialect_icon} **Type:** {dialect_label}")
    st.sidebar.markdown(f"📁 **Database:** `{db_info['db_name']}`")

    tables = get_all_tables_summary(db)
    st.sidebar.markdown(f"📋 **Tables:** {len(tables)}")

    if tables:
        st.sidebar.markdown("---")
        for table in tables:
            with st.sidebar.expander(
                f"📋 {table['name']}  •  {table['row_count']} rows  •  {table['column_count']} cols"
            ):
                st.caption(f"Rows: **{table['row_count']:,}**")
                st.caption(f"Columns: **{table['column_count']}**")
                st.info(
                    "Switch to the **🗂️ Explorer** tab for full schema details.",
                    icon="💡",
                )
