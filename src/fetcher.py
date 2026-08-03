"""
OHLCV Data Fetcher module using yfinance
"""

from typing import Dict, List, Optional
import pandas as pd
import yfinance as yf
from loguru import logger
import time

from config import FETCH_PERIOD, FETCH_INTERVAL, RETRY_ATTEMPTS, RETRY_DELAY
from utils import standardize_dataframe, validate_ticker


class OHLCVFetcher:
    """
    Fetch OHLCV data from Yahoo Finance using yfinance.
    """

    def __init__(
        self,
        period: str = FETCH_PERIOD,
        interval: str = FETCH_INTERVAL,
        retry_attempts: int = RETRY_ATTEMPTS,
        retry_delay: float = RETRY_DELAY
    ):
        """
        Initialize OHLCV Fetcher.

        Args:
            period: Data period (e.g., '1y', '6mo', '1d')
            interval: Data interval (e.g., '1d', '1h', '15m')
            retry_attempts: Number of retry attempts on failure
            retry_delay: Delay in seconds between retries
        """
        self.period = period
        self.interval = interval
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.fetch_errors = {}

    def fetch_ticker(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data for a single ticker with retry logic.

        Args:
            ticker: Ticker symbol

        Returns:
            pd.DataFrame: OHLCV data or None if fetch fails
        """
        if not validate_ticker(ticker):
            logger.error(f"Invalid ticker format: {ticker}")
            return None

        logger.info(f"Fetching data for ticker: {ticker}")

        for attempt in range(self.retry_attempts):
            try:
                data = yf.download(
                    ticker,
                    period=self.period,
                    interval=self.interval,
                    progress=False,
                    prepost=False
                )

                if data.empty:
                    logger.warning(f"No data returned for ticker: {ticker}")
                    return None

                data = standardize_dataframe(data)
                logger.info(
                    f"Successfully fetched {len(data)} rows for {ticker}")
                return data

            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{self.retry_attempts} failed for {ticker}: {str(e)}"
                )
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)

        logger.error(
            f"Failed to fetch {ticker} after {self.retry_attempts} attempts")
        self.fetch_errors[ticker] = f"Failed after {self.retry_attempts} attempts"
        return None

    def fetch_multiple(self, tickers: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Fetch OHLCV data for multiple tickers.

        Args:
            tickers: List of ticker symbols

        Returns:
            Dict[str, pd.DataFrame]: Dictionary of ticker -> dataframe
        """
        results = {}

        logger.info(f"Fetching data for {len(tickers)} tickers")

        for ticker in tickers:
            data = self.fetch_ticker(ticker)
            if data is not None:
                results[ticker] = data

        logger.info(
            f"Successfully fetched {len(results)}/{len(tickers)} tickers")

        if self.fetch_errors:
            logger.warning(f"Fetch errors: {self.fetch_errors}")

        return results

    def fetch_splits_and_dividends(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        Fetch splits and dividends data for a ticker.

        Args:
            ticker: Ticker symbol

        Returns:
            Dict with 'splits' and 'dividends' DataFrames
        """
        logger.info(f"Fetching splits and dividends for {ticker}")

        try:
            ticker_obj = yf.Ticker(ticker)

            splits = ticker_obj.splits
            dividends = ticker_obj.dividends

            logger.info(
                f"Found {len(splits)} splits and {len(dividends)} dividends for {ticker}"
            )

            return {
                'splits': splits,
                'dividends': dividends
            }

        except Exception as e:
            logger.error(
                f"Failed to fetch corporate actions for {ticker}: {str(e)}")
            return {
                'splits': pd.Series(dtype='float64'),
                'dividends': pd.Series(dtype='float64')
            }
