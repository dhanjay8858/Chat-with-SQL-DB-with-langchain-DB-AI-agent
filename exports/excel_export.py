"""
Excel Export Utility.

Converts DataFrames to formatted Excel (.xlsx) bytes using openpyxl.
"""

import io
import pandas as pd
from utils.logger import setup_logger

logger = setup_logger(__name__)


def export_to_excel(df: pd.DataFrame, sheet_name: str = "Query Results") -> bytes:
    """Convert DataFrame to formatted Excel (.xlsx) bytes.

    Args:
        df: Input pandas DataFrame.
        sheet_name: Name for the Excel worksheet.

    Returns:
        Excel workbook bytes.
    """
    if df is None or df.empty:
        return b""

    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        return output.getvalue()
    except Exception as e:
        logger.error("Excel export failed: %s", e)
        return b""
