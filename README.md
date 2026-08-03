# 🛡️ MarketGuard: Production OHLCV Data Validation & Anomaly Engine

<div align="center">

**Institutional Financial Market Data Cleaning, Isolation Forest ML & Roll Spread Anomaly Pipeline**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)
![FINRA](https://img.shields.io/badge/Standard-FINRA%20Quality-emerald?style=flat-square)
![ML](https://img.shields.io/badge/ML-Isolation%20Forest-purple?style=flat-square)
![Vercel](https://img.shields.io/badge/Deployment-Vercel%20Live-brightgreen?style=flat-square&logo=vercel)

[🚀 Live Market Terminal](https://ohlcv-market-pipeline.vercel.app) • [GitHub Repository](https://github.com/snipy09/OHLCV)

</div>

---

## 💡 Overview

**MarketGuard** is an institutional-grade Open-High-Low-Close-Volume (OHLCV) data validation, cleaning, and anomaly detection pipeline for financial markets. Designed for quantitative traders and algorithmic trading systems, it detects data corruption, zero-volume spikes, missing timestamps, and price manipulation using statistical and machine learning methods.

### Key Features
- 🔍 **Multi-Layer Validation**: Checks structural integrity, logical price bounds ($H \ge \max(O,C)$, $L \le \min(O,C)$), and temporal date continuity.
- 🤖 **Ensemble Anomaly Detection**:
  - Rolling Z-score return thresholds
  - Robust Median Absolute Deviation (MAD)
  - Unsupervised `IsolationForest` machine learning
- 📊 **Microstructure Analytics**: Roll Bid-Ask Spread estimator ($S = 2\sqrt{-\text{Cov}(\Delta P_t, \Delta P_{t-1})}$) for liquidity shock detection.
- 🎯 **FINRA Quality Scoring**: 0–100 data health index with rating scale (EXCELLENT / GOOD / POOR).
- 💾 **Dual Storage Persistence**: Automated CSV backup and SQLite table indexing.
- 🌐 **Interactive Market Terminal**: Live Vercel dashboard with Plotly candlestick charts, volume subplots, and anomaly markers.

---

## 🚀 Quick Start

```bash
git clone https://github.com/snipy09/OHLCV.git
cd OHLCV

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run Validation Pipeline CLI
python3 main.py
```

---

## 🌐 Live Web Deployment

Deployed live on Vercel: **[https://ohlcv-market-pipeline.vercel.app](https://ohlcv-market-pipeline.vercel.app)**
