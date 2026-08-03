"""
Data Cleaning module for OHLCV data
"""

from typing import Dict, Tuple
import pandas as pd
import numpy as np
from loguru import logger


class OHLCVCleaner:
    """
    Clean and preprocess OHLCV data.
    """

    def __init__(self):
        """Initialize cleaner."""
        self.cleaning_log = []

    def clean(self, df: pd.DataFrame, ticker: str = "UNKNOWN") -> Tuple[pd.DataFrame, Dict]:
        """
        Perform complete cleaning on OHLCV dataframe.

        Args:
            df: Input dataframe
            ticker: Ticker symbol for logging

        Returns:
            Tuple[pd.DataFrame, Dict]: Cleaned dataframe and cleaning report
        """
        logger.info(f"Starting data cleaning for {ticker}")

        self.cleaning_log = []
        df = df.copy()
        initial_rows = len(df)

        # Remove duplicates
        df = self._remove_duplicates(df, ticker)

        # Handle missing values
        df = self._handle_missing_values(df, ticker)

        # Drop severely corrupted rows
        df = self._drop_corrupted_rows(df, ticker)

        # Ensure data types
        df = self._ensure_dtypes(df, ticker)

        final_rows = len(df)
        rows_removed = initial_rows - final_rows

        cleaning_report = {
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'rows_removed': rows_removed,
            'cleaning_steps': self.cleaning_log
        }

        logger.info(
            f"Cleaning completed for {ticker}: "
            f"Removed {rows_removed} rows ({rows_removed/initial_rows*100:.2f}%)"
        )

        return df, cleaning_report

    def _remove_duplicates(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Remove duplicate timestamps (index).

        Args:
            df: Input dataframe
            ticker: Ticker symbol

        Returns:
            pd.DataFrame: Dataframe with duplicates removed
        """
        initial_len = len(df)

        # Keep first occurrence
        df = df[~df.index.duplicated(keep='first')]

        removed = initial_len - len(df)
        if removed > 0:
            self.cleaning_log.append(f"Removed {removed} duplicate timestamps")
            logger.info(f"Removed {removed} duplicates for {ticker}")

        return df

    def _handle_missing_values(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Handle missing values using forward fill with limit.

        Args:
            df: Input dataframe
            ticker: Ticker symbol

        Returns:
            pd.DataFrame: Dataframe with missing values handled
        """
        initial_nulls = df.isnull().sum().sum()

        # Forward fill with limit of 2 days
        df = df.ffill(limit=2)

        # Backward fill remaining
        df = df.bfill()
        return df

    def _drop_corrupted_rows(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Drop severely corrupted rows.
        Criteria:
        - Zero volume (except for some cases)
        - Negative values
        - OHLC illogical

        Args:
            df: Input dataframe
            ticker: Ticker symbol

        Returns:
            pd.DataFrame: Dataframe with corrupted rows removed
        """
        initial_len = len(df)

        # Remove zero volume rows (but keep some tolerance for gaps)
        zero_volume_count = (df['volume'] == 0).sum()
        if zero_volume_count > len(df) * 0.5:
            # Many zero volumes, likely bad data
            df = df[df['volume'] > 0]

        # Remove negative prices
        df = df[
            (df['open'] > 0) & (df['high'] > 0) &
            (df['low'] > 0) & (df['close'] > 0)
        ]

        # Remove illogical OHLC
        df = df[
            (df['high'] >= df['open']) &
            (df['high'] >= df['close']) &
            (df['low'] <= df['open']) &
            (df['low'] <= df['close'])
        ]

        removed = initial_len - len(df)
        if removed > 0:
            self.cleaning_log.append(f"Dropped {removed} corrupted rows")
            logger.info(f"Dropped {removed} corrupted rows for {ticker}")

        return df

    def _ensure_dtypes(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Ensure proper data types.

        Args:
            df: Input dataframe
            ticker: Ticker symbol

        Returns:
            pd.DataFrame: Dataframe with proper dtypes
        """
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Volume should be integer
        if 'volume' in df.columns:
            df['volume'] = df['volume'].astype('int64')

        self.cleaning_log.append("Ensured proper data types")

        return df
