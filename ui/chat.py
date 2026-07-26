"""
Chat interface components with Safe Execution Layer middleware, SQL Preview Panel, and AI Explainer.

Manages chat message history, renders the conversation, displays confirmation dialogs
for dangerous write/DDL operations, and streams LangChain agent responses.
"""

import re
import streamlit as st
from typing import Optional
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq

from config.security import validate_query_security
from history.query_history import add_query_log
from services.safety import evaluate_query_safety
from services.sql_executor import execute_sql, is_write_operation, classify_sql
from ui.sql_panel import render_sql_panel
from utils.logger import setup_logger

logger = setup_logger(__name__)


def init_chat_history() -> None:
    """Initialize or reset chat history in session state."""
    if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "How can I help you?",
            }
        ]
        if "pending_confirmation" in st.session_state:
            del st.session_state["pending_confirmation"]


def render_chat_messages(llm: Optional[ChatGroq] = None) -> None:
    """Render all messages from the chat history.

    Args:
        llm: Optional ChatGroq model instance for AI SQL Explainer.
    """
    for idx, msg in enumerate(st.session_state["messages"]):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "sql_panel" in msg and msg["sql_panel"]:
                panel = msg["sql_panel"]
                render_sql_panel(
                    sql=panel["sql"],
                    execution_time_ms=panel.get("execution_time_ms"),
                    rows_affected=panel.get("rows_affected"),
                    success=panel.get("success", True),
                    sql_type=panel.get("sql_type", "SELECT"),
                    explanation=panel.get("explanation"),
                    expanded=False,
                    llm=llm,
                    key_prefix=f"history_{idx}",
                )


def extract_sql_from_response(text_content: str) -> list[str]:
    """Extract SQL blocks or inline queries from agent response text.

    Args:
        text_content: Agent response text.

    Returns:
        List of extracted SQL query strings.
    """
    # Look for ```sql ... ``` blocks
    sql_blocks = re.findall(r"```sql\s*(.*?)\s*```", text_content, re.DOTALL | re.IGNORECASE)
    if sql_blocks:
        return [block.strip() for block in sql_blocks]

    # Look for generic ``` ... ``` blocks containing SQL keywords
    code_blocks = re.findall(r"```\s*(.*?)\s*```", text_content, re.DOTALL)
    extracted = []
    for block in code_blocks:
        if any(kw in block.upper() for kw in ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]):
            extracted.append(block.strip())

    return extracted


def render_confirmation_dialog(db: SQLDatabase, llm: Optional[ChatGroq] = None) -> None:
    """Render confirmation dialog UI if a pending operation exists in session state.

    Args:
        db: The connected SQLDatabase instance.
        llm: Optional ChatGroq model instance.
    """
    if "pending_confirmation" not in st.session_state or not st.session_state["pending_confirmation"]:
        return

    pending = st.session_state["pending_confirmation"]
    sql = pending["sql"]
    safety = pending["safety"]

    risk_level = safety["risk_level"]

    st.markdown("---")
    with st.container():
        st.warning(f"🛡️ **Action Required: Confirmation Needed ({risk_level} Risk)**")
        st.markdown(safety["explanation"])

        st.caption("Generated SQL Preview:")
        st.code(sql, language="sql")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Confirm & Execute", key="btn_confirm_exec", type="primary", width="stretch"):
                is_sec_ok, sec_msg = validate_query_security(sql)
                if not is_sec_ok:
                    st.session_state["messages"].append(
                        {
                            "role": "assistant",
                            "content": f"🛡️ **Security Policy Alert**:\n\n{sec_msg}",
                        }
                    )
                    del st.session_state["pending_confirmation"]
                    st.rerun()
                    return

                result = execute_sql(db, sql)
                add_query_log(
                    question=pending.get("user_query", "Write Operation"),
                    sql=sql,
                    execution_time_ms=result.execution_time_ms,
                    rows_affected=result.rows_affected,
                    status="SUCCESS" if result.success else "FAILED",
                )
                if result.success:
                    msg_obj = {
                        "role": "assistant",
                        "content": f"✅ **Executed Successfully!**  \n{result.message}",
                        "sql_panel": {
                            "sql": sql,
                            "execution_time_ms": result.execution_time_ms,
                            "rows_affected": result.rows_affected,
                            "success": True,
                            "sql_type": result.sql_type,
                            "explanation": safety.get("explanation"),
                        },
                    }
                    st.session_state["messages"].append(msg_obj)
                else:
                    st.session_state["messages"].append(
                        {
                            "role": "assistant",
                            "content": f"❌ **Execution Failed:** {result.error}",
                        }
                    )
                del st.session_state["pending_confirmation"]
                st.rerun()

        with col2:
            if st.button("❌ Cancel Action", key="btn_cancel_exec", width="stretch"):
                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": "🚫 **Operation canceled.** No changes were made to the database.",
                    }
                )
                del st.session_state["pending_confirmation"]
                st.rerun()


def handle_user_input(
    agent,
    db: Optional[SQLDatabase] = None,
    llm: Optional[ChatGroq] = None,
) -> None:
    """Handle user chat input, evaluate query safety, and stream response.

    Args:
        agent: LangChain SQL agent instance.
        db: Optional SQLDatabase instance for direct execution on confirmation.
        llm: Optional ChatGroq model instance for AI SQL Explainer.
    """
    # 1. Render pending confirmation dialog if present
    if db:
        render_confirmation_dialog(db, llm=llm)

    # 2. Render chat input box
    user_query = st.chat_input(placeholder="Ask anything from the database...")

    if user_query:
        st.session_state["messages"].append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)

        with st.chat_message("assistant"):
            streamlit_callback = StreamlitCallbackHandler(st.container())
            answer = ""

            try:
                response = agent.invoke(
                    {"input": user_query},
                    {"callbacks": [streamlit_callback]},
                )
                answer = response.get("output", "")
            except Exception as e:
                logger.error("Agent execution error: %s", e)
                error_str = str(e)
                import re

                # 1. Extract raw LLM response from Output Parsing Failure
                if "Could not parse LLM output:" in error_str:
                    clean_err = re.sub(r"\s*For troubleshooting, visit:.*$", "", error_str, flags=re.DOTALL)
                    raw_text = re.sub(r"^.*?Could not parse LLM output:\s*[`'\"]*", "", clean_err, flags=re.DOTALL)
                    raw_text = re.sub(r"[`'\"]*$", "", raw_text, flags=re.DOTALL).strip()
                    if raw_text:
                        answer = raw_text

                if not answer:
                    # 2. Fallback: Extract SQL statement directly if present
                    sql_match = re.search(r"```sql\s*(.*?)\s*```", error_str, re.DOTALL | re.IGNORECASE)
                    if not sql_match:
                        sql_match = re.search(r"(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\s+[^\n]+", error_str, re.IGNORECASE)

                    if sql_match:
                        extracted = sql_match.group(0).strip()
                        answer = f"```sql\n{extracted}\n```"
                    else:
                        answer = (
                            "⚠️ **Agent Response Notice**: The model generated an unparsed response. "
                            "Please try rephrasing your request or selecting `llama-3.3-70b-versatile` in the sidebar."
                        )

            # Extract generated SQL queries from answer
            extracted_sqls = extract_sql_from_response(answer)

            if extracted_sqls and db:
                target_sql = extracted_sqls[0]
                is_sec_ok, sec_msg = validate_query_security(target_sql)

                if not is_sec_ok:
                    st.session_state["messages"].append(
                        {
                            "role": "assistant",
                            "content": f"🛡️ **Security Policy Alert**:\n\n{sec_msg}",
                        }
                    )
                    st.rerun()
                    return

                write_sqls = [sql for sql in extracted_sqls if is_write_operation(sql)]
                if write_sqls:
                    safety = evaluate_query_safety(target_sql)
                    if safety["requires_confirmation"]:
                        st.session_state["pending_confirmation"] = {
                            "sql": target_sql,
                            "user_query": user_query,
                            "safety": safety,
                        }
                        st.session_state["messages"].append(
                            {
                                "role": "assistant",
                                "content": f"🛡️ **Safety Check**: This action requires your confirmation.\n\n"
                                           f"**SQL Statement**: `{target_sql}`\n\n"
                                           f"Please review the confirmation card below to proceed or cancel.",
                            }
                        )
                        st.rerun()
                        return

            # For read queries or non-dangerous queries, attach SQL panel if SQL was detected
            sql_panel_data = None
            if extracted_sqls:
                target_sql = extracted_sqls[0]
                sql_type = classify_sql(target_sql)
                add_query_log(
                    question=user_query,
                    sql=target_sql,
                    execution_time_ms=0.0,
                    rows_affected=0,
                    status="SUCCESS",
                )
                sql_panel_data = {
                    "sql": target_sql,
                    "execution_time_ms": None,
                    "rows_affected": None,
                    "success": True,
                    "sql_type": sql_type,
                    "explanation": f"Generates {sql_type} query against database.",
                }

            msg_obj = {"role": "assistant", "content": answer}
            if sql_panel_data:
                msg_obj["sql_panel"] = sql_panel_data

            st.session_state["messages"].append(msg_obj)
            st.write(answer)
            if sql_panel_data:
                render_sql_panel(
                    sql=sql_panel_data["sql"],
                    execution_time_ms=sql_panel_data["execution_time_ms"],
                    rows_affected=sql_panel_data["rows_affected"],
                    success=sql_panel_data["success"],
                    sql_type=sql_panel_data["sql_type"],
                    explanation=sql_panel_data["explanation"],
                    expanded=False,
                    llm=llm,
                    key_prefix=f"live_{hash(target_sql)}",
                )
