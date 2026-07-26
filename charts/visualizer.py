"""
Plotly Data Visualization Engine.

Automatically detects numeric and categorical structures in DataFrames
and generates interactive Plotly charts: Bar Charts, Pie Charts, Line Charts,
Scatter Plots, Histograms, Box Plots, and Heatmaps.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Any, Optional, List

import plotly.express as px
import plotly.graph_objects as go

from utils.logger import setup_logger

logger = setup_logger(__name__)

# Curated modern color palette
COLOR_PALETTE = px.colors.qualitative.Plotly


def analyze_dataframe_for_charts(df: pd.DataFrame) -> dict[str, Any]:
    """Analyze DataFrame columns to classify data types and recommend charts.

    Args:
        df: Input pandas DataFrame.

    Returns:
        Dict with numeric_cols, categorical_cols, datetime_cols, and recommended_charts.
    """
    if df is None or df.empty:
        return {"numeric_cols": [], "categorical_cols": [], "datetime_cols": [], "recommended_charts": []}

    numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
    categorical_cols = list(df.select_dtypes(include=["object", "category", "string"]).columns)
    datetime_cols = list(df.select_dtypes(include=["datetime", "datetime64"]).columns)

    recommended = []

    if numeric_cols:
        recommended.append("Histogram")
        recommended.append("Box Plot")

    if categorical_cols and numeric_cols:
        recommended.append("Bar Chart")
        recommended.append("Pie Chart")

    if len(numeric_cols) >= 2:
        recommended.append("Scatter Plot")
        recommended.append("Heatmap")

    if datetime_cols and numeric_cols:
        recommended.append("Line Chart")
    elif len(numeric_cols) >= 1 and categorical_cols:
        recommended.append("Line Chart")

    return {
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "datetime_cols": datetime_cols,
        "recommended_charts": recommended,
    }


def generate_chart_figure(
    df: pd.DataFrame,
    chart_type: str,
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
    color_col: Optional[str] = None,
) -> Optional[go.Figure]:
    """Generate a Plotly Figure based on chart configuration.

    Args:
        df: Input DataFrame.
        chart_type: One of 'Bar Chart', 'Pie Chart', 'Line Chart', 'Scatter Plot', 'Histogram', 'Box Plot', 'Heatmap'.
        x_col: X-axis column name.
        y_col: Y-axis column name.
        color_col: Color grouping column name.

    Returns:
        Plotly go.Figure instance or None if generation failed.
    """
    try:
        template = "plotly_dark"

        if chart_type == "Bar Chart":
            fig = px.bar(
                df,
                x=x_col,
                y=y_col,
                color=color_col if color_col else x_col,
                template=template,
                color_discrete_sequence=COLOR_PALETTE,
                title=f"Bar Chart: {y_col} by {x_col}" if y_col else f"Bar Chart of {x_col}",
            )
        elif chart_type == "Pie Chart":
            fig = px.pie(
                df,
                names=x_col,
                values=y_col if y_col else None,
                template=template,
                color_discrete_sequence=COLOR_PALETTE,
                title=f"Pie Chart: {x_col} Distribution",
            )
        elif chart_type == "Line Chart":
            fig = px.line(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                markers=True,
                template=template,
                color_discrete_sequence=COLOR_PALETTE,
                title=f"Line Chart: {y_col} vs {x_col}",
            )
        elif chart_type == "Scatter Plot":
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                size=y_col if y_col in df.select_dtypes(include=[np.number]).columns else None,
                template=template,
                color_discrete_sequence=COLOR_PALETTE,
                title=f"Scatter Plot: {y_col} vs {x_col}",
            )
        elif chart_type == "Histogram":
            fig = px.histogram(
                df,
                x=x_col,
                color=color_col,
                marginal="rug",
                template=template,
                color_discrete_sequence=COLOR_PALETTE,
                title=f"Histogram of {x_col}",
            )
        elif chart_type == "Box Plot":
            fig = px.box(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                points="all",
                template=template,
                color_discrete_sequence=COLOR_PALETTE,
                title=f"Box Plot: {y_col or x_col}",
            )
        elif chart_type == "Heatmap":
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.shape[1] >= 2:
                corr = numeric_df.corr()
                fig = px.imshow(
                    corr,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale="Viridis",
                    template=template,
                    title="Correlation Heatmap",
                )
            else:
                return None
        else:
            return None

        fig.update_layout(
            font_family="Inter, sans-serif",
            title_font_size=16,
            legend_title_text=color_col if color_col else "",
            margin=dict(l=20, r=20, t=50, b=20),
        )
        return fig

    except Exception as e:
        logger.error("Failed to generate chart %s: %s", chart_type, e)
        return None


def render_auto_visualization(df: pd.DataFrame, key: str = "auto_chart") -> None:
    """Render interactive chart builder controls and Plotly figure.

    Args:
        df: Input pandas DataFrame.
        key: Unique widget key prefix.
    """
    analysis = analyze_dataframe_for_charts(df)
    recommended = analysis["recommended_charts"]

    if not recommended:
        st.info("No numeric or visualizable columns detected for charting.")
        return

    all_cols = list(df.columns)
    numeric_cols = analysis["numeric_cols"]
    categorical_cols = analysis["categorical_cols"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        selected_type = st.selectbox(
            "Chart Type",
            options=["Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot", "Histogram", "Box Plot", "Heatmap"],
            index=0,
            key=f"{key}_chart_type",
        )

    with col2:
        default_x = categorical_cols[0] if categorical_cols else (all_cols[0] if all_cols else None)
        x_col = st.selectbox("X-Axis / Category", options=all_cols, index=all_cols.index(default_x) if default_x in all_cols else 0, key=f"{key}_x_col")

    with col3:
        default_y = numeric_cols[0] if numeric_cols else (all_cols[1] if len(all_cols) > 1 else None)
        y_options = [None] + all_cols
        y_col = st.selectbox("Y-Axis / Value", options=y_options, index=y_options.index(default_y) if default_y in y_options else 0, key=f"{key}_y_col")

    with col4:
        color_options = [None] + all_cols
        color_col = st.selectbox("Color Grouping", options=color_options, index=0, key=f"{key}_color_col")

    fig = generate_chart_figure(df, selected_type, x_col=x_col, y_col=y_col, color_col=color_col)

    if fig:
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning(f"Could not render {selected_type} with selected columns.")
