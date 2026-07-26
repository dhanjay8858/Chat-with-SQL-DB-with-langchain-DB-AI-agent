"""
AI Database Assistant — Main Application Entry Point.

A natural language interface for SQL databases powered by
LangChain SQL Agent and Groq's Llama 3.3 70B model.

Run with: streamlit run app.py
"""

import streamlit as st

from config.settings import APP_TITLE, MYSQLDB, get_llm
from database.connection import configure_db
from agents.sql_agent import create_sql_agent_instance
from ui.sidebar import render_sidebar, render_db_info
from ui.chat import init_chat_history, render_chat_messages, handle_user_input
from ui.explorer import render_explorer
from ui.history_ui import render_history_tab
from ui.styles import apply_custom_css


# ─── Page Setup & Custom CSS ───
st.title(APP_TITLE)
apply_custom_css()

# ─── Sidebar Configuration ───
sidebar_config = render_sidebar()

# ─── API Key Validation ───
if not sidebar_config["groq_api_key"]:
    st.info("Please Provide groq API Key to continue")
    st.stop()

# ─── LLM Initialization ───
selected_model_name = sidebar_config.get("selected_model", "openai/gpt-oss-120b")
model = get_llm(sidebar_config["groq_api_key"], model_name=selected_model_name)

# ─── Database Connection ───
if sidebar_config["db_url"] == MYSQLDB:
    db = configure_db(
        sidebar_config["db_url"],
        sidebar_config["mysql_host"],
        sidebar_config["mysql_user"],
        sidebar_config["mysql_password"],
        sidebar_config["mysql_db"],
    )
else:
    db = configure_db(sidebar_config["db_url"])

# ─── Database Explorer Sidebar ───
render_db_info(db)

# ─── SQL Agent ───
agent = create_sql_agent_instance(db, model)

# ─── Main Content (Tabs) ───
tab_chat, tab_explorer, tab_history = st.tabs(["💬 Chat", "🗂️ Database Explorer", "📜 Query History"])

with tab_chat:
    init_chat_history()
    render_chat_messages(model)
    handle_user_input(agent, db, model)

with tab_explorer:
    render_explorer(db)

with tab_history:
    render_history_tab(db)
