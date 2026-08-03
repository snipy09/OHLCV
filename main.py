"""
Main pipeline for OHLCV Data Validation & Monitoring System

Complete workflow:
1. Fetch raw data
2. Store raw data
3. Validate data
4. Clean data
5. Detect outliers
6. Handle corporate actions
7. Store clean data
8. Calculate quality score
"""

import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd

# Add src to path FIRST (before any imports from src)
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from config import DEFAULT_TICKERS
from utils import setup_logger, calculate_data_quality_score, get_quality_rating, format_error_report
from fetcher import OHLCVFetcher
from validator import OHLCVValidator
from cleaner import OHLCVCleaner
from outlier import OutlierDetector
from corporate_actions import CorporateActionsHandler
from storage import OHLCVStorage


class OHLCVPipeline:
    """
    Complete OHLCV data processing pipeline.
    """

    def __init__(self, tickers: List[str] = None):
        """
        Initialize the pipeline.

        Args:
            tickers: List of ticker symbols to process
        """
        self.tickers = tickers or DEFAULT_TICKERS
        self.fetcher = OHLCVFetcher()
        self.validator = OHLCVValidator()
        self.cleaner = OHLCVCleaner()
        self.outlier_detector = OutlierDetector()
        self.corporate_actions_handler = CorporateActionsHandler()
        self.storage = OHLCVStorage()

        self.results = {}

    def run(self) -> Dict:
        """
        Run complete pipeline for all tickers.

        Returns:
            Dict: Pipeline results for all tickers
        """
        logger.info(f"Starting OHLCV pipeline for {len(self.tickers)} tickers")

        for ticker in self.tickers:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {ticker}")
            logger.info(f"{'='*60}")

            self._process_ticker(ticker)

        logger.info(f"\n{'='*60}")
        logger.info("Pipeline complete")
        logger.info(f"{'='*60}")

        return self.results

    def _process_ticker(self, ticker: str) -> None:
        """
        Process single ticker through complete pipeline.

        Args:
            ticker: Ticker symbol
        """
        ticker_result = {
            'ticker': ticker,
            'status': 'failed',
            'stages': {}
        }

        try:
            # Stage 1: Fetch raw data
            logger.info("\n[1/7] Fetching data...")
            raw_data = self.fetcher.fetch_ticker(ticker)

            if raw_data is None or raw_data.empty:
                logger.error(f"Failed to fetch data for {ticker}")
                ticker_result['status'] = 'fetch_failed'
                self.results[ticker] = ticker_result
                return

            ticker_result['stages']['fetch'] = {
                'rows': len(raw_data),
                'columns': list(raw_data.columns)
            }

            # Stage 2: Store raw data
            logger.info("[2/7] Storing raw data...")
            raw_save_report = self.storage.save_raw(raw_data, ticker)
            ticker_result['stages']['raw_storage'] = raw_save_report

            # Stage 3: Validate data
            logger.info("[3/7] Validating data...")
            validated_data, validation_report = self.validator.validate(raw_data, ticker)
            ticker_result['stages']['validation'] = validation_report

            if validation_report['total_errors'] > 0:
                logger.warning(f"Validation errors found:\n{format_error_report(validation_report['errors'])}")

            # Stage 4: Clean data
            logger.info("[4/7] Cleaning data...")
            cleaned_data, cleaning_report = self.cleaner.clean(validated_data, ticker)
            ticker_result['stages']['cleaning'] = cleaning_report

            if len(cleaned_data) == 0:
                logger.error(f"No data remaining after cleaning for {ticker}")
                ticker_result['status'] = 'empty_after_cleaning'
                self.results[ticker] = ticker_result
                return

            # Stage 5: Detect outliers
            logger.info("[5/7] Detecting outliers...")
            outlier_data, outlier_report = self.outlier_detector.detect(cleaned_data, ticker)
            ticker_result['stages']['outlier_detection'] = outlier_report

            # Stage 6: Handle corporate actions
            logger.info("[6/7] Processing corporate actions...")
            corporate_actions = self.fetcher.fetch_splits_and_dividends(ticker)
            final_data, actions_report = self.corporate_actions_handler.process(
                outlier_data,
                corporate_actions['splits'],
                corporate_actions['dividends'],
                ticker
            )
            ticker_result['stages']['corporate_actions'] = actions_report

            # Stage 7: Store clean data
            logger.info("[7/7] Storing clean data...")
            clean_save_report = self.storage.save_clean(final_data, ticker)
            ticker_result['stages']['clean_storage'] = clean_save_report

            # Calculate quality score
            quality_score = calculate_data_quality_score(final_data, validation_report['errors'])
            quality_rating = get_quality_rating(quality_score)

            ticker_result['status'] = 'success'
            ticker_result['quality_score'] = quality_score
            ticker_result['quality_rating'] = quality_rating
            ticker_result['final_rows'] = len(final_data)

            logger.info(f"\n✓ {ticker} processing complete")
            logger.info(f"  Quality Score: {quality_score:.2f}/100 ({quality_rating})")
            logger.info(f"  Final rows: {len(final_data)}")

        except Exception as e:
            logger.error(f"Error processing {ticker}: {str(e)}")
            ticker_result['status'] = 'error'
            ticker_result['error'] = str(e)

        finally:
            self.results[ticker] = ticker_result

    def get_summary(self) -> Dict:
        """
        Get summary of pipeline results.

        Returns:
            Dict: Summary statistics
        """
        summary = {
            'total_tickers': len(self.results),
            'successful': sum(1 for r in self.results.values() if r['status'] == 'success'),
            'failed': sum(1 for r in self.results.values() if r['status'] != 'success'),
            'tickers': self.results
        }

        return summary


def main():
    """Main entry point."""
    # Setup logging
    setup_logger()

    logger.info("Starting OHLCV Data Validation & Monitoring System")

    # Create and run pipeline
    pipeline = OHLCVPipeline(tickers=DEFAULT_TICKERS)
    results = pipeline.run()

    # Print summary
    summary = pipeline.get_summary()

    logger.info("\n" + "="*60)
    logger.info("PIPELINE SUMMARY")
    logger.info("="*60)
    logger.info(f"Total tickers processed: {summary['total_tickers']}")
    logger.info(f"Successful: {summary['successful']}")
    logger.info(f"Failed: {summary['failed']}")

    for ticker, result in summary['tickers'].items():
        status_icon = "✓" if result['status'] == 'success' else "✗"
        logger.info(
            f"\n{status_icon} {ticker}: {result['status'].upper()}"
        )
        if result['status'] == 'success':
            logger.info(
                f"  Quality: {result['quality_rating']} ({result['quality_score']:.2f}/100)"
            )
            logger.info(f"  Final rows: {result['final_rows']}")


if __name__ == "__main__":
    main()
