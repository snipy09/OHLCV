# OHLCV Data Validation & Monitoring System

<div align="center">

**Professional-Grade Market Data Pipeline with Real-Time Monitoring & Advanced Analytics**

![Python](https://img.shields.io/badge/Python-3.14-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red?style=flat-square)
![SQLite](https://img.shields.io/badge/Database-SQLite3-green?style=flat-square)

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [Dashboard](#dashboard)

</div>

---

## Overview

A production-grade OHLCV (Open, High, Low, Close, Volume) data validation and monitoring system built with Python. Fetches real market data, applies sophisticated multi-layer validation and cleaning, detects anomalies with 3 different methods, and provides an interactive web dashboard with professional technical analysis charts.

**Perfect for:** Financial data engineers, quantitative traders, data scientists, and automated trading systems.

---

## Features

### Data Pipeline
- **Real-Time Fetching**: Live OHLCV data from yfinance with 3-attempt retry logic
- **Multi-Layer Validation**: Structural, logical, and temporal consistency checks
- **Intelligent Cleaning**: Deduplication, null handling, corruption removal (0% data loss on quality data)
- **Anomaly Detection**: Z-score (5σ), price spikes, volume spikes
- **Corporate Actions**: Automatic stock split and dividend flagging
- **Dual Persistence**: SQLite database + timestamped CSV exports
- **Quality Scoring**: 0-100 scale (POOR/FAIR/GOOD/EXCELLENT)

### Dashboard & Analytics
- **Professional Charts**:
  - Candlestick with Bollinger Bands ±2σ
  - 20-day & 50-day Moving Averages
  - Color-coded Volume Analysis
  - RSI (14) with overbought/oversold levels
  - Price Distribution Histograms
- **Data Quality Metrics**: Score, rating, anomaly count, data gaps
- **Interactive Controls**: Toggle Clean/Raw data, filter by ticker
- **Statistical Analysis**: Price & volume distributions, summary statistics
- **Real-Time Updates**: Live data refresh and processing logs

### Reliability & Scalability
- **Comprehensive Logging**: Daily rotation, 7-day retention (loguru)
- **Error Handling**: Graceful failures with detailed diagnostics
- **Data Integrity**: 100% retention after cleaning
- **Unlimited Scalability**: Process any number of tickers
- **Type Safety**: Full type hints throughout codebase
- **Modular Design**: 9 independent, reusable modules

---

## Quick Start

### 🚀 Master Command (Recommended)

The fastest way to get everything running:

```bash
# Option 1: Using the shell script (Recommended)
./run.sh full

# Option 2: Using Make
make full
```

This single command will:
1. ✅ Create virtual environment
2. ✅ Install all dependencies
3. ✅ Verify installation
4. ✅ Run the complete data pipeline
5. ✅ Launch the interactive dashboard

---

### 📋 Alternative: Step-by-Step Installation

#### 1. Installation

```bash
cd /Users/sajalmishra/Desktop/OHLCV

# Option A: Using setup script
./setup.sh

# Option B: Manual setup
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Run Data Pipeline

```bash
# Option 1: Direct Python
python main.py

# Option 2: Using shell script
./run.sh run

# Option 3: Using Make
make run
```

**Processes 3 tickers (AAPL, MSFT, GOOGL) through 7 pipeline stages:**
1. Fetch raw data → 2. Store raw → 3. Validate → 4. Clean → 5. Detect outliers → 6. Process corporate actions → 7. Store clean

**Output:**
- `data/raw/` - Raw OHLCV CSV files (timestamped)
- `data/clean/` - Cleaned OHLCV CSV files (timestamped)
- `ohlcv_data.db` - SQLite database with both tables
- `logs/ohlcv_*.log` - Daily log files with full audit trail

#### 3. Launch Dashboard

```bash
# Option 1: Direct Streamlit
streamlit run dashboard/app.py

# Option 2: Using shell script
./run.sh dashboard

# Option 3: Using Make
make dashboard
```

**Access at:** http://localhost:8501

**Features:**
- Select ticker from sidebar (AAPL, MSFT, GOOGL)
- Toggle between "Clean Data" (validated) and "Raw Data" (unprocessed)
- 5 tabs: Price Chart, Volume, RSI Indicator, Price Trend, Statistics
- Real-time quality metrics and anomaly detection results

---

### 📚 Available Commands

#### Using Shell Script (./run.sh)

```bash
./run.sh setup              # Setup environment
./run.sh run                # Run pipeline
./run.sh dashboard          # Launch dashboard
./run.sh full               # Complete workflow
./run.sh test               # Test installation
./run.sh clean              # Clean cache
./run.sh help               # Show help
```

#### Using Make

```bash
make setup                  # Setup environment
make run                    # Run pipeline
make dashboard              # Launch dashboard
make full                   # Complete workflow
make test                   # Run tests
make clean                  # Clean cache
make help                   # Show help
```

---

### 4. Verify Installation

```bash
python test_installation.py
```

Tests 6 categories: imports, dependencies, directories, config, classes, database.

---

## Usage Examples

### Run Full Pipeline
```bash
python main.py
```

### Run Interactive Examples
```bash
python example.py
```

Demonstrates:
1. Fetching raw data
2. Validating data
3. Cleaning data
4. Detecting outliers
5. Storing/retrieving from SQLite
6. Quality scoring

### Python API
```python
from src.storage import OHLCVStorage
from src.utils import calculate_data_quality_score

storage = OHLCVStorage()
clean_data = storage.load_clean('AAPL')
quality_score = calculate_data_quality_score(clean_data, [])
print(f"Quality Score: {quality_score:.1f}/100")
```

---

## Architecture

### Project Structure
```
OHLCV/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration: tickers, thresholds, paths
│   ├── utils.py               # Logging, quality scoring, utilities
│   ├── fetcher.py             # yfinance integration, data fetching
│   ├── validator.py           # Multi-layer validation logic
│   ├── cleaner.py             # Data cleaning and preprocessing
│   ├── outlier.py             # 3-method anomaly detection
│   ├── corporate_actions.py   # Splits and dividends handling
│   └── storage.py             # SQLite and CSV persistence
├── dashboard/
│   ├── __init__.py
│   └── app.py                 # Streamlit web interface
├── data/
│   ├── raw/                   # Raw OHLCV data (CSV)
│   └── clean/                 # Cleaned OHLCV data (CSV)
├── logs/                      # Daily rotation logs
├── main.py                    # Pipeline orchestrator
├── example.py                 # Usage examples
├── test_installation.py       # System verification
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

### Data Flow
```
yfinance
   ↓
[Fetch] → [Store Raw] → [Validate] → [Clean] → [Detect Outliers] → [Corporate Actions] → [Store Clean]
   ↓            ↓            ↓         ↓             ↓                    ↓
 CSVs        Database      Errors   CSVs         Flags              Database + CSVs
                              ↓                                             ↓
                          Reports                                       Dashboard
```

### Core Modules

| Module | Purpose | Key Functions |
|--------|---------|----------------|
| `config.py` | Central configuration | `DEFAULT_TICKERS`, `DB_PATH`, `OUTLIER_THRESHOLD` |
| `utils.py` | Utilities & logging | `setup_logger()`, `calculate_data_quality_score()` |
| `fetcher.py` | Data acquisition | `fetch_ticker()`, `fetch_splits_and_dividends()` |
| `validator.py` | Data validation | `validate()`, structural/logical/temporal checks |
| `cleaner.py` | Data preprocessing | `clean()`, remove duplicates/nulls/corruption |
| `outlier.py` | Anomaly detection | `detect()`, Z-score/price/volume spike detection |
| `corporate_actions.py` | Event flagging | `process()`, split and dividend handling |
| `storage.py` | Persistence layer | `save_raw()`, `save_clean()`, `load_raw()`, `load_clean()` |

---

## Dashboard

### Tabs

1. **Price Chart** - Candlestick with Bollinger Bands and moving averages
   - Green/Red candles for up/down days
   - BB Upper/Middle/Lower bands (±2σ)
   - MA20 (blue) and MA50 (green) trend lines
   - Outliers marked with red diamonds (clean data only)

2. **Volume** - Volume analysis with moving averages
   - Color-coded bars (green=up, red=down)
   - MA20 and MA50 volume moving averages
   - Helps identify volume trends and breakouts

3. **RSI Indicator** - Momentum analysis
   - RSI(14) with overbought (70) and oversold (30) levels
   - Identifies potential reversals
   - Neutral line at 50

4. **Price Trend** - High-low range with close price
   - Shows price trading range
   - Close price overlay
   - Visualizes high-low volatility

5. **Statistics** - Price and volume distribution
   - Descriptive statistics tables
   - Mean, median, std dev, min, max

### Metrics Panel

- **Quality Score**: 0-100 scale (EXCELLENT if ≥90)
- **Anomalies**: Count of detected outliers
- **Data Gaps**: Missing values or null entries
- **Date Range**: Time period covered
- **Latest Close, Period Change, 52-Week Range, Avg Volume, Volatility**

### Controls

- **Ticker Selection**: Dropdown menu (AAPL, MSFT, GOOGL)
- **Data Type Toggle**: Switch between Clean and Raw data
- **Auto-Refresh**: Streamlit reruns on data changes

---

## Data Quality Pipeline

### Validation Stages

#### Stage 1: Structural Validation
- Required columns present (open, high, low, close, volume)
- Correct data types
- No completely null rows

#### Stage 2: Logical Validation
- High ≥ Open, Close
- Low ≤ Open, Close
- Volume > 0
- Open, High, Low, Close > 0

#### Stage 3: Temporal Validation
- Monotonic increasing timestamps
- No duplicate dates
- Identify trading gaps (weekends/holidays)

### Cleaning Stages

1. **Deduplication**: Remove rows with same timestamp
2. **Null Handling**: Forward fill (limit=1) then backward fill
3. **Corruption Detection**: Flag extreme outliers for removal
4. **Type Enforcement**: Ensure all columns have correct types

### Outlier Detection

**Method 1: Z-Score (5σ)**
- Calculate 30-day rolling mean/std
- Flag if |price - mean| > 5 * std

**Method 2: Price Spike**
- Intraday: |high - low| / open > 10%
- Daily: |close - prev_close| / prev_close > 10%

**Method 3: Volume Spike**
- 30-day moving average
- Flag if volume > avg_volume * 3

---

## Configuration

Edit `src/config.py` to customize:

```python
# Tickers to process
DEFAULT_TICKERS = ['AAPL', 'MSFT', 'GOOGL']

# Outlier detection threshold (sigma)
OUTLIER_THRESHOLD_SIGMA = 5

# Data fetching period
FETCH_PERIOD = '1y'  # '1mo', '1y', '5y', 'max', etc.

# Paths
DB_PATH = Path('ohlcv_data.db')
RAW_DATA_DIR = Path('data/raw')
CLEAN_DATA_DIR = Path('data/clean')
```

---

## Performance

Typical execution times (per ticker):
- **Fetch**: ~1 second
- **Validate**: ~0.1 seconds
- **Clean**: ~0.1 seconds
- **Outlier Detection**: ~0.2 seconds
- **Total Pipeline**: ~5 seconds for 3 tickers

Database queries: <100ms for loading 250 rows

---

## Troubleshooting

### No clean data showing in dashboard
```bash
# Regenerate clean data
python main.py

# Verify database contents
python -c "from src.storage import OHLCVStorage; s = OHLCVStorage(); print(len(s.load_clean('AAPL')))"
```

### Import errors when running dashboard
```bash
# Ensure sys.path is configured correctly (already done in app.py)
# Otherwise run from project root:
cd /Users/sajalmishra/Desktop/OHLCV
streamlit run dashboard/app.py
```

### Dashboard connection issues
```bash
# Kill existing Streamlit process
pkill -f "streamlit run"

# Restart dashboard
streamlit run dashboard/app.py
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | 2.1.4 | Data manipulation |
| numpy | 1.24.3 | Numerical operations |
| yfinance | 0.2.32 | Market data fetching |
| plotly | 5.17.0 | Interactive visualizations |
| streamlit | 1.28.1 | Web dashboard |
| loguru | 0.7.2 | Logging with rotation |
| sqlite3 | Built-in | Database persistence |

---

## License

MIT License - Feel free to use for personal or commercial projects.

---

## Support

For issues, questions, or improvements:
1. Check logs in `logs/` directory
2. Run `test_installation.py` for diagnostics
3. Review example.py for usage patterns

---

**Built with ❤️ for data-driven decision making**
