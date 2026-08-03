# 🎯 QUICK START - ONE COMMAND

## The Fastest Way to Run Everything

```bash
./run.sh full
```

That's it! This single command will:

1. ✅ Set up Python virtual environment
2. ✅ Install all dependencies
3. ✅ Test the installation
4. ✅ Run the complete data pipeline (fetch, validate, clean, analyze)
5. ✅ Launch the interactive dashboard

---

## What You'll See

```
═══════════════════════════════════════════════════════════
OHLCV Setup
═══════════════════════════════════════════════════════════

✓ Python 3.14.0 found
✓ Virtual environment created
✓ Virtual environment activated
✓ Dependencies installed
✓ All packages verified

═══════════════════════════════════════════════════════════
OHLCV Pipeline Execution
═══════════════════════════════════════════════════════════

✓ Running pipeline for AAPL
  [1/7] Fetching data...
  [2/7] Storing raw data...
  [3/7] Validating data...
  [4/7] Cleaning data...
  [5/7] Detecting outliers...
  [6/7] Processing corporate actions...
  [7/7] Storing clean data...
  Quality Score: 92.45/100 (GOOD)

... (similar for MSFT and GOOGL)

═══════════════════════════════════════════════════════════
OHLCV Dashboard
═══════════════════════════════════════════════════════════

  Local URL: http://localhost:8501
```

---

## Open the Dashboard

Your browser should automatically open to:

```
http://localhost:8501
```

If not, manually visit that URL to see:
- Live stock price charts
- Volume analysis
- Technical indicators (RSI, Moving Averages)
- Data quality metrics
- Outlier detection results

---

## Alternative Commands

If you want to run parts separately:

```bash
./run.sh setup              # Just setup (first time only)
./run.sh run                # Just run the pipeline
./run.sh dashboard          # Just launch the dashboard
./run.sh clean              # Clean up cache files
./run.sh help               # See all options
```

---

## Using Make

If you prefer Make commands:

```bash
make full                   # Same as ./run.sh full
make setup && make run      # Setup then run pipeline
make help                   # See all options
```

---

## Requirements

- Python 3.8+ (check with `python3 --version`)
- Internet connection (to fetch market data)
- ~500MB disk space

---

## Troubleshooting

### Python not installed?
```bash
brew install python3  # macOS
apt-get install python3  # Ubuntu/Linux
```

### Virtual environment issues?
```bash
rm -rf .venv
./run.sh full  # Try again
```

### Package import errors?
```bash
source .venv/bin/activate
pip install -q --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## What Gets Created

After running, you'll have:

```
data/
├── raw/             # Raw data from Yahoo Finance
│   ├── AAPL_raw_*.csv
│   ├── MSFT_raw_*.csv
│   └── GOOGL_raw_*.csv
└── clean/           # Cleaned and validated data
    ├── AAPL_clean_*.csv
    ├── MSFT_clean_*.csv
    └── GOOGL_clean_*.csv

logs/
└── ohlcv_*.log      # Execution logs

ohlcv_data.db        # SQLite database with all data
```

---

## Next Steps

1. **View Results** - Visit http://localhost:8501
2. **Check Logs** - `tail -f logs/ohlcv_*.log`
3. **Customize** - Edit `src/config.py` to change tickers or settings
4. **Schedule** - Set up cron job for automatic daily updates

---

## Documentation

For more detailed information:
- **README.md** - Complete documentation
- **MASTER_COMMANDS.md** - All available commands
- **QUICKSTART.md** - Detailed setup guide
- **PROJECT_POLISH.md** - Recent improvements

---

Ready? Just run:

```bash
./run.sh full
```

🚀 **Enjoy!**
