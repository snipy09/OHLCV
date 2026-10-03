# OHLCV

A production-grade pipeline for fetching, validating, cleaning, and monitoring OHLCV financial market data.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Streamlit](https://img.shields.io/badge/dashboard-streamlit-red)](https://streamlit.io/)

---

## Overview

OHLCV is a modular data engineering system built around Open, High, Low, Close, and Volume financial data. It provides a complete validation and monitoring pipeline — from raw data ingestion via Yahoo Finance through multi-layer quality checks, outlier detection, corporate action handling, and dual-format storage — surfaced through an interactive Streamlit dashboard.

The project is designed as a robust backend for quantitative research workflows where data quality and auditability are non-negotiable.

---

## Features

| Category | Capability |
|---|---|
| Data Fetching | Yahoo Finance via `yfinance` with configurable retry logic |
| Validation | Multi-layer validation engine covering schema, range, and consistency checks |
| Outlier Detection | Z-score based detection with configurable sensitivity thresholds |
| Corporate Actions | Automatic handling of stock splits and dividend adjustments |
| Data Cleaning | Modular cleaning pipeline with per-step logging |
| Storage | Dual output to CSV and SQLite; query-ready from day one |
| Quality Scoring | Per-dataset quality score and letter-grade rating |
| Dashboard | Real-time Streamlit UI with Plotly charts and technical indicators |
| Logging | Structured log rotation via `loguru` |
| Deployment | Vercel-compatible via `api/index.py` + `vercel.json` |

---

## Architecture

```
OHLCV/
├── src/
│   ├── __init__.py
│   ├── config.py               # Centralised configuration constants
│   ├── utils.py                # Shared utility functions
│   ├── fetcher.py              # OHLCVFetcher — yfinance wrapper with retry
│   ├── validator.py            # Multi-layer validation engine
│   ├── cleaner.py              # Data cleaning pipeline
│   ├── outlier.py              # Z-score outlier detection
│   ├── corporate_actions.py    # Split and dividend adjustment handlers
│   └── storage.py              # CSV and SQLite storage adapters
├── dashboard/
│   ├── __init__.py
│   └── app.py                  # Streamlit dashboard with Plotly charts
├── api/
│   └── index.py                # Vercel serverless entry point
├── main.py                     # Pipeline orchestrator
├── example.py                  # Usage examples
├── test_installation.py        # Smoke test for installation
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── setup.sh
└── vercel.json
```

---

## Pipeline Stages

```
Fetch  →  Validate  →  Detect Outliers  →  Handle Corporate Actions  →  Clean  →  Score  →  Store
```

| Stage | Module | Description |
|---|---|---|
| Fetch | `fetcher.py` | Download OHLCV data from Yahoo Finance with exponential backoff |
| Validate | `validator.py` | Check schema integrity, value ranges, OHLC consistency, and volume sanity |
| Detect Outliers | `outlier.py` | Flag statistically anomalous rows using Z-score method |
| Corporate Actions | `corporate_actions.py` | Adjust prices and volumes for splits and dividends |
| Clean | `cleaner.py` | Fill gaps, drop duplicates, normalise data types |
| Score | `validator.py` | Compute a data quality score (0–100) and assign a letter grade |
| Store | `storage.py` | Write output to CSV and/or SQLite |

---

## Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9 or higher |
| pip | Latest recommended |

### Installation

```bash
# Clone the repository
git clone https://github.com/snipy09/OHLCV.git
cd OHLCV

# (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt
```

Alternatively, use the provided setup script:

```bash
bash setup.sh
```

Or the Makefile shortcut:

```bash
make install
```

### Verify Installation

```bash
python test_installation.py
```

### Run the Pipeline

```bash
# Run with defaults (see src/config.py for configuration)
python main.py

# Run the usage examples
python example.py
```

---

## Dashboard

The Streamlit dashboard provides real-time monitoring of data quality metrics, OHLCV candlestick charts, volume profiles, outlier visualisations, and technical indicators.

### Launch Locally

```bash
streamlit run dashboard/app.py
```

The dashboard opens at `http://localhost:8501` by default.

### Makefile Shortcut

```bash
make dashboard
```

### Features at a Glance

- Interactive candlestick chart (Plotly)
- Volume bar chart with colour-coded sessions
- Z-score overlay for outlier identification
- Data quality score card and grade badge
- Corporate action event markers on price chart
- Technical indicator panel (configurable in `src/config.py`)

---

## Configuration

All runtime parameters are centralised in `src/config.py`. Key options:

| Parameter | Description |
|---|---|
| `DEFAULT_TICKER` | Default stock symbol to fetch |
| `DATE_RANGE_START` | Historical start date |
| `DATE_RANGE_END` | Historical end date (or `None` for today) |
| `ZSCORE_THRESHOLD` | Outlier sensitivity (default: 3.0) |
| `STORAGE_FORMAT` | `"csv"`, `"sqlite"`, or `"both"` |
| `LOG_ROTATION` | Log file rotation policy (e.g., `"10 MB"`) |
| `LOG_DIR` | Directory for loguru log files |

---

## Tech Stack

| Library | Role |
|---|---|
| `yfinance` | Market data fetching |
| `pandas` | Data manipulation and storage |
| `numpy` | Numerical operations |
| `scipy` | Statistical computations |
| `scikit-learn` | Preprocessing utilities |
| `streamlit` | Dashboard UI framework |
| `plotly` | Interactive charting |
| `flask` | Vercel serverless API layer |
| `loguru` | Structured logging with rotation |

---

## Makefile Reference

```bash
make install      # Install Python dependencies
make dashboard    # Launch the Streamlit dashboard
make test         # Run installation smoke test
make clean        # Remove generated output files
```

---

## Deployment

The repository includes a `vercel.json` and `api/index.py` for zero-configuration deployment to [Vercel](https://vercel.com/).

```bash
vercel deploy
```

---

## License

This project is licensed under the [MIT License](LICENSE).
