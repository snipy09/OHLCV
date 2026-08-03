#!/bin/bash

###############################################################################
# OHLCV Data Validation & Monitoring System - Master Run Script
#
# This is the comprehensive master command for running the entire OHLCV pipeline
# and dashboard. It handles setup, validation, data processing, and dashboard launch.
###############################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
}

check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        print_info "Creating virtual environment at $VENV_PATH..."
        python3 -m venv "$VENV_PATH"
        print_success "Virtual environment created"
    else
        print_success "Virtual environment exists"
    fi
}

activate_venv() {
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
        print_success "Virtual environment activated"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi
}

install_dependencies() {
    if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_info "Installing dependencies..."
    pip install -q --upgrade pip setuptools wheel
    pip install -q -r "$PROJECT_ROOT/requirements.txt"
    print_success "Dependencies installed"
}

verify_installation() {
    print_info "Verifying Python packages..."
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
    "$VENV_PATH/bin/python" << 'EOF'
import sys
packages = ['pandas', 'numpy', 'yfinance', 'plotly', 'streamlit', 'loguru']
try:
    for pkg in packages:
        __import__(pkg)
    print("✓ All required packages verified", file=sys.stderr)
except ImportError as e:
    print(f"✗ Missing package: {e}", file=sys.stderr)
    sys.exit(1)
EOF
    print_success "All packages verified"
}

run_pipeline() {
    print_info "Running OHLCV data pipeline..."
    cd "$PROJECT_ROOT"
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
    "$VENV_PATH/bin/python" main.py
    print_success "Pipeline execution completed"
}

launch_dashboard() {
    print_info "Launching Streamlit dashboard..."
    print_info "Dashboard will open at http://localhost:8501"
    print_info "Press Ctrl+C to stop the dashboard\n"
    cd "$PROJECT_ROOT"
    streamlit run dashboard/app.py
}

test_installation() {
    print_info "Testing installation..."
    cd "$PROJECT_ROOT"
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
    "$VENV_PATH/bin/python" test_installation.py
    print_success "Installation test passed"
}

show_help() {
    cat << EOF
${BLUE}OHLCV Data Validation & Monitoring System - Master Run Script${NC}

${YELLOW}USAGE:${NC}
    ./run.sh [COMMAND]

${YELLOW}COMMANDS:${NC}
    setup           Install dependencies and create virtual environment
    run             Run the complete data pipeline (fetch, validate, clean, analyze)
    dashboard       Launch the interactive Streamlit dashboard
    full            Run complete workflow (setup + pipeline + dashboard)
    test            Run installation tests
    clean           Remove cache files and logs
    help            Show this help message

${YELLOW}EXAMPLES:${NC}
    ./run.sh setup              # Setup environment first time
    ./run.sh run                # Process OHLCV data
    ./run.sh dashboard          # Launch dashboard
    ./run.sh full               # Complete workflow (recommended)

${YELLOW}QUICK START:${NC}
    ./run.sh full

${YELLOW}REQUIREMENTS:${NC}
    • Python 3.8+
    • pip
    • Internet connection (for data fetching)

${YELLOW}OUTPUT FILES:${NC}
    • data/raw/     - Raw OHLCV CSV files
    • data/clean/   - Cleaned OHLCV CSV files
    • logs/         - Pipeline execution logs
    • ohlcv_data.db - SQLite database

EOF
}

###############################################################################
# Main Script
###############################################################################

main() {
    # Default to 'help' if no argument provided
    COMMAND="${1:-help}"

    case "$COMMAND" in
        setup)
            print_header "OHLCV Setup"
            check_python
            check_venv
            activate_venv
            install_dependencies
            verify_installation
            test_installation
            print_header "✓ Setup Complete"
            echo -e "Next step: Run ${BLUE}./run.sh run${NC} to process data"
            ;;

        run)
            print_header "OHLCV Pipeline Execution"
            check_python
            check_venv
            activate_venv
            run_pipeline
            print_header "✓ Pipeline Complete"
            echo -e "Next step: Run ${BLUE}./run.sh dashboard${NC} to view results"
            ;;

        dashboard)
            print_header "OHLCV Dashboard"
            check_python
            check_venv
            activate_venv
            launch_dashboard
            ;;

        full)
            print_header "OHLCV Complete Workflow"
            check_python
            check_venv
            activate_venv
            install_dependencies
            verify_installation
            test_installation
            run_pipeline
            print_header "Starting Dashboard"
            launch_dashboard
            ;;

        test)
            print_header "Testing Installation"
            check_python
            check_venv
            activate_venv
            test_installation
            print_success "All tests passed"
            ;;

        clean)
            print_header "Cleaning Project"
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
            find . -type f -name "*.pyc" -delete
            find . -type f -name ".DS_Store" -delete
            rm -rf "$PROJECT_ROOT/.streamlit/cache" 2>/dev/null || true
            print_success "Cache cleaned"
            ;;

        help|--help|-h)
            show_help
            ;;

        *)
            print_error "Unknown command: $COMMAND"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
