# Strategies Package

This package contains trading strategy implementations.

## Components

### `christmas_ladder.py`
Christmas ladder strategy implementation.

**Strategy Logic:**
- **Accumulation Phase**: Buy equal notional amounts on last N trading days before Dec 25
- **Distribution Phase**: Sell 1/Nth of position each trading day after Dec 25
- **Execution**: Buys at close, sells at specified time (default 10:30 AM)

**Parameters (`XmasParams`):**
- `year` - Target year for strategy
- `symbol` - Stock symbol to trade
- `buy_days` - Number of accumulation days (default: 5)
- `sell_days` - Number of distribution days (default: 10)
- `sell_execution_time` - Time of day for sales (default: "10:30")

## Usage

```python
from trading.strategies.christmas_ladder import generate_orders, XmasParams

# Configure strategy parameters
params = XmasParams(
    year=2023,
    symbol="AAPL",
    buy_days=5,
    sell_days=10,
    sell_execution_time="10:30"
)

# Generate orders
orders = generate_orders(
    df=price_data,
    cash=10000,
    p=params
)
```

## Strategy Framework

All strategies should implement:
- **Parameter Class**: Dataclass with strategy configuration
- **Generate Orders Function**: Takes market data and cash, returns order DataFrame
- **Standard Order Format**: time, side, qty, price, value columns

## Adding New Strategies

1. Create new strategy file in this package
2. Define parameter dataclass with strategy settings
3. Implement `generate_orders(df, cash, params)` function
4. Return orders in standard DataFrame format
5. Add documentation and usage examples

## Order Format

Generated orders must include columns:
- `time` - Execution timestamp
- `side` - "BUY" or "SELL"  
- `qty` - Number of shares (integer)
- `price` - Execution price
- `value` - Total value (negative for buys, positive for sells)