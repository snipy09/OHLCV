# Master Commands Guide

## 🚀 Quick Reference

The fastest way to run the entire system:

```bash
# Using shell script (Recommended)
./run.sh full

# Using Make
make full
```

Both commands execute the complete workflow:
1. **Setup** - Create virtual environment and install dependencies
2. **Run** - Execute the data pipeline (fetch, validate, clean, detect outliers)
3. **Dashboard** - Launch the interactive Streamlit dashboard

---

## 📖 Detailed Command Reference

### Shell Script (`./run.sh`)

The shell script is the primary interface with comprehensive features and error handling.

#### Master Commands

| Command | Purpose | Time |
|---------|---------|------|
| `./run.sh full` | Complete workflow (setup + run + dashboard) | ~2-3 min |
| `./run.sh setup` | Setup environment only | ~30 sec |
| `./run.sh run` | Run pipeline only | ~1-2 min |
| `./run.sh dashboard` | Launch dashboard only | Runs until stopped |

#### Utility Commands

| Command | Purpose |
|---------|---------|
| `./run.sh test` | Verify installation |
| `./run.sh clean` | Remove cache and temporary files |
| `./run.sh help` | Show help message |

---

### Make Commands

Alternative interface using GNU Make.

#### Master Commands

```bash
make full       # Complete workflow (recommended)
make master     # Alias for 'full'
```

#### Setup & Installation

```bash
make setup              # Setup environment
make install            # Install dependencies only
make install-dev        # Install dev dependencies
make test-install       # Test installation
```

#### Pipeline & Dashboard

```bash
make run                # Run data pipeline
make dashboard          # Launch dashboard
make example            # Run example usage
```

#### Maintenance

```bash
make clean              # Clean cache files
make lint               # Run linters
make format             # Format code
make help               # Show help
make info               # Show project structure
make docs               # Show documentation
```

---

## 🎯 Usage Examples

### Complete Workflow (All-in-One)

```bash
# Using shell script
./run.sh full

# Using Make
make full
```

**What happens:**
1. Creates `.venv/` directory
2. Installs all packages from `requirements.txt`
3. Verifies all imports work
4. Runs data pipeline for AAPL, MSFT, GOOGL
5. Launches Streamlit dashboard at http://localhost:8501

---

### Step-by-Step Workflow

```bash
# Step 1: Setup (one time)
./run.sh setup
# or: make setup

# Step 2: Run pipeline
./run.sh run
# or: make run

# Step 3: View results in dashboard
./run.sh dashboard
# or: make dashboard
```

---

### Development Workflow

```bash
# Setup with dev dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Run linters
make lint

# Clean cache
make clean
```

---

## 📊 Output Files

After running the pipeline, you'll find:

```
OHLCV/
├── data/
│   ├── raw/                    # Raw CSV files
│   │   ├── AAPL_raw_*.csv
│   │   ├── MSFT_raw_*.csv
│   │   └── GOOGL_raw_*.csv
│   └── clean/                  # Cleaned CSV files
│       ├── AAPL_clean_*.csv
│       ├── MSFT_clean_*.csv
│       └── GOOGL_clean_*.csv
├── logs/                       # Log files
│   └── ohlcv_*.log
└── ohlcv_data.db              # SQLite database
```

---

## 🔧 Configuration

### Change Tickers

Edit `src/config.py`:

```python
DEFAULT_TICKERS = ["TSLA", "META", "AMZN"]
```

Then run:
```bash
./run.sh run  # or make run
```

### Change Data Period

Edit `src/config.py`:

```python
FETCH_PERIOD = "2y"  # 2 years of data
```

### Adjust Outlier Detection

Edit `src/config.py`:

```python
OUTLIER_STD_THRESHOLD = 5.0    # 5 standard deviations
OUTLIER_WINDOW = 30             # 30-day rolling window
```

---

## 🐛 Troubleshooting

### Issue: "Python not found"

**Solution:**
```bash
python3 --version  # Verify Python 3 is installed
brew install python3  # macOS
```

### Issue: "Virtual environment activation fails"

**Solution:**
```bash
rm -rf .venv
./run.sh setup  # Recreate from scratch
```

### Issue: "Package import errors"

**Solution:**
```bash
source .venv/bin/activate
pip install -q --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Issue: "Dashboard won't start"

**Solution:**
```bash
pip install --upgrade streamlit
streamlit run dashboard/app.py --logger.level=debug
```

---

## 📋 Requirements

- **Python 3.8+**
- **pip** (package manager)
- **Internet connection** (for fetching market data)
- **~500MB disk space** (for data and environment)

---

## 🎓 What Each Command Does

### `./run.sh full` Breakdown

```
1. check_python
   └─ Verify Python 3 is installed

2. check_venv / create .venv
   └─ Create virtual environment if needed

3. activate_venv
   └─ Activate .venv for dependency isolation

4. install_dependencies
   └─ pip install -r requirements.txt

5. verify_installation
   └─ Test all imports work

6. run_pipeline (main.py)
   ├─ Fetch real market data from Yahoo Finance
   ├─ Validate data quality
   ├─ Clean and normalize data
   ├─ Detect statistical outliers
   ├─ Process corporate actions
   ├─ Save results to CSV & SQLite
   └─ Generate quality metrics

7. launch_dashboard (streamlit)
   ├─ Start Streamlit server
   ├─ Open interactive web UI
   └─ Display real-time analytics
```

---

## 📚 Additional Resources

- **README.md** - Complete project documentation
- **QUICKSTART.md** - 5-minute setup guide
- **DEPLOYMENT.md** - Production deployment guide
- **ARCHITECTURE.py** - System architecture details
- **SYSTEM_STATUS.md** - Current system status

---

## 🎯 Quick Decision Tree

```
Do you want to...

├─ Run everything?
│  └─ ./run.sh full
│
├─ Just setup the environment?
│  └─ ./run.sh setup
│
├─ Just run the pipeline?
│  └─ ./run.sh run
│
├─ Just launch the dashboard?
│  └─ ./run.sh dashboard
│
├─ Clean up cache files?
│  └─ ./run.sh clean
│
└─ Need help?
   └─ ./run.sh help
```

---

## 🚀 Performance Notes

- **First run**: ~2-3 minutes (includes setup)
- **Subsequent runs**: ~1-2 minutes (pipeline only)
- **Dashboard startup**: ~5-10 seconds
- **Data processing**: ~30-60 seconds per ticker

---

## ✅ Verification

After running `./run.sh full`, verify everything works:

```bash
# Check log files
tail -f logs/ohlcv_*.log

# Check data was created
ls -lah data/raw/
ls -lah data/clean/

# Verify database
sqlite3 ohlcv_data.db ".tables"

# Check dashboard is running
# Open: http://localhost:8501
```

---

*Last Updated: April 20, 2026*
