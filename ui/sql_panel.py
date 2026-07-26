"""
SQL Preview & Metadata Panel UI Component with AI Explainer and Data Insights.

Displays execution metrics, timing performance, affected row count,
generated SQL statements, status indicators, interactive AI SQL explanations,
and automated statistical data insights (Highest, Lowest, Mean, Median, Outliers, Patterns).
"""

import streamlit as st
import pandas as pd
from typing import Optional
from langchain_groq import ChatGroq

from services.sql_explainer import explain_sql_query
from services.ai_insights import analyze_dataframe_insights


def render_sql_panel(
    sql: str,
    execution_time_ms: Optional[float] = None,
    rows_affected: Optional[int] = None,
    success: bool = True,
    sql_type: Optional[str] = "SELECT",
    explanation: Optional[str] = None,
    expanded: bool = True,
    llm: Optional[ChatGroq] = None,
    df: Optional[pd.DataFrame] = None,
    key_prefix: str = "sql_panel",
) -> None:
    """Render a dedicated SQL execution preview panel with metrics, AI Explainer, and Insights.

    Args:
        sql: The executed or generated SQL statement.
        execution_time_ms: Query runtime in milliseconds.
        rows_affected: Number of rows returned or modified.
        success: Execution status (True for success, False for error).
        sql_type: Operation type (SELECT, INSERT, UPDATE, DELETE, etc.).
        explanation: Optional brief AI explanation of the query.
        expanded: Whether the details expander is open by default.
        llm: Optional ChatGroq LLM for generating deep explanations and insights.
        df: Optional pandas DataFrame for statistical insights.
        key_prefix: Unique prefix for Streamlit widget keys.
    """
    title = f"💻 SQL Execution Panel — {sql_type.upper() if sql_type else 'QUERY'}"

    with st.expander(title, expanded=expanded):
        # Metrics row
        col1, col2, col3 = st.columns(3)

        with col1:
            time_str = f"{execution_time_ms:.1f} ms" if execution_time_ms is not None else "—"
            st.metric("⏱️ Execution Time", time_str)

        with col2:
            row_label = "Rows Returned" if sql_type == "SELECT" else "Rows Affected"
            row_str = f"{rows_affected:,}" if rows_affected is not None else "—"
            st.metric(f"📊 {row_label}", row_str)

        with col3:
            status_str = "✅ SUCCESS" if success else "❌ FAILED"
            st.metric("🟢 Status", status_str)

        # SQL Code block
        st.caption("Generated SQL Query:")
        st.code(sql, language="sql")

        # Optional summary text
        if explanation:
            st.info(f"💡 **AI Summary**: {explanation}")

        # Action Buttons: Explain SQL & Generate Insights
        b_col1, b_col2 = st.columns(2)

        btn_explain_key = f"{key_prefix}_explain_{hash(sql)}"
        btn_insights_key = f"{key_prefix}_insights_{hash(sql)}"

        with b_col1:
            if st.button("💡 Explain SQL (Deep Analysis)", key=btn_explain_key, width="stretch"):
                with st.spinner("Generating AI query explanation..."):
                    deep_exp = explain_sql_query(sql, llm=llm)
                    st.session_state[f"exp_{btn_explain_key}"] = deep_exp

        with b_col2:
            if df is not None and not df.empty:
                if st.button("📈 Generate AI Data Insights", key=btn_insights_key, width="stretch"):
                    with st.spinner("Analyzing dataset metrics & outliers..."):
                        insights_res = analyze_dataframe_insights(df, llm=llm)
                        st.session_state[f"ins_{btn_insights_key}"] = insights_res

        # Render Explanation Output
        if f"exp_{btn_explain_key}" in st.session_state:
            st.markdown("---")
            st.markdown("#### 📖 AI Query Explanation")
            st.markdown(st.session_state[f"exp_{btn_explain_key}"])

        # Render Data Insights Output
        if f"ins_{btn_insights_key}" in st.session_state:
            ins = st.session_state[f"ins_{btn_insights_key}"]
            st.markdown("---")
            st.markdown("#### 🤖 AI Dataset Insights & Statistics")

            # Numeric Stats Table
            if ins["numeric_stats"]:
                st.caption("Numeric Column Metrics (Highest, Lowest, Mean, Median):")
                stat_rows = []
                for c_name, s in ins["numeric_stats"].items():
                    stat_rows.append({
                        "Column": c_name,
                        "Highest (Max)": s["max"],
                        "Lowest (Min)": s["min"],
                        "Average (Mean)": s["mean"],
                        "Median": s["median"],
                        "Std Dev": s["std"],
                        "Outliers Found": s["outlier_count"],
                    })
                st.dataframe(pd.DataFrame(stat_rows), width="stretch", hide_index=True)

            # AI Summary & Patterns
            if ins["ai_summary"]:
                st.markdown(ins["ai_summary"])
