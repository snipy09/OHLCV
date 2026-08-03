"""
Institutional-Grade Outlier & Microstructure Anomaly Detection Module
Combines Z-score, Dynamic Median Absolute Deviation (MAD), Isolation Forest ML, and Roll Bid-Ask Spread Estimator.
"""

from typing import Dict, Tuple
import pandas as pd
import numpy as np
from loguru import logger
from sklearn.ensemble import IsolationForest

from config import OUTLIER_STD_THRESHOLD, OUTLIER_WINDOW


class OutlierDetector:
    """
    Multi-model Outlier & Anomaly Detector for Financial OHLCV Data.
    - Robust MAD (Median Absolute Deviation) Z-score
    - Unsupervised Isolation Forest Anomaly Detection
    - Intraday & Volume Spike Detection
    - Roll Bid-Ask Spread & Illiquidity Microstructure Estimator
    """

    def __init__(
        self,
        std_threshold: float = OUTLIER_STD_THRESHOLD,
        window: int = OUTLIER_WINDOW
    ):
        self.std_threshold = std_threshold
        self.window = window

    def detect(self, df: pd.DataFrame, ticker: str = "UNKNOWN") -> Tuple[pd.DataFrame, Dict]:
        """
        Detect anomalies using ensemble statistical + ML models.
        """
        logger.info(f"Starting advanced outlier detection for {ticker}")

        df = df.copy()
        df['is_outlier'] = False

        # 1. Standard Rolling Return Z-score
        df['returns'] = df['close'].pct_change()
        df['rolling_mean'] = df['returns'].rolling(window=self.window).mean()
        df['rolling_std'] = df['returns'].rolling(window=self.window).std()

        df['z_score'] = np.abs(
            (df['returns'] - df['rolling_mean']) / (df['rolling_std'] + 1e-8)
        )
        outliers_std = df['z_score'] > self.std_threshold

        # 2. Dynamic Median Absolute Deviation (MAD) Z-score (Heavy-tail robust)
        rolling_median = df['returns'].rolling(window=self.window).median()
        mad = (df['returns'] - rolling_median).abs().rolling(window=self.window).median()
        mad_z_score = 0.6745 * (df['returns'] - rolling_median).abs() / (mad + 1e-8)
        outliers_mad = mad_z_score > 3.5

        # 3. Isolation Forest Unsupervised Anomaly Detection
        features = df[['open', 'high', 'low', 'close', 'volume']].copy()
        features['return'] = df['returns'].fillna(0)
        features['range'] = (df['high'] - df['low']) / (df['close'] + 1e-8)
        features = features.fillna(0)

        iso_forest = IsolationForest(contamination=0.03, random_state=42)
        iso_preds = iso_forest.fit_predict(features)
        outliers_iso = (iso_preds == -1)

        # 4. Intraday Price Spike Detection
        df['intraday_move'] = np.abs(df['high'] - df['low']) / (df['open'] + 1e-8)
        intraday_threshold = df['intraday_move'].quantile(0.99)
        outliers_intraday = df['intraday_move'] > (intraday_threshold * 1.8)

        # 5. Volume Spike Detection
        df['volume_ma'] = df['volume'].rolling(window=self.window).mean()
        df['volume_ratio'] = df['volume'] / (df['volume_ma'] + 1e-8)
        outliers_volume = df['volume_ratio'] > 4.5

        # 6. Microstructure Metric: Roll Bid-Ask Spread Estimator
        # Roll (1984) spread S = 2 * sqrt(-Cov(dPt, dPt-1))
        dp = df['close'].diff()
        cov = dp.cov(dp.shift(1))
        roll_spread = 2.0 * np.sqrt(max(0, -cov)) if not np.isnan(cov) and cov < 0 else 0.0

        # Combine ensemble flags
        df['is_outlier'] = outliers_std | outliers_mad | outliers_iso | outliers_intraday | outliers_volume

        outlier_count = df['is_outlier'].sum()
        outlier_percentage = (outlier_count / len(df)) * 100 if len(df) > 0 else 0.0

        if outlier_count > 0:
            logger.info(f"Detected {outlier_count} ensemble anomalies for {ticker} ({outlier_percentage:.2f}%)")

        # Clean up temporary columns
        df = df.drop(
            columns=[
                'returns', 'rolling_mean', 'rolling_std', 'z_score',
                'intraday_move', 'volume_ma', 'volume_ratio'
            ],
            errors='ignore'
        )

        detection_report = {
            'total_outliers': int(outlier_count),
            'outlier_percentage': float(outlier_percentage),
            'outlier_reasons': {
                'std_deviation': int(outliers_std.sum()),
                'robust_mad': int(outliers_mad.sum()),
                'isolation_forest': int(outliers_iso.sum()),
                'intraday_move': int(outliers_intraday.sum()),
                'volume_spike': int(outliers_volume.sum())
            },
            'roll_bid_ask_spread_est': float(roll_spread),
            'outlier_threshold': self.std_threshold,
            'window_size': self.window
        }

        return df, detection_report
