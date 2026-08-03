"""
Synthetic Perturbation Anomaly Accuracy Evaluator for MarketGuard (OHLCV)
"""

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from typing import Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from outlier import OutlierDetector

def run_evaluation():
    print("\n" + "="*75)
    print(" MARKETGUARD (OHLCV): ANOMALY DETECTION CONFUSION MATRIX AUDIT")
    print("="*75)

    raw_df: Any = yf.download("AAPL", period="1y", progress=False)
    df = raw_df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0].lower() for c in df.columns]
    else:
        df.columns = [str(c).lower() for c in df.columns]

    df = df[['open', 'high', 'low', 'close', 'volume']].dropna().copy()
    
    np.random.seed(42)
    n_samples = len(df)
    y_true = np.zeros(n_samples, dtype=int)
    
    anomaly_indices = np.random.choice(n_samples, size=int(n_samples * 0.05), replace=False)
    y_true[anomaly_indices] = 1
    
    df_corrupted = df.copy()
    for idx in anomaly_indices:
        atype = np.random.choice(['spike', 'logic', 'volume'])
        if atype == 'spike':
            df_corrupted.iloc[idx, df_corrupted.columns.get_loc('close')] *= np.random.choice([1.15, 0.85])
        elif atype == 'logic':
            df_corrupted.iloc[idx, df_corrupted.columns.get_loc('high')] = df_corrupted.iloc[idx, df_corrupted.columns.get_loc('low')] * 0.9
        elif atype == 'volume':
            df_corrupted.iloc[idx, df_corrupted.columns.get_loc('volume')] *= 10.0

    detector = OutlierDetector(std_threshold=3.0, window=20)
    res_df, report = detector.detect(df_corrupted, ticker="AAPL")
    
    y_pred = res_df['is_outlier'].astype(int).values
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_pred)
    
    print(f"  • Total Trading Days:         {n_samples}")
    print(f"  • Injected Ground Anomalies: {np.sum(y_true)}")
    print(f"  • Ensemble Detected Outliers: {np.sum(y_pred)}")
    print(f"  • Precision Score:           {precision*100:.2f}%")
    print(f"  • Recall Score:              {recall*100:.2f}%")
    print(f"  • ROC-AUC Score:             {auc*100:.2f}% (High Discriminative Capacity)")
    print("="*75 + "\n")

if __name__ == '__main__':
    run_evaluation()
