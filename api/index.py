"""
Vercel Serverless API Endpoint for OHLCV Market Data Pipeline & Anomaly Engine
"""

from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Any, Dict, List
import math

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validator import OHLCVValidator
from cleaner import OHLCVCleaner
from outlier import OutlierDetector
from corporate_actions import CorporateActionsHandler

app = Flask(__name__)

def sanitize_json(obj: Any) -> Any:
    """Recursively convert NumPy data types to Python native types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [sanitize_json(v) for v in obj]
    elif isinstance(obj, np.ndarray):
        return [sanitize_json(v) for v in obj.tolist()]
    elif isinstance(obj, (float, np.float32, np.float64, np.floating)):
        val = float(obj)
        return None if math.isnan(val) or math.isinf(val) else val
    elif isinstance(obj, (int, np.int32, np.int64, np.integer)):
        return int(obj)
    elif isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    else:
        return obj

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # 20-day SMA & Bollinger Bands
    df['sma20'] = df['close'].rolling(20, min_periods=1).mean()
    df['std20'] = df['close'].rolling(20, min_periods=1).std().fillna(0)
    df['upper_band'] = df['sma20'] + (2.0 * df['std20'])
    df['lower_band'] = df['sma20'] - (2.0 * df['std20'])
    
    # 50-day SMA
    df['sma50'] = df['close'].rolling(50, min_periods=1).mean()
    
    # RSI (14)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()
    rs = gain / (loss + 1e-8)
    df['rsi'] = (100.0 - (100.0 / (1.0 + rs))).fillna(50.0)
    
    # MACD (12, 26, 9)
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # ATR (14)
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr14'] = true_range.rolling(14, min_periods=1).mean()

    # Volume Z-Score
    vol_mean = df['volume'].rolling(20, min_periods=1).mean()
    vol_std = df['volume'].rolling(20, min_periods=1).std().replace(0, 1)
    df['vol_zscore'] = (df['volume'] - vol_mean) / vol_std
    df['volume_anomaly'] = (df['vol_zscore'].abs() > 2.5).astype(int)

    # Roll Effective Spread Approximation
    delta_p = df['close'].diff()
    cov_dp = (delta_p * delta_p.shift(1)).rolling(20, min_periods=1).mean()
    df['roll_spread'] = 2.0 * np.sqrt(np.maximum(0.0, -cov_dp.fillna(0)))

    # Amihud Illiquidity Measure
    abs_ret = df['close'].pct_change().abs()
    dollar_vol = (df['close'] * df['volume']) + 1e-5
    df['amihud_illiquidity'] = (abs_ret / dollar_vol) * 1e6

    return df

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'online', 'system': 'OHLCV Market Data Validation Pipeline v2.1'})

@app.route('/api/validate', methods=['GET', 'POST'])
def validate_ticker():
    try:
        if request.method == 'POST':
            req = request.get_json(force=True) or {}
            ticker = req.get('ticker', 'AAPL').upper().strip()
            days = int(req.get('days', 365))
        else:
            ticker = request.args.get('ticker', 'AAPL').upper().strip()
            days = int(request.args.get('days', 365))

        # 1. Fetch raw ticker data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        raw_df = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if raw_df is None or raw_df.empty:
            return jsonify({'error': f'No data returned for ticker {ticker}'}), 400

        if isinstance(raw_df.columns, pd.MultiIndex):
            raw_df.columns = [col[0].lower() for col in raw_df.columns]
        else:
            raw_df.columns = [str(col).lower() for col in raw_df.columns]

        if 'adj close' in raw_df.columns and 'close' not in raw_df.columns:
            raw_df['close'] = raw_df['adj close']

        req_cols = ['open', 'high', 'low', 'close', 'volume']
        raw_df = raw_df[[c for c in req_cols if c in raw_df.columns]]

        # 2. Multi-layer Validation
        validator = OHLCVValidator()
        validated_df, error_report = validator.validate(raw_df, ticker)

        # 3. Intelligent Cleaning
        cleaner = OHLCVCleaner()
        cleaned_df, cleaning_report = cleaner.clean(validated_df, ticker)

        # 4. Outlier & Microstructure Anomaly Detection
        outlier_detector = OutlierDetector()
        final_df, outlier_report = outlier_detector.detect(cleaned_df, ticker)

        # 5. Technical Indicators
        final_df = calculate_technical_indicators(final_df)

        dates = [d.strftime('%Y-%m-%d') for d in final_df.index]
        
        ohlcv_records = []
        anomaly_audit_log = []

        for d, row in zip(dates, final_df.to_dict('records')):
            row['date'] = d
            is_outlier = bool(row.get('is_outlier', False)) or bool(row.get('volume_anomaly', 0) == 1)
            row['is_anomaly'] = is_outlier
            ohlcv_records.append(row)

            if is_outlier:
                anomaly_type = "Volume Spike" if row.get('volume_anomaly') == 1 else "Price Outlier / Microstructure"
                anomaly_audit_log.append({
                    'date': d,
                    'type': anomaly_type,
                    'close': float(row['close']),
                    'volume': float(row['volume']),
                    'zscore': round(float(row.get('vol_zscore', 0.0)), 2),
                    'action': "Verified / Sanitized"
                })

        quality_score = float(cleaning_report.get('quality_score', 98.5))
        avg_roll_spread = float(final_df['roll_spread'].mean())
        avg_amihud = float(final_df['amihud_illiquidity'].mean())

        response = {
            'success': True,
            'ticker': ticker,
            'data_points': len(final_df),
            'quality_score': quality_score,
            'metrics': {
                'avg_roll_spread': round(avg_roll_spread, 4),
                'avg_amihud_illiquidity': round(avg_amihud, 6),
                'total_anomalies': len(anomaly_audit_log),
                'contamination_rate': round(len(anomaly_audit_log) / max(len(final_df), 1) * 100.0, 2)
            },
            'validation_report': error_report,
            'cleaning_report': cleaning_report,
            'outlier_report': outlier_report,
            'audit_log': anomaly_audit_log,
            'series': ohlcv_records
        }

        return jsonify(sanitize_json(response))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel entrypoint
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
