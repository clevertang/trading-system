# Trading System

A comprehensive Python trading system with backtesting capabilities, risk management, and strategy implementation framework.

## Features

- **Backtesting Engine**: Complete P&L calculation and performance metrics
- **Market Data Integration**: Yahoo Finance data feed with extensible interface
- **Risk Management**: Position sizing and margin requirement validation
- **Strategy Framework**: Extensible strategy implementation (Christmas ladder included)
- **Execution Simulation**: Realistic order execution with slippage and timing
- **Comprehensive Testing**: 50+ unit tests and end-to-end integration tests

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd trading-system

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run with coverage
make test-coverage

# Using test runner script
python scripts/run_tests.py all
```

### Basic Usage

```python
from trading.strategies.christmas_ladder import generate_orders, XmasParams
from trading.backtest.engine import run_backtest
from trading.datafeed.yfinance_feed import YFinanceFeed

# Setup data feed
feed = YFinanceFeed()
data = feed.history("AAPL", "2023-01-01", "2023-12-31")

# Configure strategy
params = XmasParams(year=2023, symbol="AAPL", buy_days=5, sell_days=10)

# Generate orders
orders = generate_orders(data, cash=50000, p=params)

# Run backtest
results = run_backtest(orders, initial_cash=50000)
print(f"Return: {results['return_pct']:.2%}")
```

## Project Structure

```
trading-system/
├── trading/                 # Main package
│   ├── backtest/           # Backtesting engine
│   ├── datafeed/           # Market data feeds
│   ├── execution/          # Order execution simulation
│   ├── risk/               # Risk management
│   ├── strategies/         # Trading strategies
│   └── utils/              # Utility functions
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── e2e/                # End-to-end tests
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── requirements.txt        # Dependencies
```

## Dependencies

### Core Dependencies
- **pandas** (>=2.0.0): Data manipulation and analysis
- **numpy** (>=1.20.0): Numerical computing  
- **yfinance** (>=0.2.0): Yahoo Finance market data

### Testing & Development
- **pytest**: Testing framework with coverage and parallel execution
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking

See [REQUIREMENTS.md](REQUIREMENTS.md) for detailed dependency information.

## Package Documentation

Each package includes detailed documentation:

- [Backtest Package](trading/backtest/README.md) - Backtesting engine and metrics
- [Datafeed Package](trading/datafeed/README.md) - Market data interfaces
- [Execution Package](trading/execution/README.md) - Order execution simulation  
- [Risk Package](trading/risk/README.md) - Position sizing and risk management
- [Strategies Package](trading/strategies/README.md) - Trading strategy framework
- [Utils Package](trading/utils/README.md) - Utility functions

## Testing

The project includes comprehensive test coverage:

- **54 unit tests** covering all components
- **End-to-end integration tests** for complete workflows
- **Realistic mock data** with proper market calendars
- **Coverage reporting** and performance benchmarks

See [tests/README.md](tests/README.md) for detailed testing information.

## Available Commands

### Using Makefile
```bash
make install          # Install dependencies
make test            # Run all tests  
make test-unit       # Run unit tests only
make test-coverage   # Run tests with coverage
make test-fast       # Run tests in parallel
make lint            # Run code linting
make format          # Format code with black
make clean           # Clean test artifacts
```

### Using Test Runner
```bash
python scripts/run_tests.py unit        # Unit tests
python scripts/run_tests.py e2e         # End-to-end tests
python scripts/run_tests.py coverage    # With coverage
python scripts/run_tests.py --verbose   # Verbose output
```

## Strategy Implementation

The system provides a flexible framework for implementing trading strategies:

```python
from dataclasses import dataclass
import pandas as pd

@dataclass
class MyStrategyParams:
    symbol: str
    # ... other parameters

def generate_orders(df: pd.DataFrame, cash: float, params: MyStrategyParams) -> pd.DataFrame:
    """Generate orders for your strategy."""
    orders = []
    # ... implement your strategy logic
    return pd.DataFrame(orders)
```

See the [Christmas ladder strategy](trading/strategies/christmas_ladder.py) for a complete example.

## Risk Management

The system includes built-in risk management:

```python
from trading.risk.position_sizing import calculate_position_size, check_margin_requirements

# Calculate appropriate position size
shares = calculate_position_size(
    available_cash=100000,
    target_allocation=10000,
    current_price=150.0,
    max_position_pct=0.05  # 5% max position
)

# Validate margin requirements
margin_ok = check_margin_requirements(orders, available_cash=50000)
```

## Contributing

1. **Install development dependencies**: `pip install -r requirements.txt`
2. **Run tests**: `make test` 
3. **Format code**: `make format`
4. **Run linting**: `make lint`
5. **Add tests** for new functionality
6. **Update documentation** as needed

## Performance

- **Fast test execution**: Parallel testing with pytest-xdist
- **Efficient data processing**: Vectorized operations with pandas/numpy
- **Minimal dependencies**: Core system requires only pandas, numpy, yfinance
- **Scalable architecture**: Modular design for easy extension

## License

[Add your license information here]

## Support

For issues, questions, or contributions:
- Check existing [documentation](docs/)
- Run the test suite to verify installation
- Review [package documentation](trading/) for usage examples