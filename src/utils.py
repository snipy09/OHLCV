"""
Utility functions for OHLCV Data Validation & Monitoring System
"""

from typing import Dict, List, Any
from datetime import datetime
import pandas as pd
from loguru import logger


def setup_logger(log_file: str = None) -> None:
    """
    Setup loguru logger with file and console output.

    Args:
        log_file: Path to log file (optional)
    """
    from config import LOGS_DIR, LOG_FORMAT, LOG_LEVEL

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        lambda msg: print(msg, end=""),
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        colorize=True
    )

    # Add file handler
    if log_file is None:
        log_file = LOGS_DIR / \
            f"ohlcv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger.add(
        str(log_file),
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        rotation="500 MB",
        retention="7 days"
    )


def validate_ticker(ticker: str) -> bool:
    """
    Basic validation of ticker symbol.

    Args:
        ticker: Ticker symbol

    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(ticker, str):
        return False
    if len(ticker) < 1 or len(ticker) > 5:
        return False
    if not ticker.isupper():
        return False
    return True


def standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize OHLCV dataframe columns and types.

    Args:
        df: Input dataframe

    Returns:
        pd.DataFrame: Standardized dataframe
    """
    df = df.copy()

    # Handle MultiIndex columns (from yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Handle MultiIndex rows (reset to datetime index)
    if isinstance(df.index, pd.MultiIndex):
        df = df.reset_index(level=0, drop=True)

    # Rename columns to lowercase
    df.columns = df.columns.str.lower()

    # Ensure proper dtypes
    if 'open' in df.columns:
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
    if 'high' in df.columns:
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
    if 'low' in df.columns:
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
    if 'close' in df.columns:
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
    if 'volume' in df.columns:
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    if 'adj close' in df.columns:
        df['adj close'] = pd.to_numeric(df['adj close'], errors='coerce')

    # Ensure index is datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    df.index.name = 'date'

    return df


def calculate_data_quality_score(
    df: pd.DataFrame,
    validation_errors: Dict[str, Any]
) -> float:
    """
    Calculate data quality score (0-100).

    Args:
        df: Dataframe to score
        validation_errors: Dictionary of validation errors

    Returns:
        float: Quality score
    """
    score = 100.0

    # Check for null values
    null_percentage = df.isnull().sum().sum() / (len(df) * len(df.columns))
    score -= null_percentage * 50

    # Check for errors
    if validation_errors:
        error_count = sum(len(v) if isinstance(v, list) else 1
                          for v in validation_errors.values())
        score -= min(error_count * 2, 40)

    # Check for outliers
    if 'is_outlier' in df.columns:
        outlier_percentage = df['is_outlier'].sum() / len(df)
        score -= outlier_percentage * 20

    return max(0.0, min(100.0, score))


def get_quality_rating(score: float) -> str:
    """
    Get quality rating based on score.

    Args:
        score: Quality score

    Returns:
        str: Rating string
    """
    from config import QUALITY_SCORE_EXCELLENT, QUALITY_SCORE_GOOD, QUALITY_SCORE_WARNING

    if score >= QUALITY_SCORE_EXCELLENT:
        return "EXCELLENT"
    elif score >= QUALITY_SCORE_GOOD:
        return "GOOD"
    elif score >= QUALITY_SCORE_WARNING:
        return "WARNING"
    else:
        return "CRITICAL"


def format_error_report(validation_errors: Dict[str, Any]) -> str:
    """
    Format error report as readable string.

    Args:
        validation_errors: Dictionary of validation errors

    Returns:
        str: Formatted error report
    """
    if not validation_errors:
        return "No errors detected"

    report = "VALIDATION ERROR REPORT\n"
    report += "=" * 50 + "\n"

    for error_type, errors in validation_errors.items():
        if errors:
            report += f"\n{error_type.upper()}:\n"
            if isinstance(errors, list):
                for err in errors[:5]:  # Show first 5 errors
                    report += f"  - {err}\n"
                if len(errors) > 5:
                    report += f"  ... and {len(errors) - 5} more\n"
            else:
                report += f"  {errors}\n"

    return report


def truncate_dataframe(df: pd.DataFrame, max_rows: int = 100) -> pd.DataFrame:
    """
    Truncate dataframe for display purposes.

    Args:
        df: Input dataframe
        max_rows: Maximum rows to keep

    Returns:
        pd.DataFrame: Truncated dataframe
    """
    if len(df) > max_rows:
        return pd.concat([df.head(max_rows // 2), df.tail(max_rows // 2)])
    return df
