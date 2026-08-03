# 📊 Live OHLCV Data Validation & Monitoring System

A production-grade Python system for fetching, validating, cleaning, analyzing, and visualizing OHLCV (Open, High, Low, Close, Volume) market data with comprehensive error detection, outlier identification, and corporate action tracking.

---

## 🎯 Features

### Data Fetching
- **Real-time data** from Yahoo Finance using yfinance
- **Multi-ticker support** for batch processing
- **Automatic retry logic** (3 attempts) with configurable delays
- **Error handling** for network failures and invalid tickers

### Data Validation (Multi-Layer)
- **Structural Checks**: Column presence, null values, data types
- **Logical Checks**: High/Low vs Open/Close relationships, positive volumes
- **Temporal Checks**: Missing dates, duplicate timestamps, date sequences
- **Detailed Error Reporting**: Categorized errors and warnings

### Data Cleaning
- **Duplicate Removal**: Timestamp-based duplicate elimination
- **Missing Value Handling**: Forward fill with limits + backward fill
- **Corruption Detection**: Removal of severely corrupted rows
- **Type Enforcement**: Automatic data type correction
- **Comprehensive Logging**: All cleaning actions tracked

### Outlier Detection
- **Rolling Statistics**: 30-day rolling mean/std calculations
- **Multiple Methods**:
  - Z-score analysis (5-sigma threshold)
  - Intraday price movement detection
  - Volume spike detection
- **Non-destructive**: Outliers marked, not deleted
- **Detailed Reporting**: Breakdown by detection method

### Corporate Actions
- **Split Handling**: Detection and flagging of stock splits
- **Dividend Processing**: Dividend event tracking
- **Event Flagging**: Dedicated column for marking events
- **Historical Tracking**: All corporate actions preserved

### Storage
- **Dual Format Storage**:
  - CSV files (timestamped, versioned)
  - SQLite database (queryable, indexed)
- **Raw & Clean Separation**: Maintains data lineage
- **Version Control**: Automatic timestamped versioning

### Monitoring Dashboard
- **Interactive Visualizations**: Candlestick charts with Plotly
- **Real-time Data Selection**: Toggle between raw/clean data
- **Quality Metrics**: Data quality scoring (0-100)
- **Outlier Highlighting**: Visual markers on charts
- **Corporate Events Display**: Timeline of corporate actions
- **Data Preview**: Table view of processed data

### Quality Metrics
- **Comprehensive Scoring**: 0-100 scale
  - Excellent: 95+
  - Good: 80-94
  - Warning: 60-79
  - Critical: <60
- **Multi-Factor Analysis**: Nulls, errors, outliers combined
- **Rating System**: EXCELLENT/GOOD/WARNING/CRITICAL

---

## 🏗️ Architecture

```
ohlcv-validator/
│
├── data/
│   ├── raw/              # Raw OHLCV CSV files (timestamped)
│   └── clean/            # Cleaned OHLCV CSV files (timestamped)
│
├── logs/
│   └── ohlcv_*.log       # Structured logs with rotation
│
├── src/
│   ├── config.py         # Configuration & constants
│   ├── utils.py          # Utility functions
│   ├── fetcher.py        # Data fetching (yfinance)
│   ├── validator.py      # Multi-layer validation
│   ├── cleaner.py        # Data cleaning
│   ├── outlier.py        # Outlier detection
│   ├── corporate_actions.py  # Corporate action handling
│   └── storage.py        # CSV & SQLite storage
│
├── dashboard/
│   └── app.py            # Streamlit dashboard
│
├── ohlcv_data.db         # SQLite database (auto-created)
├── main.py               # Pipeline orchestrator
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 📋 Pipeline Flow

```
1. FETCH DATA
   ↓ (Retry: 3 attempts)
2. STORE RAW
   ├─ CSV (data/raw/)
   └─ SQLite (raw_ohlcv table)
   ↓
3. VALIDATE
   ├─ Structural checks
   ├─ Logical checks
   └─ Temporal checks
   ↓
4. CLEAN
   ├─ Remove duplicates
   ├─ Handle missing values
   ├─ Drop corrupted rows
   └─ Enforce types
   ↓
5. DETECT OUTLIERS
   ├─ Rolling std (z-score)
   ├─ Price spikes
   └─ Volume spikes
   ↓
6. CORPORATE ACTIONS
   ├─ Fetch splits & dividends
   └─ Flag events
   ↓
7. STORE CLEAN
   ├─ CSV (data/clean/)
   └─ SQLite (clean_ohlcv table)
   ↓
8. QUALITY SCORING & REPORTING
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- pip or conda

### Setup

```bash
# 1. Navigate to project directory
cd ohlcv-validator

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 💻 Usage

### Running the Pipeline

```bash
# Run for default tickers (AAPL, MSFT, GOOGL)
python main.py

# Or customize in src/config.py
# Modify DEFAULT_TICKERS = ["YOUR_TICKERS"]
```

**Output Example:**
```
2024-01-15 10:30:45 | INFO | Starting OHLCV Data Validation & Monitoring System
2024-01-15 10:30:45 | INFO | Fetching data for ticker: AAPL
2024-01-15 10:30:47 | INFO | Successfully fetched 252 rows for AAPL
2024-01-15 10:30:47 | INFO | Starting validation for AAPL
2024-01-15 10:30:47 | INFO | Validation passed for AAPL: No errors or warnings
2024-01-15 10:30:47 | INFO | Starting data cleaning for AAPL
2024-01-15 10:30:47 | INFO | Cleaning completed for AAPL: Removed 0 rows (0.00%)
2024-01-15 10:30:47 | INFO | Starting outlier detection for AAPL
2024-01-15 10:30:47 | INFO | Detected 3 outliers for AAPL (1.19%)
2024-01-15 10:30:47 | INFO | Processing corporate actions for AAPL
2024-01-15 10:30:48 | INFO | Corporate actions for AAPL: 0 splits, 1 dividends
2024-01-15 10:30:48 | INFO | Saving clean data for AAPL

✓ AAPL processing complete
  Quality Score: 92.45/100 (GOOD)
  Final rows: 252
```

### Launching the Dashboard

```bash
# Run Streamlit dashboard
streamlit run dashboard/app.py

# Opens at http://localhost:8501
```

**Dashboard Features:**
- 📊 Interactive candlestick charts
- 🎯 Outlier visualization
- 📋 Data preview table
- 📈 Quality metrics
- 🔄 Toggle raw/clean data
- 🎛️ Ticker selection
- 📌 Corporate action timeline

---

## ⚙️ Configuration

Edit `src/config.py` to customize:

```python
# Data fetching
FETCH_PERIOD = "1y"          # Default: 1 year
FETCH_INTERVAL = "1d"        # Default: daily
RETRY_ATTEMPTS = 3           # Default: 3 retries

# Validation
NULL_THRESHOLD = 0.5         # 50% null tolerance

# Outlier detection
OUTLIER_STD_THRESHOLD = 5.0  # 5 sigma
OUTLIER_WINDOW = 30          # 30-day window

# Logging
LOG_LEVEL = "INFO"           # Can be DEBUG, INFO, WARNING, ERROR

# Default tickers
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL"]

# Quality score thresholds
QUALITY_SCORE_EXCELLENT = 95
QUALITY_SCORE_GOOD = 80
QUALITY_SCORE_WARNING = 60
```

---

## 📊 Data Quality Scoring

Quality score calculated from:
- **Null Values** (50% weight): Penalizes missing data
- **Validation Errors** (40% weight): Logical/structural issues
- **Outliers** (20% weight): Extreme values

```
Score = 100 - (null_pct * 50) - (error_count * 2) - (outlier_pct * 20)
```

**Ratings:**
- 🟢 **EXCELLENT** (95+): Production-ready
- 🔵 **GOOD** (80-94): Acceptable with minor issues
- 🟠 **WARNING** (60-79): Requires attention
- 🔴 **CRITICAL** (<60): Not recommended for analysis

---

## 📁 Output Files

### CSV Storage
```
data/
├── raw/
│   ├── AAPL_raw_20240115_103045.csv
│   ├── MSFT_raw_20240115_103045.csv
│   └── GOOGL_raw_20240115_103045.csv
│
└── clean/
    ├── AAPL_clean_20240115_103045.csv
    ├── MSFT_clean_20240115_103045.csv
    └── GOOGL_clean_20240115_103045.csv
```

### SQLite Database
```
ohlcv_data.db
├── raw_ohlcv
│   ├── ticker (TEXT)
│   ├── date (TIMESTAMP)
│   ├── open, high, low, close (REAL)
│   └── volume (INTEGER)
│
└── clean_ohlcv
    ├── ticker (TEXT)
    ├── date (TIMESTAMP)
    ├── open, high, low, close (REAL)
    ├── volume (INTEGER)
    ├── is_outlier (BOOLEAN)
    └── corporate_action_flag (TEXT)
```

### Logs
```
logs/
└── ohlcv_20240115_103045.log
```

---

## 🔍 Validation Rules

### Structural
- ✓ All required columns present (open, high, low, close, volume)
- ✓ No excessive null values (default: >50%)
- ✓ Correct data types (numeric for OHLCV)

### Logical
- ✓ High ≥ max(Open, Close)
- ✓ Low ≤ min(Open, Close)
- ✓ Volume ≥ 0
- ✓ Prices > 0

### Temporal
- ✓ No duplicate timestamps
- ✓ Chronological ordering
- ✓ Reasonable date gaps (allows weekends)

---

## 🎯 Outlier Detection Methods

1. **Rolling Standard Deviation**
   - Z-score > 5 standard deviations
   - Detects extreme price moves relative to history

2. **Intraday Movement**
   - Extreme high-low range
   - 2x the 99th percentile threshold

3. **Volume Spike**
   - Volume > 5x the 30-day moving average
   - Unusual trading activity

---

## 🛠️ Advanced Usage

### Custom Tickers
```python
from src.config import DEFAULT_TICKERS
from main import OHLCVPipeline

# Process specific tickers
pipeline = OHLCVPipeline(tickers=["TSLA", "META", "AMZN"])
results = pipeline.run()
```

### Load Historical Data
```python
from src.storage import OHLCVStorage

storage = OHLCVStorage()

# Load from database
clean_data = storage.load_clean("AAPL")
raw_data = storage.load_raw("AAPL")

# Get available tickers
tickers = storage.get_available_tickers()
```

### Manual Validation
```python
from src.validator import OHLCVValidator
import pandas as pd

validator = OHLCVValidator()
df = pd.read_csv("data.csv")

cleaned_df, errors = validator.validate(df, ticker="TEST")
print(errors)
```

---

## 📈 Example Output

### Pipeline Summary
```
============================================================
PIPELINE SUMMARY
============================================================
Total tickers processed: 3
Successful: 3
Failed: 0

✓ AAPL: SUCCESS
  Quality: GOOD (92.45/100)
  Final rows: 252

✓ MSFT: SUCCESS
  Quality: EXCELLENT (97.80/100)
  Final rows: 252

✓ GOOGL: SUCCESS
  Quality: GOOD (85.30/100)
  Final rows: 251
```

---

## 🐛 Troubleshooting

### Issue: "No data returned from yfinance"
- **Solution**: Check internet connection and ticker validity
- **Debug**: Verify ticker works at finance.yahoo.com

### Issue: "SQLite database locked"
- **Solution**: Close other connections to database
- **Debug**: Check if dashboard is running

### Issue: "Memory error with large datasets"
- **Solution**: Process fewer tickers or shorter periods
- **Config**: Modify `FETCH_PERIOD` in config.py

### Issue: "Missing dependencies"
- **Solution**: `pip install --upgrade -r requirements.txt`

---

## 📚 API Reference

### OHLCVFetcher
```python
fetcher = OHLCVFetcher(period="1y", interval="1d")
data = fetcher.fetch_ticker("AAPL")
data_dict = fetcher.fetch_multiple(["AAPL", "MSFT"])
splits, dividends = fetcher.fetch_splits_and_dividends("AAPL")
```

### OHLCVValidator
```python
validator = OHLCVValidator()
df, errors = validator.validate(df, ticker="AAPL")
```

### OHLCVCleaner
```python
cleaner = OHLCVCleaner()
df, report = cleaner.clean(df, ticker="AAPL")
```

### OutlierDetector
```python
detector = OutlierDetector(std_threshold=5.0, window=30)
df, report = detector.detect(df, ticker="AAPL")
```

### OHLCVStorage
```python
storage = OHLCVStorage()
storage.save_raw(df, "AAPL")
storage.save_clean(df, "AAPL")
df = storage.load_clean("AAPL")
tickers = storage.get_available_tickers()
```

---

## 🔐 Data Privacy & Compliance

- ✓ Uses public Yahoo Finance data only
- ✓ No sensitive data transmission
- ✓ Local storage (no cloud upload)
- ✓ Audit logs for all operations
- ✓ Configurable retention policies

---

## 📊 Sample Dashboard Views

### Candlestick Chart with Outliers
```
[Chart showing candlestick data with red X markers for outliers]
- Green: Up days
- Red: Down days
- Red X: Outlier days
- Blue bars: Volume
```

### Quality Dashboard
```
┌─────────────────────────────────────┐
│ Data Quality Analysis               │
├─────────────────────────────────────┤
│ Quality Score: 92.45/100            │
│ Rating: GOOD                        │
│ Clean Data: 98.5%                   │
│ Price Range: $150.25 - $195.85      │
└─────────────────────────────────────┘
```

---

## 🤝 Contributing

To extend the system:
1. Add new validation rules in `src/validator.py`
2. Add new cleaning steps in `src/cleaner.py`
3. Add new detection methods in `src/outlier.py`
4. Add new dashboard components in `dashboard/app.py`

---

## 📝 License

MIT License - Free to use and modify

---

## 🙋 Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs in `logs/` directory
3. Ensure all dependencies installed
4. Verify data is available for ticker

---

## 📅 Changelog

### v1.0.0 (2024-01-15)
- ✅ Complete OHLCV validation pipeline
- ✅ Multi-layer validation engine
- ✅ Outlier detection system
- ✅ Corporate actions handling
- ✅ Streamlit dashboard
- ✅ SQLite + CSV storage
- ✅ Quality scoring system
- ✅ Comprehensive logging

---

**Built with ❤️ for quantitative traders and data engineers**
