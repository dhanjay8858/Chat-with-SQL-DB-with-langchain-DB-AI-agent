"""
AI SQL Explainer Service.

Uses Groq LLM and SQL AST parsing to produce beginner-friendly explanations
of SQL queries including purpose, clause breakdown, performance complexity,
and index optimization recommendations.
"""

import re
from typing import Any, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from utils.logger import setup_logger

logger = setup_logger(__name__)

EXPLAINER_SYSTEM_PROMPT = """You are a Senior Database Engineer and Educator.
Your task is to explain a SQL query in simple, clear, beginner-friendly terms.

Break down your response into the following 4 sections:

1. 🎯 **Purpose**: A clear 1-2 sentence explanation of what this query does in plain English.
2. 🔍 **Clause-by-Clause Breakdown**:
   - Explain each keyword/clause (e.g. SELECT, FROM, WHERE, GROUP BY, ORDER BY, JOIN) and what it achieves.
3. ⚡ **Performance & Complexity**:
   - Estimated Time/Space Complexity (e.g., O(N) full table scan, O(log N) indexed search).
   - Potential performance bottlenecks.
4. 💡 **Suggested Optimizations & Indexes**:
   - Specific indexes that could speed up this query.
   - Any recommended query rewrites or best practices.

Keep your tone helpful, professional, and accessible to non-technical users."""


def quick_rule_based_explain(sql: str) -> dict[str, Any]:
    """Provide a fast, offline rule-based breakdown of a SQL query.

    Args:
        sql: The SQL statement.

    Returns:
        Dict with basic purpose, clauses found, and estimated complexity.
    """
    cleaned = sql.strip()
    upper_sql = cleaned.upper()

    clauses = []
    if "SELECT" in upper_sql:
        clauses.append("SELECT (retrieves specific columns/values)")
    if "FROM" in upper_sql:
        clauses.append("FROM (identifies source table)")
    if "WHERE" in upper_sql:
        clauses.append("WHERE (filters rows based on conditions)")
    if "GROUP BY" in upper_sql:
        clauses.append("GROUP BY (aggregates matching rows)")
    if "HAVING" in upper_sql:
        clauses.append("HAVING (filters aggregated groups)")
    if "ORDER BY" in upper_sql:
        clauses.append("ORDER BY (sorts the final results)")
    if "JOIN" in upper_sql:
        clauses.append("JOIN (combines data across multiple tables)")
    if "LIMIT" in upper_sql:
        clauses.append("LIMIT (restricts maximum row count returned)")

    complexity = "O(N) - Full Table Scan likely" if "WHERE" not in upper_sql and "SELECT" in upper_sql else "O(N) - Filtered Scan"
    if "WHERE" in upper_sql and ("ID" in upper_sql or "PK" in upper_sql):
        complexity = "O(log N) - Primary Key Lookup expected"

    return {
        "purpose": f"Executes a database query operating on target tables.",
        "clauses": clauses,
        "complexity": complexity,
        "has_where": "WHERE" in upper_sql,
    }


def explain_sql_query(
    sql: str,
    llm: Optional[ChatGroq] = None,
    table_context: str = "",
) -> str:
    """Generate a comprehensive, beginner-friendly AI explanation of a SQL query.

    Args:
        sql: The SQL query statement.
        llm: Optional ChatGroq LLM instance. If None, uses fallback rules.
        table_context: Optional string describing table schemas.

    Returns:
        Markdown-formatted explanation string.
    """
    if not llm:
        rule_data = quick_rule_based_explain(sql)
        clauses_str = "\n".join(f"- {c}" for c in rule_data["clauses"])
        return f"""### 🎯 Purpose
{rule_data['purpose']}

### 🔍 Clause Breakdown
{clauses_str}

### ⚡ Performance & Complexity
- **Estimated Complexity**: `{rule_data['complexity']}`

### 💡 Suggested Optimizations
- Ensure filtering columns have indexes created for faster retrieval.
"""

    prompt = f"Target SQL Query:\n```sql\n{sql}\n```"
    if table_context:
        prompt += f"\n\nTable Schema Context:\n{table_context}"

    try:
        messages = [
            SystemMessage(content=EXPLAINER_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        response = llm.invoke(messages)
        logger.info("Generated AI SQL explanation successfully.")
        return response.content
    except Exception as e:
        logger.error("Failed to generate AI SQL explanation: %s", e)
        rule_data = quick_rule_based_explain(sql)
        return f"⚠️ **Could not generate full LLM explanation** ({e}).\n\n**Quick Summary**: {rule_data['purpose']}"
