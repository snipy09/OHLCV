"""
Data Validation Engine for OHLCV data
"""

from typing import Dict, Tuple, List, Any
import pandas as pd
import numpy as np
from loguru import logger

from config import NULL_THRESHOLD


class OHLCVValidator:
    """
    Multi-layer validation for OHLCV data:
    - Structural checks
    - Logical checks
    - Temporal checks
    """

    def __init__(self):
        """Initialize validator."""
        self.errors = {}
        self.warnings = {}

    def validate(self, df: pd.DataFrame, ticker: str = "UNKNOWN") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Perform complete validation on OHLCV dataframe.

        Args:
            df: Input dataframe
            ticker: Ticker symbol for logging

        Returns:
            Tuple[pd.DataFrame, Dict]: Clean dataframe and error report
        """
        logger.info(f"Starting validation for {ticker}")

        self.errors = {}
        self.warnings = {}

        df = df.copy()

        # Structural checks
        self._check_structure(df, ticker)

        # Logical checks
        self._check_logic(df, ticker)

        # Temporal checks
        self._check_temporal(df, ticker)

        # Log results
        self._log_validation_results(ticker)

        error_report = {
            'errors': self.errors,
            'warnings': self.warnings,
            'total_errors': len(self.errors),
            'total_warnings': sum(len(v) if isinstance(v, list) else 1 for v in self.warnings.values())
        }

        return df, error_report

    def _check_structure(self, df: pd.DataFrame, ticker: str) -> None:
        """
        Check structural integrity:
        - Required columns present
        - No null values (or within threshold)
        - Correct data types

        Args:
            df: Input dataframe
            ticker: Ticker symbol
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']

        # Check for required columns
        missing_cols = [
            col for col in required_columns if col not in df.columns]
        if missing_cols:
            self.errors['missing_columns'] = missing_cols
            logger.error(f"Missing columns for {ticker}: {missing_cols}")

        # Check for null values
        null_counts = df[required_columns].isnull().sum()
        null_percentages = (null_counts / len(df)) * 100

        null_issues = []
        for col, pct in null_percentages.items():
            if pct > NULL_THRESHOLD * 100:
                null_issues.append(f"{col}: {pct:.2f}% null")

        if null_issues:
            self.errors['high_null_percentage'] = null_issues
            logger.error(f"High null percentage for {ticker}: {null_issues}")

        # Check data types
        dtype_issues = []
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    dtype_issues.append(f"{col}: {df[col].dtype}")

        if dtype_issues:
            self.warnings['dtype_issues'] = dtype_issues
            logger.warning(f"Data type issues for {ticker}: {dtype_issues}")

    def _check_logic(self, df: pd.DataFrame, ticker: str) -> None:
        """
        Check logical relationships:
        - High >= max(Open, Close)
        - Low <= min(Open, Close)
        - Volume >= 0

        Args:
            df: Input dataframe
            ticker: Ticker symbol
        """
        logic_errors = []

        # High >= max(Open, Close)
        high_violations = df[
            df['high'] < np.maximum(df['open'], df['close'])
        ]
        if len(high_violations) > 0:
            logic_errors.append(
                f"High < max(Open, Close): {len(high_violations)} rows")
            logger.warning(
                f"High violations for {ticker}: {len(high_violations)} rows")

        # Low <= min(Open, Close)
        low_violations = df[
            df['low'] > np.minimum(df['open'], df['close'])
        ]
        if len(low_violations) > 0:
            logic_errors.append(
                f"Low > min(Open, Close): {len(low_violations)} rows")
            logger.warning(
                f"Low violations for {ticker}: {len(low_violations)} rows")

        # Volume >= 0
        negative_volume = df[df['volume'] < 0]
        if len(negative_volume) > 0:
            logic_errors.append(
                f"Negative volume: {len(negative_volume)} rows")
            logger.warning(
                f"Negative volume for {ticker}: {len(negative_volume)} rows")

        # OHLC prices should be positive
        negative_prices = df[
            (df['open'] < 0) | (df['high'] < 0) |
            (df['low'] < 0) | (df['close'] < 0)
        ]
        if len(negative_prices) > 0:
            logic_errors.append(
                f"Negative prices: {len(negative_prices)} rows")
            logger.warning(
                f"Negative prices for {ticker}: {len(negative_prices)} rows")

        if logic_errors:
            self.errors['logic_violations'] = logic_errors

    def _check_temporal(self, df: pd.DataFrame, ticker: str) -> None:
        """
        Check temporal integrity:
        - No missing timestamps
        - No duplicate timestamps

        Args:
            df: Input dataframe
            ticker: Ticker symbol
        """
        temporal_issues = []

        # Check for duplicate timestamps
        duplicates = df.index.duplicated().sum()
        if duplicates > 0:
            temporal_issues.append(f"Duplicate timestamps: {duplicates}")
            logger.warning(f"Duplicate timestamps for {ticker}: {duplicates}")

        # Check for missing dates in sequence
        # (assuming daily data, allowing weekends)
        date_diff = df.index.to_series().diff()
        expected_diff = pd.Timedelta(days=1)

        # Find gaps larger than expected (allowing weekends)
        large_gaps = date_diff[date_diff > pd.Timedelta(days=3)].index
        gap_count = len(large_gaps)

        if gap_count > 0:
            temporal_issues.append(
                f"Missing dates (gaps > 3 days): {gap_count}")
            logger.info(f"Date gaps for {ticker}: {gap_count} gaps detected")

        if temporal_issues:
            self.warnings['temporal_issues'] = temporal_issues

    def _log_validation_results(self, ticker: str) -> None:
        """
        Log validation results summary.

        Args:
            ticker: Ticker symbol
        """
        error_count = len(self.errors)
        warning_count = sum(len(v) if isinstance(v, list)
                            else 1 for v in self.warnings.values())

        if error_count == 0 and warning_count == 0:
            logger.info(
                f"Validation passed for {ticker}: No errors or warnings")
        else:
            logger.warning(
                f"Validation completed for {ticker}: "
                f"{error_count} errors, {warning_count} warnings"
            )
