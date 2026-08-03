"""
Configuration file for OHLCV Data Validation & Monitoring System
"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "clean"
LOGS_DIR = PROJECT_ROOT / "logs"

# Database configuration
DB_PATH = PROJECT_ROOT / "ohlcv_data.db"
RAW_TABLE_NAME = "raw_ohlcv"
CLEAN_TABLE_NAME = "clean_ohlcv"

# Data fetcher config
FETCH_PERIOD = "1y"  # Default period
FETCH_INTERVAL = "1d"  # Daily data
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds

# Validation config
NULL_THRESHOLD = 0.5  # Percentage threshold for dropping columns with nulls

# Outlier detection config
OUTLIER_STD_THRESHOLD = 5.0  # 5 standard deviations
OUTLIER_WINDOW = 30  # Rolling window for calculating std

# Logging config
LOG_LEVEL = "INFO"
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"

# Default tickers
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL"]

# Quality score thresholds
QUALITY_SCORE_EXCELLENT = 95
QUALITY_SCORE_GOOD = 80
QUALITY_SCORE_WARNING = 60

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
