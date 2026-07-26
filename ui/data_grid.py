"""
Interactive Data Grid UI Component with Charting Integration.

Provides a feature-rich data grid with real-time text searching, column filtering,
sorting, pagination, column resizing, CSV export, and Plotly charts integration.
"""

import math
import streamlit as st
import pandas as pd
from typing import Optional

from charts.visualizer import render_auto_visualization, analyze_dataframe_for_charts
from exports import export_to_csv, export_to_excel, export_to_json, export_to_pdf


def filter_dataframe(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """Filter DataFrame rows based on search substring match across any column.

    Args:
        df: Input DataFrame.
        search_term: Substring query string.

    Returns:
        Filtered DataFrame.
    """
    if not search_term:
        return df

    term = search_term.strip().lower()
    mask = df.astype(str).apply(lambda row: row.str.lower().str.contains(term, regex=False).any(), axis=1)
    return df[mask]


def render_interactive_grid(
    df: pd.DataFrame,
    key: str = "data_grid",
    default_page_size: int = 10,
    show_controls: bool = True,
    show_download: bool = True,
    show_charts: bool = True,
) -> None:
    """Render an interactive data grid with search, pagination, sorting, CSV download, and charts.

    Args:
        df: The pandas DataFrame to display.
        key: Unique Streamlit widget key prefix.
        default_page_size: Number of rows per page.
        show_controls: Whether to render search and pagination controls.
        show_download: Whether to render quick CSV download button.
        show_charts: Whether to render visualization expander.
    """
    if df is None or df.empty:
        st.info("No data available to display.")
        return

    # 1. Search and Filter Controls
    filtered_df = df
    if show_controls:
        c1, c2 = st.columns([3, 1])
        with c1:
            search_query = st.text_input(
                "🔍 Search table...",
                key=f"{key}_search",
                placeholder="Type to filter across all columns...",
            )
            filtered_df = filter_dataframe(df, search_query)
        with c2:
            page_size = st.selectbox(
                "Rows per page",
                options=[5, 10, 25, 50, 100],
                index=[5, 10, 25, 50, 100].index(default_page_size) if default_page_size in [5, 10, 25, 50, 100] else 1,
                key=f"{key}_pagesize",
            )
    else:
        page_size = default_page_size

    total_rows = len(filtered_df)
    total_pages = max(1, math.ceil(total_rows / page_size))

    # 2. Pagination State
    page_key = f"{key}_current_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    current_page = st.session_state[page_key]
    if current_page > total_pages:
        current_page = total_pages
        st.session_state[page_key] = current_page

    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_rows)

    page_df = filtered_df.iloc[start_idx:end_idx]

    # 3. Data Grid Render
    st.caption(f"Showing **{start_idx + 1}–{end_idx}** of **{total_rows}** row(s) (Filtered from {len(df)} total rows)")
    st.dataframe(
        page_df,
        width="stretch",
        hide_index=True,
    )

    # 4. Pagination & Export Bar
    if show_controls:
        b1, b2, b3, b4 = st.columns([1, 2, 1, 2])

        with b1:
            if st.button("◀ Prev", key=f"{key}_prev", disabled=(current_page <= 1), width="stretch"):
                st.session_state[page_key] = max(1, current_page - 1)
                st.rerun()

        with b2:
            st.markdown(f"<div style='text-align: center; padding-top: 5px;'>Page <b>{current_page}</b> of <b>{total_pages}</b></div>", unsafe_allow_html=True)

        with b3:
            if st.button("Next ▶", key=f"{key}_next", disabled=(current_page >= total_pages), width="stretch"):
                st.session_state[page_key] = min(total_pages, current_page + 1)
                st.rerun()

        with b4:
            if show_download:
                with st.popover("📥 Export Data", width="stretch"):
                    st.caption("Select Export Format:")
                    
                    csv_b = export_to_csv(filtered_df)
                    st.download_button("📥 CSV (.csv)", data=csv_b, file_name=f"export_{key}.csv", mime="text/csv", key=f"{key}_dl_csv", width="stretch")
                    
                    excel_b = export_to_excel(filtered_df)
                    st.download_button("📊 Excel (.xlsx)", data=excel_b, file_name=f"export_{key}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"{key}_dl_xlsx", width="stretch")

                    json_b = export_to_json(filtered_df)
                    st.download_button("📄 JSON (.json)", data=json_b, file_name=f"export_{key}.json", mime="application/json", key=f"{key}_dl_json", width="stretch")

                    pdf_b = export_to_pdf(filtered_df)
                    st.download_button("📑 PDF (.pdf)", data=pdf_b, file_name=f"export_{key}.pdf", mime="application/pdf", key=f"{key}_dl_pdf", width="stretch")

    # 5. Interactive Visualizations & Charts Expander
    if show_charts and not filtered_df.empty:
        chart_analysis = analyze_dataframe_for_charts(filtered_df)
        if chart_analysis["recommended_charts"]:
            with st.expander("📊 Interactive Visualizations & Charts", expanded=False):
                render_auto_visualization(filtered_df, key=f"{key}_chart")
