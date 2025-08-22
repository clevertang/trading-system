# Backtest Package

This package provides backtesting functionality for trading strategies.

## Components

### `engine.py`
Core backtesting engine that processes orders and calculates performance metrics.

**Key Functions:**
- `run_backtest(orders, initial_cash)` - Executes backtest given order list and starting capital

**Features:**
- Position tracking (bought vs sold shares)
- P&L calculation including unrealized gains
- Return percentage calculation
- Cash flow management

### `metrics.py`
Performance metrics and analysis utilities for backtest results.

## Usage

```python
from trading.backtest.engine import run_backtest
import pandas as pd

# Generate orders from your strategy
orders = pd.DataFrame([...])

# Run backtest
results = run_backtest(orders, initial_cash=10000)
print(f"Return: {results['return_pct']:.2%}")
```

## Output Format

The backtest engine returns a dictionary with:
- `orders` - Original order DataFrame
- `initial_cash` - Starting cash amount
- `ending_cash` - Final cash position
- `remaining_shares` - Unsold shares
- `remaining_value_mark` - Mark-to-market value of remaining shares
- `pnl` - Profit and loss
- `return_pct` - Return percentage