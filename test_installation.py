"""
Test Script: Verify OHLCV System Installation

Run this to verify all components are installed and working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test all module imports"""
    print("Testing imports...")

    test_modules = [
        ("config", "Configuration"),
        ("utils", "Utilities"),
        ("fetcher", "Data Fetcher"),
        ("validator", "Data Validator"),
        ("cleaner", "Data Cleaner"),
        ("outlier", "Outlier Detector"),
        ("corporate_actions", "Corporate Actions"),
        ("storage", "Storage"),
    ]

    failed = []

    for module_name, display_name in test_modules:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name} ({module_name})")
        except Exception as e:
            print(f"  ✗ {display_name} ({module_name}): {str(e)}")
            failed.append(module_name)

    return len(failed) == 0, failed


def test_dependencies():
    """Test external dependencies"""
    print("\nTesting dependencies...")

    dependencies = [
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("yfinance", "yfinance"),
        ("plotly", "Plotly"),
        ("streamlit", "Streamlit"),
        ("loguru", "Loguru"),
    ]

    failed = []

    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except ImportError:
            print(f"  ✗ {display_name} - Not installed")
            failed.append(display_name)

    return len(failed) == 0, failed


def test_directories():
    """Test project directories exist"""
    print("\nTesting directories...")

    directories = [
        ("data/raw", "Raw data directory"),
        ("data/clean", "Clean data directory"),
        ("logs", "Logs directory"),
        ("src", "Source code directory"),
        ("dashboard", "Dashboard directory"),
    ]

    failed = []

    base_path = Path(__file__).parent

    for rel_path, display_name in directories:
        dir_path = base_path / rel_path
        if dir_path.exists() and dir_path.is_dir():
            print(f"  ✓ {display_name}")
        else:
            print(f"  ✗ {display_name} - Not found")
            failed.append(rel_path)

    return len(failed) == 0, failed


def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")

    try:
        from config import (
            DEFAULT_TICKERS,
            FETCH_PERIOD,
            RETRY_ATTEMPTS,
            OUTLIER_STD_THRESHOLD,
            RAW_DATA_DIR,
            CLEAN_DATA_DIR,
            LOGS_DIR
        )

        print(f"  ✓ Configuration loaded")
        print(f"    - Default Tickers: {DEFAULT_TICKERS}")
        print(f"    - Fetch Period: {FETCH_PERIOD}")
        print(f"    - Retry Attempts: {RETRY_ATTEMPTS}")
        print(f"    - Outlier Threshold: {OUTLIER_STD_THRESHOLD}σ")

        return True, []
    except Exception as e:
        print(f"  ✗ Configuration error: {str(e)}")
        return False, ["configuration"]


def test_classes():
    """Test class instantiation"""
    print("\nTesting class instantiation...")

    failed = []

    try:
        from fetcher import OHLCVFetcher
        fetcher = OHLCVFetcher()
        print(f"  ✓ OHLCVFetcher instantiated")
    except Exception as e:
        print(f"  ✗ OHLCVFetcher: {str(e)}")
        failed.append("OHLCVFetcher")

    try:
        from validator import OHLCVValidator
        validator = OHLCVValidator()
        print(f"  ✓ OHLCVValidator instantiated")
    except Exception as e:
        print(f"  ✗ OHLCVValidator: {str(e)}")
        failed.append("OHLCVValidator")

    try:
        from cleaner import OHLCVCleaner
        cleaner = OHLCVCleaner()
        print(f"  ✓ OHLCVCleaner instantiated")
    except Exception as e:
        print(f"  ✗ OHLCVCleaner: {str(e)}")
        failed.append("OHLCVCleaner")

    try:
        from outlier import OutlierDetector
        detector = OutlierDetector()
        print(f"  ✓ OutlierDetector instantiated")
    except Exception as e:
        print(f"  ✗ OutlierDetector: {str(e)}")
        failed.append("OutlierDetector")

    try:
        from storage import OHLCVStorage
        storage = OHLCVStorage()
        print(f"  ✓ OHLCVStorage instantiated")
    except Exception as e:
        print(f"  ✗ OHLCVStorage: {str(e)}")
        failed.append("OHLCVStorage")

    return len(failed) == 0, failed


def test_database():
    """Test database initialization"""
    print("\nTesting database...")

    try:
        from storage import OHLCVStorage
        from config import DB_PATH

        storage = OHLCVStorage()

        if DB_PATH.exists():
            print(f"  ✓ Database created at {DB_PATH}")
        else:
            print(f"  ✗ Database not found at {DB_PATH}")
            return False, ["database_file"]

        # Try to query
        tickers = storage.get_available_tickers()
        print(f"  ✓ Database accessible")
        print(f"    - Available tickers: {len(tickers)}")

        return True, []
    except Exception as e:
        print(f"  ✗ Database error: {str(e)}")
        return False, ["database"]


def main():
    """Run all tests"""
    print("="*60)
    print("OHLCV System Installation Test")
    print("="*60)
    print("")

    results = {}

    # Run tests
    results["imports"], failed_imports = test_imports()
    results["dependencies"], failed_deps = test_dependencies()
    results["directories"], failed_dirs = test_directories()
    results["configuration"], failed_config = test_configuration()
    results["classes"], failed_classes = test_classes()
    results["database"], failed_db = test_database()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    print("="*60)

    if all_passed:
        print("\n✅ All tests passed!")
        print("\nNext steps:")
        print("  1. Run the example: python example.py")
        print("  2. Run the pipeline: python main.py")
        print("  3. Launch dashboard: streamlit run dashboard/app.py")
        return 0
    else:
        print("\n❌ Some tests failed!")
        print("\nFailed components:")
        all_failed = []
        if failed_imports:
            all_failed.extend([f"  - Module: {m}" for m in failed_imports])
        if failed_deps:
            all_failed.extend([f"  - Dependency: {d}" for d in failed_deps])
        if failed_dirs:
            all_failed.extend([f"  - Directory: {d}" for d in failed_dirs])
        if failed_classes:
            all_failed.extend([f"  - Class: {c}" for c in failed_classes])

        for item in all_failed:
            print(item)

        print("\nTroubleshooting:")
        print("  1. Check Python version: python --version (requires 3.10+)")
        print("  2. Reinstall dependencies: pip install -r requirements.txt")
        print("  3. Check directory permissions: ls -la")

        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
