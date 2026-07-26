"""
CSV Export Utility.

Converts DataFrames to UTF-8 encoded CSV bytes for user download.
"""

import pandas as pd
from utils.logger import setup_logger

logger = setup_logger(__name__)


def export_to_csv(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes.

    Args:
        df: Input pandas DataFrame.

    Returns:
        UTF-8 encoded CSV bytes.
    """
    if df is None or df.empty:
        return b""

    try:
        return df.to_csv(index=False).encode("utf-8")
    except Exception as e:
        logger.error("CSV export failed: %s", e)
        return b""
