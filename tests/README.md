# Trading System Test Suite

This directory contains comprehensive tests for the trading system, organized into unit tests and end-to-end integration tests.

## Test Structure

```
tests/
├── conftest.py              # Test fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── backtest/           # Backtest engine tests
│   ├── datafeed/           # Market data feed tests
│   ├── execution/          # Order execution tests
│   ├── risk/               # Risk management tests
│   ├── strategies/         # Trading strategy tests
│   └── utils/              # Utility function tests
└── e2e/                    # End-to-end integration tests
    ├── test_complete_trading_workflow.py
    └── test_data_pipeline.py
```

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
# Using pytest directly
pytest

# Using make (recommended)
make test

# Using the test runner script
python scripts/run_tests.py all
```

### Run Specific Test Suites

```bash
# Unit tests only
make test-unit
python scripts/run_tests.py unit

# End-to-end tests only
make test-e2e
python scripts/run_tests.py e2e

# Fast test subset (parallel execution)
make test-fast
python scripts/run_tests.py fast
```

### Run Tests with Coverage

```bash
make test-coverage
python scripts/run_tests.py coverage
```

## Test Categories

### Unit Tests

Unit tests verify individual components in isolation:

- **Backtest Engine** (`test_engine.py`): P&L calculation, position tracking, return metrics
- **Market Data** (`test_base.py`): Data feed interface contracts and validation
- **Risk Management** (`test_position_sizing.py`): Position sizing, margin requirements
- **Strategies** (`test_christmas_ladder.py`): Strategy logic, order generation
- **Execution** (`test_timing.py`): Market timing, execution bar finding
- **Utilities** (`test_calendar.py`): Trading calendar calculations

### End-to-End Tests

Integration tests verify complete workflows:

- **Complete Trading Workflow**: Full strategy execution from data to backtest results
- **Data Pipeline**: Data fetching, validation, error handling, and multi-symbol support

## Test Data and Fixtures

### Common Fixtures (conftest.py)

- `sample_market_data`: Realistic market data for testing
- `sample_orders`: Sample order DataFrame for backtest testing
- `christmas_params`: Christmas ladder strategy parameters

### Mock Data

Tests use realistic mock data with:
- Proper OHLCV format with DatetimeIndex
- Realistic price movements and volatility
- Trading day calendars (weekdays only)
- Volume and liquidity data

## Running Specific Tests

### By Test File

```bash
pytest tests/unit/backtest/test_engine.py -v
python scripts/run_tests.py --file tests/unit/backtest/test_engine.py
```

### By Test Pattern

```bash
pytest -k "test_position_sizing" -v
python scripts/run_tests.py --pattern "test_position_sizing"
```

### With Verbose Output

```bash
pytest -vvv -s
python scripts/run_tests.py --verbose
```

## Test Coverage

Generate coverage reports to ensure comprehensive test coverage:

```bash
# HTML coverage report
make test-coverage
open htmlcov/index.html

# Terminal coverage report
pytest --cov=trading --cov-report=term-missing
```

Target coverage goals:
- **Overall**: >85%
- **Critical components** (engine, strategies): >95%
- **Utilities**: >80%

## Test Performance

### Parallel Execution

Run tests in parallel for faster execution:

```bash
pytest -n auto  # Auto-detect CPU cores
make test-fast   # Uses parallel execution
```

### Test Duration Monitoring

Monitor slow tests:

```bash
pytest --durations=10  # Show 10 slowest tests
```

## Continuous Integration

Tests run automatically on:
- Pull requests to main branch
- Pushes to main/develop branches
- Multiple Python versions (3.9, 3.10, 3.11)

See `.github/workflows/tests.yml` for CI configuration.

## Writing New Tests

### Unit Test Guidelines

1. **Test one thing**: Each test should verify a single behavior
2. **Use descriptive names**: `test_calculate_position_size_with_max_constraint`
3. **Arrange-Act-Assert**: Clear test structure
4. **Use fixtures**: Leverage conftest.py fixtures for common test data
5. **Mock external dependencies**: Don't depend on network or file system

### Integration Test Guidelines

1. **Test realistic scenarios**: Use complete, realistic workflows
2. **Include error cases**: Test failure modes and recovery
3. **Validate end-to-end behavior**: Verify complete system interactions
4. **Performance considerations**: Mark slow tests appropriately

### Example Unit Test

```python
def test_calculate_position_size_basic():
    """Test basic position size calculation."""
    shares = calculate_position_size(
        available_cash=10000,
        target_allocation=5000,
        current_price=100.0,
        max_position_pct=0.5
    )
    
    assert shares == 50  # 5000 / 100
```

### Example Integration Test

```python
def test_complete_strategy_workflow(sample_market_data):
    """Test complete strategy execution workflow."""
    # 1. Setup
    params = XmasParams(year=2023, symbol="TEST")
    
    # 2. Generate orders
    orders = generate_orders(sample_market_data, 10000, params)
    
    # 3. Execute and validate
    results = run_backtest(orders, 10000)
    assert results["initial_cash"] == 10000
```

## Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.slow
def test_large_dataset():
    """Test that takes a long time."""
    pass

@pytest.mark.network
def test_api_connection():
    """Test requiring network access."""
    pass
```

Run specific markers:

```bash
pytest -m "not slow"      # Skip slow tests
pytest -m "network"       # Run only network tests
```

## Debugging Tests

### Run Single Test with Debug

```bash
pytest tests/unit/backtest/test_engine.py::TestBacktestEngine::test_pnl_calculation -vvv -s --pdb
```

### Common Debugging Tips

1. **Use print statements**: Add temporary debug output
2. **Pytest debugging**: Use `--pdb` flag to drop into debugger on failure
3. **Isolated execution**: Run single tests to isolate issues
4. **Check fixtures**: Verify test data is as expected

## Test Maintenance

### Regular Tasks

1. **Update test data**: Keep mock data realistic and current
2. **Review coverage**: Identify and test uncovered code paths
3. **Performance monitoring**: Track and optimize slow tests
4. **Dependency updates**: Keep test dependencies current

### Best Practices

1. **Green CI**: Keep all tests passing
2. **Fast feedback**: Optimize for quick test execution
3. **Reliable tests**: Avoid flaky or intermittent failures
4. **Comprehensive coverage**: Test both success and failure paths