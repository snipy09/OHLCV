# 🚀 Quick Start Guide

## ⚡ 30-Second Setup (Recommended)

```bash
./run.sh full
```

That's it! This command:
1. Sets up the environment
2. Installs dependencies  
3. Runs the data pipeline
4. Launches the dashboard

---

## 📋 5-Minute Manual Setup

### Step 1: Install Dependencies
```bash
cd /Users/sajalmishra/Desktop/OHLCV
./setup.sh
```

Or manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Run the Pipeline
```bash
python main.py
```

**Expected Output:**
```
Starting OHLCV Data Validation & Monitoring System
Fetching data for ticker: AAPL
Validating data...
Cleaning data...
✓ AAPL processing complete
  Quality Score: 92.45/100 (GOOD)
```

### Step 3: Launch Dashboard
```bash
streamlit run dashboard/app.py
```

Open browser at `http://localhost:8501`

---

## 🎯 Available Commands

### Quick Start Options
| Command | What it does |
|---------|------------|
| `./run.sh full` | Complete workflow (setup + run + dashboard) |
| `./run.sh run` | Run pipeline only |
| `./run.sh dashboard` | Launch dashboard only |
| `make full` | Equivalent to `./run.sh full` |

### Individual Commands
| Command | Description |
|---------|------------|
| `./run.sh setup` | Install dependencies & setup environment |
| `./run.sh test` | Test installation |
| `./run.sh clean` | Clean cache files |
| `make install` | Install dependencies |
| `make clean` | Clean cache |

---

## ⚙️ Customization

### Change Tickers
Edit `src/config.py`:
```python
DEFAULT_TICKERS = ["TSLA", "META", "AMZN"]
```

### Change Data Period
Edit `src/config.py`:
```python
FETCH_PERIOD = "2y"  # 2 years of data
```

### Adjust Outlier Sensitivity
Edit `src/config.py`:
```python
OUTLIER_STD_THRESHOLD = 3.0  # More sensitive (3 sigma)
```

---

## Understanding Outputs

### Dashboard
- **Candlestick Chart**: Shows OHLCV with red X marks for outliers
- **Metrics Panel**: Quality score, outlier count, missing values
- **Data Table**: First/last 25 rows of dataset

### CSV Files
- `data/raw/AAPL_raw_*.csv`: Raw unprocessed data
- `data/clean/AAPL_clean_*.csv`: Cleaned data with outlier flags

### SQLite Database
- `ohlcv_data.db`: Contains all processed data
  - `raw_ohlcv` table: Raw data
  - `clean_ohlcv` table: Clean data + flags

### Logs
- `logs/ohlcv_*.log`: Complete execution log

---

## Quality Score Meaning

| Score | Rating | Status |
|-------|--------|--------|
| 95+ | 🟢 EXCELLENT | Production-ready |
| 80-94 | 🔵 GOOD | Acceptable |
| 60-79 | 🟠 WARNING | Needs attention |
| <60 | 🔴 CRITICAL | Not recommended |

---

## Common Issues & Solutions

**Issue**: `ModuleNotFoundError: No module named 'yfinance'`
- **Solution**: `pip install yfinance`

**Issue**: `Connection refused` in dashboard
- **Solution**: Make sure port 8501 is available, or use `streamlit run dashboard/app.py --server.port 8502`

**Issue**: "No data for ticker"
- **Solution**: Verify ticker exists at finance.yahoo.com (e.g., try AAPL)

---

## Next Steps

1. **Explore Data**
   - Use dashboard to visualize data
   - Check quality metrics

2. **Integrate Data**
   ```python
   from src.storage import OHLCVStorage
   storage = OHLCVStorage()
   data = storage.load_clean("AAPL")
   ```

3. **Extend System**
   - Add custom validation rules
   - Implement ML models
   - Build trading strategies

---

For detailed documentation, see [README.md](README.md)
