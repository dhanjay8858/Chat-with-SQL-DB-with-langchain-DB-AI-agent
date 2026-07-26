"""
Custom UI/UX CSS Design System.

Applies modern, premium styling to the Streamlit application including Google Fonts,
dark glassmorphism containers, custom metric cards, tab navigation styling,
and micro-animations inspired by ChatGPT, DBeaver, and MySQL Workbench.
"""

import streamlit as st

CUSTOM_CSS = """
<style>
/* ─── Google Fonts ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre, [class*="stCode"] {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ─── Main Content Styling ─── */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    color: #f8fafc;
}

/* ─── Header Title Styling ─── */
h1 {
    font-weight: 700 !important;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

/* ─── Sidebar Customization ─── */
[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.85) !important;
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

/* ─── Tab Bar Styling ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(30, 41, 59, 0.5);
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    border-radius: 8px;
    padding: 0 20px;
    color: #94a3b8;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.2s ease-in-out;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #f8fafc;
    background-color: rgba(255, 255, 255, 0.05);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* ─── Metric Cards ─── */
[data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: rgba(99, 102, 241, 0.4) !important;
}

[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

[data-testid="stMetricValue"] {
    color: #38bdf8 !important;
    font-weight: 700 !important;
    font-size: 22px !important;
}

/* ─── Buttons Styling ─── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    border: none !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
}

/* ─── Expander Containers ─── */
.streamlit-expanderHeader {
    background-color: rgba(30, 41, 59, 0.4) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

.streamlit-expanderContent {
    background-color: rgba(15, 23, 42, 0.3) !important;
    border-radius: 0 0 8px 8px !important;
}
</style>
"""


def apply_custom_css() -> None:
    """Inject custom design system CSS into the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
