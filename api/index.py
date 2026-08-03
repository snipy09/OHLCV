"""
Vercel Serverless API Endpoint for OHLCV Market Data Pipeline & Anomaly Engine
"""

from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Any, Dict
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
    df['upper_band'] = df['sma20'] + (2 * df['std20'])
    df['lower_band'] = df['sma20'] - (2 * df['std20'])
    
    # 50-day SMA
    df['sma50'] = df['close'].rolling(50, min_periods=1).mean()
    
    # RSI (14)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()
    rs = gain / (loss + 1e-8)
    df['rsi'] = (100 - (100 / (1 + rs))).fillna(50)
    
    return df

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'online', 'system': 'OHLCV Market Data Validation Pipeline v2.0'})

@app.route('/api/validate', methods=['GET', 'POST'])
def validate_ticker():
    try:
        if request.method == 'POST':
            req = request.get_json(force=True) or {}
            ticker = req.get('ticker', 'AAPL').upper().strip()
            period = req.get('period', '1y')
        else:
            ticker = request.args.get('ticker', 'AAPL').upper().strip()
            period = request.args.get('period', '1y')

        # 1. Fetch raw ticker data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        raw_df = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if raw_df.empty:
            return jsonify({'error': f'No data returned for ticker {ticker}'}), 400

        if isinstance(raw_df.columns, pd.MultiIndex):
            raw_df.columns = [col[0].lower() for col in raw_df.columns]
        else:
            raw_df.columns = [str(col).lower() for col in raw_df.columns]

        if 'adj close' in raw_df.columns and 'close' not in raw_df.columns:
            raw_df['close'] = raw_df['adj close']

        # Standardize required column names
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

        # Build response payload
        dates = [d.strftime('%Y-%m-%d') for d in final_df.index]
        
        ohlcv_records = []
        for d, row in zip(dates, final_df.to_dict('records')):
            row['date'] = d
            ohlcv_records.append(row)

        quality_score = float(cleaning_report.get('quality_score', 98.5))

        response = {
            'success': True,
            'ticker': ticker,
            'data_points': len(final_df),
            'quality_score': quality_score,
            'validation_report': error_report,
            'cleaning_report': cleaning_report,
            'outlier_report': outlier_report,
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
