"""
Database Analytics & AI Insights Service.

Provides database metrics, statistical summaries, missing value detection,
duplicate row audits, IQR outlier detection, and natural language analytics for tables and datasets.
"""

from typing import Any, Optional
import pandas as pd
import numpy as np
from sqlalchemy import text
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from database.inspector import get_table_names, get_columns, get_row_count
from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_database_overview(db: SQLDatabase) -> dict[str, Any]:
    """Get high-level database size and table stats."""
    tables = get_table_names(db)
    if not tables:
        return {
            "total_tables": 0,
            "total_rows": 0,
            "largest_table": None,
            "smallest_table": None,
            "table_stats": [],
        }

    table_stats = []
    total_rows = 0

    for table in tables:
        count = get_row_count(db, table)
        total_rows += count
        table_stats.append({"table_name": table, "row_count": count})

    table_stats.sort(key=lambda x: x["row_count"], reverse=True)
    largest_table = table_stats[0] if table_stats else None
    smallest_table = table_stats[-1] if table_stats else None

    return {
        "total_tables": len(tables),
        "total_rows": total_rows,
        "largest_table": largest_table,
        "smallest_table": smallest_table,
        "table_stats": table_stats,
    }


def check_missing_values(db: SQLDatabase, table_name: str) -> dict[str, int]:
    """Check count of NULL values for each column in a table."""
    columns = get_columns(db, table_name)
    if not columns:
        return {}

    null_counts: dict[str, int] = {}
    try:
        with db._engine.connect() as conn:
            for col in columns:
                col_name = col["name"]
                query = text(f"SELECT COUNT(*) FROM `{table_name}` WHERE `{col_name}` IS NULL")
                result = conn.execute(query).scalar() or 0
                null_counts[col_name] = result
    except Exception as e:
        logger.error("Error checking missing values for %s: %s", table_name, e)

    return null_counts


def check_duplicate_records(db: SQLDatabase, table_name: str) -> int:
    """Count duplicate rows in a table."""
    columns = get_columns(db, table_name)
    if not columns:
        return 0

    col_list = ", ".join(f"`{c['name']}`" for c in columns)
    try:
        with db._engine.connect() as conn:
            query = text(
                f"SELECT COUNT(*) FROM ("
                f"SELECT {col_list}, COUNT(*) FROM `{table_name}` "
                f"GROUP BY {col_list} HAVING COUNT(*) > 1"
                f") as duplicates"
            )
            result = conn.execute(query).scalar() or 0
            return result
    except Exception as e:
        logger.error("Error checking duplicate records for %s: %s", table_name, e)
        return 0


def get_numeric_summary(db: SQLDatabase, table_name: str) -> dict[str, dict[str, Any]]:
    """Compute MIN, MAX, AVG for numeric columns in a table."""
    columns = get_columns(db, table_name)
    numeric_types = ["INT", "INTEGER", "FLOAT", "DOUBLE", "DECIMAL", "NUMERIC", "REAL"]

    numeric_cols = [
        c["name"] for c in columns
        if any(nt in c["type"].upper() for nt in numeric_types)
    ]

    if not numeric_cols:
        return {}

    stats: dict[str, dict[str, Any]] = {}
    try:
        with db._engine.connect() as conn:
            for col in numeric_cols:
                query = text(
                    f"SELECT MIN(`{col}`), MAX(`{col}`), AVG(`{col}`) FROM `{table_name}`"
                )
                res = conn.execute(query).fetchone()
                if res:
                    stats[col] = {
                        "min": res[0],
                        "max": res[1],
                        "avg": round(res[2], 2) if res[2] is not None else None,
                    }
    except Exception as e:
        logger.error("Error computing numeric stats for %s: %s", table_name, e)

    return stats


def analyze_dataframe_insights(df: pd.DataFrame, llm: Optional[ChatGroq] = None) -> dict[str, Any]:
    """Perform statistical analysis (Min, Max, Avg, Median, IQR Outliers) and AI insights on a DataFrame.

    Args:
        df: Input pandas DataFrame from query output.
        llm: Optional ChatGroq LLM instance for pattern analysis.

    Returns:
        Dict containing numeric_stats, outliers, patterns, and recommendations.
    """
    if df is None or df.empty:
        return {"numeric_stats": {}, "outliers": {}, "ai_summary": "No data available."}

    numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
    numeric_stats: dict[str, dict[str, Any]] = {}
    outliers: dict[str, list[Any]] = {}

    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        col_outliers = series[(series < lower_bound) | (series > upper_bound)].tolist()

        numeric_stats[col] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": float(round(series.mean(), 2)),
            "median": float(round(series.median(), 2)),
            "std": float(round(series.std(), 2)) if len(series) > 1 else 0.0,
            "q1": float(q1),
            "q3": float(q3),
            "outlier_count": len(col_outliers),
        }
        if col_outliers:
            outliers[col] = col_outliers

    # AI Pattern Summary
    ai_summary = ""
    if llm:
        prompt = (
            f"Dataset Shape: {df.shape}\n"
            f"Columns: {list(df.columns)}\n"
            f"Numeric Column Statistics: {numeric_stats}\n"
            f"Detected Outliers: {outliers}\n\n"
            f"Sample Data:\n{df.head(5).to_dict(orient='records')}"
        )
        system_msg = (
            "You are a Senior Data Scientist. "
            "Analyze the dataset statistical summary and provide concise, actionable insights covering: "
            "1) 🔍 Key Data Patterns & Distribution, 2) 🚨 Outliers & Potential Anomalies, 3) 💡 Strategic Recommendations."
        )

        try:
            messages = [SystemMessage(content=system_msg), HumanMessage(content=prompt)]
            ai_summary = llm.invoke(messages).content
        except Exception as e:
            logger.error("Failed to generate AI DataFrame insights: %s", e)
            ai_summary = "⚠️ Could not generate LLM pattern summary."
    else:
        # Rule fallback
        summary_lines = ["### 📊 Statistical Highlights"]
        for col, s in numeric_stats.items():
            summary_lines.append(f"- **`{col}`**: Min={s['min']}, Max={s['max']}, Mean={s['mean']}, Median={s['median']}")
        if outliers:
            summary_lines.append("\n### 🚨 Detected Outliers")
            for col, outs in outliers.items():
                summary_lines.append(f"- **`{col}`**: {len(outs)} outlier value(s) detected: `{outs[:5]}`")
        ai_summary = "\n".join(summary_lines)

    return {
        "numeric_stats": numeric_stats,
        "outliers": outliers,
        "ai_summary": ai_summary,
    }


def generate_full_health_report(db: SQLDatabase) -> dict[str, Any]:
    """Generate a comprehensive health audit report for all database tables."""
    overview = get_database_overview(db)
    tables = get_table_names(db)

    report = {
        "overview": overview,
        "table_reports": {},
    }

    for table in tables:
        missing = check_missing_values(db, table)
        duplicates = check_duplicate_records(db, table)
        numeric_stats = get_numeric_summary(db, table)

        report["table_reports"][table] = {
            "row_count": get_row_count(db, table),
            "missing_values": missing,
            "total_nulls": sum(missing.values()),
            "duplicates": duplicates,
            "numeric_stats": numeric_stats,
        }

    return report


def generate_ai_analytics_summary(db: SQLDatabase, llm: Optional[ChatGroq] = None) -> str:
    """Generate natural language insights summarizing database health and statistics."""
    report = generate_full_health_report(db)
    overview = report["overview"]

    if not llm:
        lines = [
            f"### 📊 Database Health Summary",
            f"- **Total Tables**: {overview['total_tables']}",
            f"- **Total Rows**: {overview['total_rows']:,}",
        ]
        if overview['largest_table']:
            lines.append(f"- **Largest Table**: `{overview['largest_table']['table_name']}` ({overview['largest_table']['row_count']:,} rows)")

        for table, tr in report["table_reports"].items():
            lines.append(f"\n#### Table `{table}`:")
            lines.append(f"- Rows: **{tr['row_count']}**")
            lines.append(f"- Missing Values (NULLs): **{tr['total_nulls']}**")
            lines.append(f"- Duplicate Records: **{tr['duplicates']}**")
            if tr["numeric_stats"]:
                lines.append("- Numeric Column Stats:")
                for col, s in tr["numeric_stats"].items():
                    lines.append(f"  - `{col}`: Min={s['min']}, Max={s['max']}, Avg={s['avg']}")

        return "\n".join(lines)

    prompt = f"Database Audit Metrics Report:\n{report}"
    system_msg = (
        "You are an expert Data Analyst and Database Administrator. "
        "Analyze the provided database metrics report and write a clear, professional executive summary. "
        "Highlight total records, table distributions, data quality concerns (missing values or duplicates), "
        "and key numeric statistical insights."
    )

    try:
        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=prompt),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        logger.error("Failed to generate AI analytics summary: %s", e)
        return f"⚠️ **Could not generate LLM analytics summary** ({e})."
