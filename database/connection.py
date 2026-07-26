"""
Database connection management with connection pooling and caching.

Handles SQLite and MySQL database connections using SQLAlchemy
engines wrapped in LangChain's SQLDatabase utility with optimized connection pooling.
"""

import streamlit as st
from pathlib import Path
from urllib.parse import quote_plus
from typing import Optional

from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

from config.settings import LOCALDB, MYSQLDB


@st.cache_resource(ttl=7200)
def configure_db(
    db_uri: str,
    mysql_host: Optional[str] = None,
    mysql_user: Optional[str] = None,
    mysql_password: Optional[str] = None,
    mysql_db: Optional[str] = None,
) -> SQLDatabase:
    """Configure and return a cached SQLDatabase connection.

    Supports SQLite (local file) and MySQL (remote server) databases with
    connection pooling (`pool_size`, `max_overflow`, `pool_recycle`, `pool_pre_ping`).
    Connection is cached for 2 hours via Streamlit's cache_resource.

    Args:
        db_uri: Database type identifier (LOCALDB or MYSQLDB).
        mysql_host: MySQL server hostname.
        mysql_user: MySQL username.
        mysql_password: MySQL password.
        mysql_db: MySQL database name.

    Returns:
        A configured SQLDatabase instance.
    """
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent.parent / "student.db").absolute()
        engine = create_engine(
            f"sqlite:///{dbfilepath}",
            connect_args={"check_same_thread": False, "timeout": 15},
            pool_pre_ping=True,
        )
        return SQLDatabase(engine)

    elif db_uri == MYSQLDB:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please Provide all MySQL connection Details")
            st.stop()

        encoded_password = quote_plus(mysql_password)
        connection_str = (
            f"mysql+mysqlconnector://"
            f"{mysql_user}:{encoded_password}"
            f"@{mysql_host}/{mysql_db}"
        )

        try:
            engine = create_engine(
                connection_str,
                pool_size=10,
                max_overflow=20,
                pool_recycle=1800,
                pool_pre_ping=True,
            )
            db = SQLDatabase(engine)
            st.success("Successfully Connected To MYSQL Database !")
            return db
        except Exception as e:
            st.error(f"Failed to connect to Mysql: {e}")
            st.stop()
