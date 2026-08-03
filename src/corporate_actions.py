"""
Corporate Actions module for handling stock splits and dividends
"""

from typing import Dict, Tuple
import pandas as pd
from loguru import logger


class CorporateActionsHandler:
    """
    Handle corporate actions (splits and dividends) for OHLCV data.
    """

    def __init__(self):
        """Initialize corporate actions handler."""
        pass

    def process(
        self,
        df: pd.DataFrame,
        splits: pd.Series,
        dividends: pd.Series,
        ticker: str = "UNKNOWN"
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Process corporate actions and flag events in data.

        Args:
            df: Input dataframe with OHLCV data
            splits: Pandas Series of splits with date index
            dividends: Pandas Series of dividends with date index
            ticker: Ticker symbol for logging

        Returns:
            Tuple[pd.DataFrame, Dict]: Dataframe with corporate action flags and report
        """
        logger.info(f"Processing corporate actions for {ticker}")

        df = df.copy()

        # Initialize corporate action flag
        df['corporate_action_flag'] = ""

        splits_processed = 0
        dividends_processed = 0

        # Handle splits
        if not splits.empty:
            splits_processed = self._handle_splits(
                df, splits, ticker
            )

        # Handle dividends
        if not dividends.empty:
            dividends_processed = self._handle_dividends(
                df, dividends, ticker
            )

        action_report = {
            'splits_found': splits_processed,
            'dividends_found': dividends_processed,
            'total_events': splits_processed + dividends_processed,
            'event_dates': df[df['corporate_action_flag'] != ""].index.tolist()
        }

        logger.info(
            f"Corporate actions for {ticker}: "
            f"{splits_processed} splits, {dividends_processed} dividends"
        )

        return df, action_report

    def _handle_splits(
        self,
        df: pd.DataFrame,
        splits: pd.Series,
        ticker: str
    ) -> int:
        """
        Process stock splits and flag in dataframe.

        Args:
            df: Input dataframe
            splits: Series of splits
            ticker: Ticker symbol

        Returns:
            int: Number of splits processed
        """
        count = 0

        for split_date, split_ratio in splits.items():
            # Find closest date in dataframe
            date = pd.Timestamp(split_date)

            if date in df.index:
                df.loc[date,
                       'corporate_action_flag'] += f"SPLIT:{split_ratio}|"
                count += 1
                logger.info(
                    f"Flagged split for {ticker} on {date}: ratio {split_ratio}"
                )
            elif date.tz_localize(None) in df.index.tz_localize(None):
                # Handle timezone differences
                matching_idx = df.index[df.index.tz_localize(
                    None) == date.tz_localize(None)]
                if len(matching_idx) > 0:
                    df.loc[matching_idx[0],
                           'corporate_action_flag'] += f"SPLIT:{split_ratio}|"
                    count += 1

        return count

    def _handle_dividends(
        self,
        df: pd.DataFrame,
        dividends: pd.Series,
        ticker: str
    ) -> int:
        """
        Process dividends and flag in dataframe.

        Args:
            df: Input dataframe
            dividends: Series of dividends
            ticker: Ticker symbol

        Returns:
            int: Number of dividends processed
        """
        count = 0

        for div_date, div_amount in dividends.items():
            # Find closest date in dataframe
            date = pd.Timestamp(div_date)

            if date in df.index:
                df.loc[date,
                       'corporate_action_flag'] += f"DIV:{div_amount:.2f}|"
                count += 1
                logger.info(
                    f"Flagged dividend for {ticker} on {date}: ${div_amount:.2f}"
                )
            elif date.tz_localize(None) in df.index.tz_localize(None):
                # Handle timezone differences
                matching_idx = df.index[df.index.tz_localize(
                    None) == date.tz_localize(None)]
                if len(matching_idx) > 0:
                    df.loc[matching_idx[0],
                           'corporate_action_flag'] += f"DIV:{div_amount:.2f}|"
                    count += 1

        return count
