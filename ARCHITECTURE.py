"""
Architecture Visualization and System Diagram
OHLCV Data Validation & Monitoring System
"""

ARCHITECTURE = """
╔════════════════════════════════════════════════════════════════════════════╗
║        OHLCV Data Validation & Monitoring System - Architecture           ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW PIPELINE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  Yahoo Finance   │
    │   (yfinance)     │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────────────┐
    │   DATA FETCHER           │  • Multi-ticker support
    │   (fetcher.py)           │  • Retry logic (3x)
    │                          │  • Error handling
    └────────┬─────────────────┘
             │
    ┌────────▼──────────┐
    │   RAW DATA        │
    │   Storage         │
    │ (CSV + SQLite)    │
    └─────────────────┬─┘
                      │
                      ▼
    ┌─────────────────────────┐
    │   VALIDATOR             │  • Structural checks
    │   (validator.py)        │  • Logical checks
    │                         │  • Temporal checks
    └─────────────────┬───────┘
                      │
                      ▼
    ┌─────────────────────────┐
    │   CLEANER               │  • Remove duplicates
    │   (cleaner.py)          │  • Handle missing values
    │                         │  • Drop corruption
    └─────────────────┬───────┘
                      │
                      ▼
    ┌─────────────────────────┐
    │   OUTLIER DETECTOR      │  • Z-score (5-sigma)
    │   (outlier.py)          │  • Price spikes
    │                         │  • Volume spikes
    └─────────────────┬───────┘
                      │
                      ▼
    ┌─────────────────────────┐
    │   CORPORATE ACTIONS     │  • Stock splits
    │   (corporate_actions.py)│  • Dividends
    │                         │  • Event flagging
    └─────────────────┬───────┘
                      │
                      ▼
    ┌──────────────────────────┐
    │   CLEAN DATA STORAGE     │  • CSV + SQLite
    │   (storage.py)           │  • Timestamped files
    │                          │  • Indexed database
    └────────┬────────────────┬┘
             │                │
    ┌────────▼──┐    ┌────────▼──────────┐
    │ CSV Files │    │  SQLite Database  │
    │(data/clean)    │  (ohlcv_data.db)  │
    └────────────┘    └───────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODULE ARCHITECTURE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────┐
    │                    CORE MODULES (src/)                          │
    │                                                                  │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
    │  │ Fetcher  │  │Validator │  │ Cleaner  │  │ Outlier  │       │
    │  │          │  │          │  │          │  │ Detector │       │
    │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
    │                                                                  │
    │  ┌────────────────────┐  ┌───────────────────────────┐         │
    │  │  Corporate Actions │  │ Storage (CSV + SQLite)    │         │
    │  │                    │  │                           │         │
    │  └────────────────────┘  └───────────────────────────┘         │
    │                                                                  │
    │  ┌──────────────────────────────────────────────────────┐      │
    │  │  Utilities (validation, logging, quality scoring)    │      │
    │  │  Configuration (constants, paths, defaults)          │      │
    │  └──────────────────────────────────────────────────────┘      │
    │                                                                  │
    └─────────────────────────────────────────────────────────────────┘
                                   ▲
                    ┌──────────────┴──────────────┐
                    │                             │
        ┌───────────▼──────────┐    ┌────────────▼──────────┐
        │   PIPELINE (main.py) │    │ DASHBOARD (app.py)    │
        │                      │    │                       │
        │ • Orchestrates all   │    │ • Streamlit UI        │
        │   modules            │    │ • Plotly charts       │
        │ • Batch processing   │    │ • Quality metrics     │
        │ • Summary reporting  │    │ • Data preview        │
        │ • Quality scoring    │    │ • Interactive select  │
        └──────────────────────┘    └───────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                      VALIDATION LAYERS                                       │
└─────────────────────────────────────────────────────────────────────────────┘

    STRUCTURAL VALIDATION
    │
    ├─ Required columns present?
    ├─ Correct data types?
    ├─ Null values within threshold?
    └─ Column count correct?
                    │
                    ▼
    LOGICAL VALIDATION
    │
    ├─ High >= max(Open, Close)?
    ├─ Low <= min(Open, Close)?
    ├─ Volume >= 0?
    └─ Prices > 0?
                    │
                    ▼
    TEMPORAL VALIDATION
    │
    ├─ No duplicate timestamps?
    ├─ Chronological order?
    ├─ Reasonable date gaps?
    └─ Timezone consistency?


┌─────────────────────────────────────────────────────────────────────────────┐
│                    OUTLIER DETECTION METHODS                                │
└─────────────────────────────────────────────────────────────────────────────┘

    METHOD 1: Rolling Z-Score
    ┌─ 30-day rolling window
    ├─ Calculate mean & std
    ├─ Z-score = (value - mean) / std
    └─ Flag if |Z-score| > 5.0

    METHOD 2: Intraday Price Movement
    ┌─ Calculate (High - Low) / Open
    ├─ Find 99th percentile threshold
    └─ Flag if move > 2x threshold

    METHOD 3: Volume Spikes
    ┌─ Calculate 30-day volume MA
    ├─ Calculate volume ratio
    └─ Flag if ratio > 5.0


┌─────────────────────────────────────────────────────────────────────────────┐
│                    QUALITY SCORE CALCULATION                                │
└─────────────────────────────────────────────────────────────────────────────┘

    BASE SCORE: 100.0
            │
            ├─ (Null % × 50) ─────┐
            │                       ├─ Subtract
            ├─ (Error Count × 2) ──┤  from score
            │                       │
            ├─ (Outlier % × 20) ───┤
            │                       │
            └─ (Other factors) ────┘
                      │
                      ▼
            FINAL SCORE (0-100)
                      │
            ┌─────────┼─────────┐
            │         │         │
            ▼         ▼         ▼
        95+ (🟢)  80-94 (🔵)  60-79 (🟠)  <60 (🔴)
        EXCELLENT  GOOD      WARNING   CRITICAL


┌─────────────────────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA                                         │
└─────────────────────────────────────────────────────────────────────────────┘

    TABLE: raw_ohlcv
    ┌─────────────────────────┐
    │ ticker     | TEXT       │  ← Ticker symbol
    │ date       | TIMESTAMP  │  ← Date (PK)
    │ open       | REAL       │  ← Opening price
    │ high       | REAL       │  ← High price
    │ low        | REAL       │  ← Low price
    │ close      | REAL       │  ← Closing price
    │ volume     | INTEGER    │  ← Trading volume
    └─────────────────────────┘

    TABLE: clean_ohlcv
    ┌──────────────────────────────┐
    │ ticker              | TEXT   │
    │ date                | TIMESTAMP│
    │ open, high, low     | REAL   │
    │ close               | REAL   │
    │ volume              | INTEGER│
    │ is_outlier          | BOOLEAN│  ← Outlier flag
    │ corporate_action_flag | TEXT │  ← Event info
    └──────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                    LOGGING STRUCTURE                                         │
└─────────────────────────────────────────────────────────────────────────────┘

    TIMESTAMP | LEVEL | MODULE:FUNCTION:LINE | MESSAGE
    ───────────────────────────────────────────────────────────
    2024-01-15 10:30:45 | INFO | fetcher:fetch_ticker:42 | Fetching AAPL
    2024-01-15 10:30:47 | INFO | fetcher:fetch_ticker:52 | Fetched 252 rows
    2024-01-15 10:30:47 | INFO | validator:validate:85 | Starting validation
    2024-01-15 10:30:48 | WARN | validator:_check_logic:120 | Violation: ...
    2024-01-15 10:30:49 | INFO | cleaner:clean:45 | Removed 2 duplicates
    2024-01-15 10:30:50 | INFO | outlier:detect:112 | Found 3 outliers
    2024-01-15 10:30:51 | INFO | storage:save_clean:200 | Data saved

    Files: logs/ohlcv_*.log (auto-rotated at 500MB)


┌─────────────────────────────────────────────────────────────────────────────┐
│                    DASHBOARD COMPONENTS                                      │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │ STREAMLIT DASHBOARD                                         │
    ├─────────────────────────────────────────────────────────────┤
    │                                                              │
    │ [SIDEBAR]                                                   │
    │ • Ticker selector      ──┐                                  │
    │ • Data source toggle   ──┼─────────────────────────┐        │
    │ • Outlier highlight    ──┘                          │        │
    │ • Refresh button                                   │        │
    │                                                    │        │
    │ [MAIN AREA]                                        │        │
    │ ┌──────────────────────────────────────────┐      │        │
    │ │ METRICS (4 columns)                      │◄─────┤        │
    │ │ • Total Candles                          │      │        │
    │ │ • Outliers                               │      │        │
    │ │ • Missing Values                         │      │        │
    │ │ • Corporate Actions                      │      │        │
    │ └──────────────────────────────────────────┘      │        │
    │                                                    │        │
    │ ┌──────────────────────────────────────────┐      │        │
    │ │ CANDLESTICK CHART (Plotly)               │◄─────┤        │
    │ │ • Green/Red candles                      │      │        │
    │ │ • Red X markers (outliers)               │      │        │
    │ │ • Volume bars                            │      │        │
    │ │ • Zoom & pan                             │      │        │
    │ └──────────────────────────────────────────┘      │        │
    │                                                    │        │
    │ ┌──────────────────────────────────────────┐      │        │
    │ │ QUALITY PANEL                            │      │        │
    │ │ • Quality Score (0-100)                  │      │        │
    │ │ • Rating badge                           │      │        │
    │ │ • Clean data %                           │      │        │
    │ │ • Price range                            │      │        │
    │ └──────────────────────────────────────────┘      │        │
    │                                                    │        │
    │ ┌──────────────────────────────────────────┐      │        │
    │ │ ERROR REPORT (expandable)                │      │        │
    │ │ • Validation errors                      │      │        │
    │ │ • Warnings                               │      │        │
    │ └──────────────────────────────────────────┘      │        │
    │                                                    │        │
    │ ┌──────────────────────────────────────────┐      │        │
    │ │ OUTLIER ANALYSIS                         │      │        │
    │ │ • Outlier count & %                      │      │        │
    │ │ • Outlier dates (expandable)             │      │        │
    │ └──────────────────────────────────────────┘      │        │
    │                                                    │        │
    │ ┌──────────────────────────────────────────┐      │        │
    │ │ CORPORATE ACTIONS TIMELINE               │      │        │
    │ │ • Split events                           │      │        │
    │ │ • Dividend events                        │      │        │
    │ └──────────────────────────────────────────┘      │        │
    │                                                    │        │
    │ ┌──────────────────────────────────────────┐      │        │
    │ │ DATA PREVIEW TABLE                       │◄─────┘        │
    │ │ • First 25 rows (if > 50)                │               │
    │ │ • Last 25 rows (if > 50)                 │               │
    │ │ • Formatted prices & volumes             │               │
    │ └──────────────────────────────────────────┘               │
    │                                                             │
    │ [FOOTER]                                                   │
    │ • Date range                                               │
    │ • Record count                                             │
    │ • Last updated timestamp                                   │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘

"""

USAGE_FLOW = """
╔════════════════════════════════════════════════════════════════════════════╗
║                         TYPICAL USAGE FLOW                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

    USER ACTION                      SYSTEM RESPONSE
    ────────────────────────────────────────────────────

    1. Install Dependencies
    $ pip install -r requirements.txt
                                    → Installs all packages

    2. Run Installation Test
    $ python test_installation.py
                                    → Verifies setup
                                    → Reports status

    3. Run Pipeline
    $ python main.py
                                    ├─ Fetches OHLCV data
                                    ├─ Validates structure/logic/temporal
                                    ├─ Cleans duplicates/nulls/corruption
                                    ├─ Detects outliers (3 methods)
                                    ├─ Processes corporate actions
                                    ├─ Stores raw & clean data
                                    ├─ Calculates quality scores
                                    └─ Prints summary

    4. View Dashboard
    $ streamlit run dashboard/app.py
                                    ├─ Opens at http://localhost:8501
                                    ├─ User selects ticker
                                    ├─ Dashboard displays:
                                    │  ├─ Metrics
                                    │  ├─ Candlestick chart
                                    │  ├─ Quality score
                                    │  ├─ Outliers
                                    │  ├─ Corporate actions
                                    │  └─ Data table
                                    └─ User can interact with controls

    5. Integrate into Code
    from src.storage import OHLCVStorage
    storage = OHLCVStorage()
    data = storage.load_clean("AAPL")
                                    → Gets clean data
                                    → Ready for analysis

"""

if __name__ == "__main__":
    print(ARCHITECTURE)
    print("\n\n")
    print(USAGE_FLOW)
