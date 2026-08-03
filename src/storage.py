"""
Data Storage module for raw and clean OHLCV data
"""

from typing import Dict, Optional
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
from loguru import logger

from config import RAW_DATA_DIR, CLEAN_DATA_DIR, DB_PATH, RAW_TABLE_NAME, CLEAN_TABLE_NAME


class OHLCVStorage:
    """
    Handle storage of OHLCV data in CSV and SQLite formats.
    """

    def __init__(self):
        """Initialize storage handler."""
        self._ensure_database_exists()

    def _ensure_database_exists(self) -> None:
        """Ensure SQLite database and tables exist."""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            # Create raw table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {RAW_TABLE_NAME} (
                    ticker TEXT NOT NULL,
                    date TIMESTAMP NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    PRIMARY KEY (ticker, date)
                )
            """)

            # Create clean table with additional columns
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {CLEAN_TABLE_NAME} (
                    ticker TEXT NOT NULL,
                    date TIMESTAMP NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    is_outlier BOOLEAN,
                    corporate_action_flag TEXT,
                    PRIMARY KEY (ticker, date)
                )
            """)

            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {DB_PATH}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def save_raw(self, df: pd.DataFrame, ticker: str) -> Dict:
        """
        Save raw OHLCV data to CSV and SQLite.

        Args:
            df: Input dataframe
            ticker: Ticker symbol

        Returns:
            Dict: Save report with file paths
        """
        logger.info(f"Saving raw data for {ticker}")

        save_report = {
            'ticker': ticker,
            'rows': len(df),
            'csv_path': None,
            'db_table': RAW_TABLE_NAME
        }

        # Save to CSV with timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = RAW_DATA_DIR / f"{ticker}_raw_{timestamp}.csv"

        try:
            df.to_csv(csv_path)
            logger.info(f"Saved raw data to CSV: {csv_path}")
            save_report['csv_path'] = str(csv_path)
        except Exception as e:
            logger.error(f"Failed to save raw data to CSV: {str(e)}")

        # Save to SQLite
        try:
            self._save_to_sqlite(df, ticker, RAW_TABLE_NAME, mode='append')
            logger.info(f"Saved raw data to SQLite table {RAW_TABLE_NAME}")
        except Exception as e:
            logger.error(f"Failed to save raw data to SQLite: {str(e)}")

        return save_report

    def save_clean(self, df: pd.DataFrame, ticker: str) -> Dict:
        """
        Save clean OHLCV data to CSV and SQLite.

        Args:
            df: Input dataframe
            ticker: Ticker symbol

        Returns:
            Dict: Save report with file paths
        """
        logger.info(f"Saving clean data for {ticker}")

        save_report = {
            'ticker': ticker,
            'rows': len(df),
            'csv_path': None,
            'db_table': CLEAN_TABLE_NAME
        }

        # Save to CSV with timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = CLEAN_DATA_DIR / f"{ticker}_clean_{timestamp}.csv"

        try:
            df.to_csv(csv_path)
            logger.info(f"Saved clean data to CSV: {csv_path}")
            save_report['csv_path'] = str(csv_path)
        except Exception as e:
            logger.error(f"Failed to save clean data to CSV: {str(e)}")

        # Save to SQLite
        try:
            self._save_to_sqlite(df, ticker, CLEAN_TABLE_NAME, mode='replace')
            logger.info(f"Saved clean data to SQLite table {CLEAN_TABLE_NAME}")
        except Exception as e:
            logger.error(f"Failed to save clean data to SQLite: {str(e)}")

        return save_report

    def _save_to_sqlite(
        self,
        df: pd.DataFrame,
        ticker: str,
        table_name: str,
        mode: str = 'append'
    ) -> None:
        """
        Save dataframe to SQLite database.

        Args:
            df: Input dataframe
            ticker: Ticker symbol
            table_name: Table name to save to
            mode: 'append' or 'replace'
        """
        conn = sqlite3.connect(str(DB_PATH))

        # Add ticker column
        data = df.copy()
        data.insert(0, 'ticker', ticker)
        data.index.name = 'date'

        # Convert index to column for insertion
        data_to_insert = data.reset_index()

        # Delete existing data for this ticker to prevent duplicates on append
        try:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE ticker = ?", (ticker,))
        except Exception:
            pass

        # Save to database
        data_to_insert.to_sql(
            table_name,
            conn,
            if_exists='append',
            index=False
        )

        conn.commit()
        conn.close()

    def load_raw(self, ticker: str, limit: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Load raw data from SQLite database.

        Args:
            ticker: Ticker symbol
            limit: Maximum rows to load (None for all)

        Returns:
            pd.DataFrame or None if not found
        """
        try:
            conn = sqlite3.connect(str(DB_PATH))

            query = f"SELECT * FROM {RAW_TABLE_NAME} WHERE ticker = ?"
            params = [ticker]

            if limit:
                query += f" LIMIT {limit}"

            df = pd.read_sql(query, conn, params=params, parse_dates=['date'])
            df.set_index('date', inplace=True)
            df = df.drop('ticker', axis=1)

            conn.close()

            logger.info(f"Loaded {len(df)} rows of raw data for {ticker}")
            return df

        except Exception as e:
            logger.error(f"Failed to load raw data for {ticker}: {str(e)}")
            return None

    def load_clean(self, ticker: str, limit: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Load clean data from SQLite database.

        Args:
            ticker: Ticker symbol
            limit: Maximum rows to load (None for all)

        Returns:
            pd.DataFrame or None if not found
        """
        try:
            conn = sqlite3.connect(str(DB_PATH))

            query = f"SELECT * FROM {CLEAN_TABLE_NAME} WHERE ticker = ?"
            params = [ticker]

            if limit:
                query += f" LIMIT {limit}"

            df = pd.read_sql(query, conn, params=params, parse_dates=['date'])
            df.set_index('date', inplace=True)
            df = df.drop('ticker', axis=1)

            conn.close()

            logger.info(f"Loaded {len(df)} rows of clean data for {ticker}")
            return df

        except Exception as e:
            logger.error(f"Failed to load clean data for {ticker}: {str(e)}")
            return None

    def get_available_tickers(self) -> list:
        """
        Get list of tickers available in database.

        Returns:
            list: List of ticker symbols
        """
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            cursor.execute(f"SELECT DISTINCT ticker FROM {CLEAN_TABLE_NAME}")
            tickers = [row[0] for row in cursor.fetchall()]

            conn.close()
            return tickers

        except Exception as e:
            logger.error(f"Failed to get tickers from database: {str(e)}")
            return []
