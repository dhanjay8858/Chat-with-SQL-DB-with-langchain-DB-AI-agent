"""
JSON Export Utility.

Converts DataFrames to formatted JSON bytes.
"""

import pandas as pd
from utils.logger import setup_logger

logger = setup_logger(__name__)


def export_to_json(df: pd.DataFrame, indent: int = 2) -> bytes:
    """Convert DataFrame to JSON bytes.

    Args:
        df: Input pandas DataFrame.
        indent: JSON indentation spaces.

    Returns:
        UTF-8 encoded JSON bytes.
    """
    if df is None or df.empty:
        return b""

    try:
        json_str = df.to_json(orient="records", indent=indent)
        return json_str.encode("utf-8")
    except Exception as e:
        logger.error("JSON export failed: %s", e)
        return b""
