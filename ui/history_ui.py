"""
Query History UI Tab Component.

Renders query logs, search filtering, re-run execution controls,
individual deletion, and clear history actions.
"""

import streamlit as st
from langchain_community.utilities import SQLDatabase

from history.query_history import (
    load_history,
    delete_query_log,
    clear_all_history,
    search_history,
)
from services.sql_executor import execute_sql
from ui.data_grid import render_interactive_grid
from ui.sql_panel import render_sql_panel


def render_history_tab(db: SQLDatabase) -> None:
    """Render the Query History management interface.

    Args:
        db: Configured SQLDatabase instance for re-running queries.
    """
    st.header("📜 Query History")

    # Top Toolbar: Search + Clear All
    c1, c2 = st.columns([3, 1])

    with c1:
        search_query = st.text_input(
            "🔍 Search history",
            placeholder="Filter by question, SQL keyword, or timestamp...",
            key="history_search_input",
        )

    with c2:
        st.write(" ")
        st.write(" ")
        if st.button("🗑️ Clear History", key="btn_clear_history_all", type="secondary", width="stretch"):
            clear_all_history()
            st.toast("Query history cleared!", icon="🧹")
            st.rerun()

    items = search_history(search_query)

    if not items:
        st.info("No query history recorded yet." if not search_query else "No matching history items found.")
        return

    st.caption(f"Showing **{len(items)}** recorded query execution(s)")

    # Render History Cards
    for idx, item in enumerate(items):
        item_id = item["id"]
        status_color = "🟢" if item["status"] == "SUCCESS" else "🔴"
        title = f"{status_color} [{item['timestamp']}] {item['question']} ({item['rows_affected']} rows, {item['execution_time_ms']} ms)"

        with st.expander(title, expanded=(idx == 0)):
            st.markdown(f"**Question:** {item['question']}")
            st.code(item["sql"], language="sql")

            col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
            col_meta1.caption(f"📅 **Time:** {item['timestamp']}")
            col_meta2.caption(f"⏱️ **Runtime:** {item['execution_time_ms']} ms")
            col_meta3.caption(f"📊 **Rows:** {item['rows_affected']}")
            col_meta4.caption(f"🟢 **Status:** {item['status']}")

            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                if st.button(f"🔄 Re-run Query", key=f"rerun_{item_id}_{idx}", type="primary", width="stretch"):
                    result = execute_sql(db, item["sql"])
                    st.session_state[f"rerun_res_{item_id}"] = result

            with btn_col2:
                if st.button(f"🗑️ Delete Log", key=f"del_{item_id}_{idx}", width="stretch"):
                    delete_query_log(item_id)
                    st.toast("Entry deleted.", icon="🗑️")
                    st.rerun()

            # Render re-run result if available
            if f"rerun_res_{item_id}" in st.session_state:
                res = st.session_state[f"rerun_res_{item_id}"]
                st.markdown("---")
                st.subheader("🔄 Re-run Output")
                render_sql_panel(
                    sql=item["sql"],
                    execution_time_ms=res.execution_time_ms,
                    rows_affected=res.rows_affected,
                    success=res.success,
                    sql_type=res.sql_type,
                )
                if res.data is not None and not res.data.empty:
                    render_interactive_grid(res.data, key=f"rerun_grid_{item_id}")
