"""
Practical usage examples for OHLCV Data Validation & Monitoring System
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path FIRST (before any imports from src)
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from config import DEFAULT_TICKERS
from utils import setup_logger, calculate_data_quality_score, get_quality_rating
from fetcher import OHLCVFetcher
from validator import OHLCVValidator
from cleaner import OHLCVCleaner
from outlier import OutlierDetector
from storage import OHLCVStorage


def example_1_fetch_data():
    """Example 1: Fetch raw OHLCV data"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 1: Fetch raw OHLCV data")
    logger.info("="*60)

    fetcher = OHLCVFetcher()
    ticker = "AAPL"

    logger.info(f"Fetching data for {ticker}...")
    data = fetcher.fetch_ticker(ticker)

    if data is not None:
        logger.info(f"[SUCCESS] Fetched {len(data)} rows")
        logger.info(f"Columns: {list(data.columns)}")
        logger.info(f"Date range: {data.index.min()} to {data.index.max()}")
        logger.info(f"\nFirst 5 rows:\n{data.head()}")
    else:
        logger.error(f"Failed to fetch {ticker}")


def example_2_validate_data():
    """Example 2: Validate data"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 2: Validate data")
    logger.info("="*60)

    fetcher = OHLCVFetcher()
    validator = OHLCVValidator()
    ticker = "MSFT"

    data = fetcher.fetch_ticker(ticker)
    if data is None:
        logger.error(f"Failed to fetch {ticker}")
        return

    logger.info(f"Validating {len(data)} rows for {ticker}...")
    validated_data, validation_report = validator.validate(data, ticker)

    logger.info(f"Validation Report:")
    logger.info(f"  Total Errors: {validation_report['total_errors']}")
    logger.info(f"  Total Warnings: {validation_report['total_warnings']}")

    if validation_report['errors']:
        logger.warning(f"Errors found:")
        for error in validation_report['errors'][:5]:
            logger.warning(f"    - {error}")

    logger.info(f"[SUCCESS] Validation complete")


def example_3_clean_data():
    """Example 3: Clean data"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 3: Clean data")
    logger.info("="*60)

    fetcher = OHLCVFetcher()
    validator = OHLCVValidator()
    cleaner = OHLCVCleaner()
    ticker = "GOOGL"

    data = fetcher.fetch_ticker(ticker)
    if data is None:
        logger.error(f"Failed to fetch {ticker}")
        return

    validated_data, _ = validator.validate(data, ticker)
    logger.info(f"Cleaning {len(validated_data)} rows for {ticker}...")

    cleaned_data, cleaning_report = cleaner.clean(validated_data, ticker)

    logger.info(f"Cleaning Report:")
    logger.info(f"  Initial rows: {cleaning_report['initial_rows']}")
    logger.info(f"  Rows removed: {cleaning_report['rows_removed']}")
    logger.info(f"  Final rows: {cleaning_report['final_rows']}")

    logger.info(f"[SUCCESS] Cleaning complete")


def example_4_detect_outliers():
    """Example 4: Detect outliers"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 4: Detect outliers")
    logger.info("="*60)

    fetcher = OHLCVFetcher()
    validator = OHLCVValidator()
    cleaner = OHLCVCleaner()
    outlier_detector = OutlierDetector()
    ticker = "AAPL"

    data = fetcher.fetch_ticker(ticker)
    if data is None:
        logger.error(f"Failed to fetch {ticker}")
        return

    validated_data, _ = validator.validate(data, ticker)
    cleaned_data, _ = cleaner.clean(validated_data, ticker)

    logger.info(f"Detecting outliers in {len(cleaned_data)} rows for {ticker}...")
    outlier_data, outlier_report = outlier_detector.detect(cleaned_data, ticker)

    logger.info(f"Outlier Detection Report:")
    logger.info(f"  Total outliers: {outlier_report['total_outliers']}")
    logger.info(f"  Outlier percentage: {outlier_report['outlier_percentage']:.2f}%")
    
    reasons = outlier_report['outlier_reasons']
    logger.info(f"  Std deviation outliers: {reasons['std_deviation']}")
    logger.info(f"  Intraday move outliers: {reasons['intraday_move']}")
    logger.info(f"  Volume spike outliers: {reasons['volume_spike']}")

    logger.info(f"[SUCCESS] Outlier detection complete")


def example_5_store_and_retrieve():
    """Example 5: Store and retrieve data"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 5: Store and retrieve data")
    logger.info("="*60)

    fetcher = OHLCVFetcher()
    validator = OHLCVValidator()
    cleaner = OHLCVCleaner()
    storage = OHLCVStorage()
    ticker = "MSFT"

    data = fetcher.fetch_ticker(ticker)
    if data is None:
        logger.error(f"Failed to fetch {ticker}")
        return

    validated_data, _ = validator.validate(data, ticker)
    cleaned_data, _ = cleaner.clean(validated_data, ticker)

    logger.info(f"Storing {len(cleaned_data)} rows for {ticker}...")

    # Store raw data
    raw_report = storage.save_raw(data, ticker)
    logger.info(f"Raw data saved: CSV and SQLite")

    # Store clean data
    clean_report = storage.save_clean(cleaned_data, ticker)
    logger.info(f"Clean data saved: CSV and SQLite")

    # Retrieve from SQLite
    logger.info(f"\nRetrieving data from database...")
    retrieved_data = storage.load_clean(ticker)

    if retrieved_data is not None:
        logger.info(f"[SUCCESS] Retrieved {len(retrieved_data)} rows for {ticker}")
        logger.info(f"Date range: {retrieved_data.index.min()} to {retrieved_data.index.max()}")
    else:
        logger.warning(f"No data found for {ticker} in database")


def example_6_quality_score():
    """Example 6: Calculate data quality score"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 6: Calculate data quality score")
    logger.info("="*60)

    fetcher = OHLCVFetcher()
    validator = OHLCVValidator()
    cleaner = OHLCVCleaner()
    ticker = "GOOGL"

    data = fetcher.fetch_ticker(ticker)
    if data is None:
        logger.error(f"Failed to fetch {ticker}")
        return

    validated_data, validation_report = validator.validate(data, ticker)
    cleaned_data, _ = cleaner.clean(validated_data, ticker)

    logger.info(f"Calculating quality score for {ticker}...")

    quality_score = calculate_data_quality_score(cleaned_data, validation_report['errors'])
    quality_rating = get_quality_rating(quality_score)

    logger.info(f"Quality Score: {quality_score:.2f}/100")
    logger.info(f"Quality Rating: {quality_rating}")

    logger.info(f"[SUCCESS] Quality assessment complete")


def main():
    """Run all examples"""
    # Setup logging
    setup_logger()

    logger.info("="*60)
    logger.info("OHLCV Data Validation & Monitoring System - Examples")
    logger.info("="*60)

    # Run examples
    example_1_fetch_data()
    example_2_validate_data()
    example_3_clean_data()
    example_4_detect_outliers()
    example_5_store_and_retrieve()
    example_6_quality_score()

    logger.info("\n" + "="*60)
    logger.info("All examples completed successfully!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
