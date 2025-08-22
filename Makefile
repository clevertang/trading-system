# Trading System Test Makefile

.PHONY: help test test-unit test-integration test-e2e test-coverage test-fast test-verbose install-test clean

# Default target
help:
	@echo "Available targets:"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"  
	@echo "  test-e2e       - Run end-to-end tests only"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  test-fast      - Run tests in parallel (fast)"
	@echo "  test-verbose   - Run tests with verbose output"
	@echo "  install-test   - Install test dependencies"
	@echo "  clean          - Clean test artifacts"

# Install all dependencies (including test dependencies)
install:
	pip install -r requirements.txt

# Install test dependencies (legacy - now same as install)
install-test: install

# Run all tests
test:
	pytest

# Run unit tests only
test-unit:
	pytest tests/unit/ -m "not slow"

# Run integration tests only  
test-integration:
	pytest tests/unit/ tests/e2e/ -m "not network"

# Run end-to-end tests only
test-e2e:
	pytest tests/e2e/

# Run tests with coverage
test-coverage:
	pytest --cov=trading --cov-report=html --cov-report=term-missing

# Run tests in parallel (faster)
test-fast:
	pytest -n auto

# Run tests with verbose output
test-verbose:
	pytest -vvv -s

# Run tests and generate HTML report
test-report:
	pytest --html=reports/test-report.html --self-contained-html

# Run specific test file
test-file:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make test-file FILE=path/to/test_file.py"; \
	else \
		pytest $(FILE) -v; \
	fi

# Run tests matching pattern
test-pattern:
	@if [ -z "$(PATTERN)" ]; then \
		echo "Usage: make test-pattern PATTERN='test_function_name'"; \
	else \
		pytest -k "$(PATTERN)" -v; \
	fi

# Clean test artifacts
clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf reports
	rm -rf .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Lint and type check (useful before running tests)
lint:
	flake8 trading/ tests/
	mypy trading/

# Format code
format:
	black trading/ tests/

# Run pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Full test suite with quality checks
test-all: lint test-coverage