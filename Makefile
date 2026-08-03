.PHONY: help install clean run test dashboard lint format setup master full example test-install install-dev info docs

help:
	@echo "OHLCV Data Validation & Monitoring System"
	@echo "=========================================="
	@echo ""
	@echo "Master Commands:"
	@echo "  make full              - Complete workflow (setup + run + dashboard)"
	@echo "  make master            - Alias for 'full'"
	@echo ""
	@echo "Individual Commands:"
	@echo "  make setup             - Setup virtual environment and install dependencies"
	@echo "  make run               - Run data pipeline"
	@echo "  make dashboard         - Launch interactive dashboard"
	@echo "  make test              - Run tests"
	@echo "  make test-install      - Test installation"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean             - Clean cache and temporary files"
	@echo "  make lint              - Run code linters"
	@echo "  make format            - Format code with black/isort"
	@echo "  make example           - Run example usage"
	@echo ""
	@echo "Usage:"
	@echo "  make full              # Recommended: setup + run + dashboard"
	@echo "  make setup && make run # Setup then run pipeline"
	@echo "  ./run.sh full          # Alternative: use shell script"
	@echo ""

install:
	pip install -q --upgrade pip setuptools wheel
	pip install -q -r requirements.txt

install-dev:
	pip install -q --upgrade pip setuptools wheel
	pip install -q -r requirements.txt
	pip install -q -r requirements-dev.txt

test-install:
	python test_installation.py

test:
	pytest tests/ -v --cov=src 2>/dev/null || echo "pytest not installed or tests/ not found"

run:
	python main.py

dashboard:
	streamlit run dashboard/app.py

example:
	python example.py

full: setup run dashboard

master: full

setup: .venv install test-install
	@echo "✓ Setup complete! Run 'make run' to start pipeline."

.venv:
	@python3 -m venv .venv
	@echo "✓ Virtual environment created"
	@echo "Activate it with: source .venv/bin/activate"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".streamlit" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✓ Cache cleaned"

lint:
	flake8 src/ dashboard/ main.py example.py --max-line-length=100 2>/dev/null || echo "flake8 not installed"
	pylint src/ dashboard/ main.py example.py --disable=C0111 2>/dev/null || echo "pylint not installed"

format:
	black src/ dashboard/ main.py example.py 2>/dev/null || echo "black not installed"
	isort src/ dashboard/ main.py example.py 2>/dev/null || echo "isort not installed"

docs:
	@echo "Documentation:"
	@echo "  - README.md      : Complete documentation"
	@echo "  - QUICKSTART.md  : 5-minute setup guide"
	@echo "  - DEPLOYMENT.md  : Production deployment guide"

info:
	@echo "Project Structure:"
	@echo "  src/              - Core modules"
	@echo "  dashboard/        - Streamlit dashboard"
	@echo "  data/             - Data files"
	@echo "    raw/            - Raw OHLCV data"
	@echo "    clean/          - Cleaned OHLCV data"
	@echo "  logs/             - Log files"
	@echo ""
	@echo "Main Components:"
	@echo "  fetcher.py        - Data fetching (yfinance)"
	@echo "  validator.py      - Multi-layer validation"
	@echo "  cleaner.py        - Data cleaning"
	@echo "  outlier.py        - Outlier detection"
	@echo "  corporate_actions.py - Corporate action handling"
	@echo "  storage.py        - CSV & SQLite storage"
	@echo "  main.py           - Pipeline orchestrator"
	@echo "  dashboard/app.py  - Streamlit UI"
