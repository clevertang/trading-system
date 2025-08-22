# Execution Package

This package handles order execution simulation and market timing.

## Components

### `simulator.py`
Realistic order execution simulation with market microstructure effects.

**Key Functions:**
- `execute_orders(orders, market_data, slippage_bps, min_liquidity_check)` - Simulate order fills

**Features:**
- Slippage modeling (basis points)
- Liquidity constraints
- Market hours validation
- Realistic execution timing

### `timing.py`
Market timing utilities for order scheduling and execution.

**Key Functions:**
- `find_execution_bar(df, date, time)` - Find closest available market bar
- `is_market_hours(timestamp)` - Check if timestamp is during market hours

## Usage

```python
from trading.execution.simulator import execute_orders
from trading.execution.timing import find_execution_bar

# Execute orders with 1bp slippage
executed = execute_orders(
    orders=strategy_orders,
    market_data=price_data,
    slippage_bps=1.0,
    min_liquidity_check=True
)

# Find execution time for specific date/time
execution_ts = find_execution_bar(data, target_date, "10:30")
```

## Execution Features

- **Slippage**: Configurable market impact in basis points
- **Liquidity Checks**: Validates order size against volume
- **Market Hours**: Ensures orders execute during trading hours
- **Timing**: Finds nearest available bar for execution

## Order Format

Expected order DataFrame columns:
- `time` - Intended execution timestamp
- `side` - "BUY" or "SELL"
- `qty` - Number of shares
- `price` - Intended execution price
- `value` - Total order value (negative for buys)