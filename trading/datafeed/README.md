# Datafeed Package

This package provides market data feed abstractions and implementations.

## Components

### `base.py`
Abstract base class defining the market data interface.

**Abstract Methods:**
- `history(symbol, start, end, interval)` - Fetch historical price data
- `last_price(symbol)` - Get current/last known price

**Data Format:**
Historical data returns pandas DataFrame with DatetimeIndex and columns:
- `Open`, `High`, `Low`, `Close`, `Volume`

### `yfinance_feed.py`
Yahoo Finance implementation of the market data feed interface.

## Usage

```python
from trading.datafeed.yfinance_feed import YFinanceFeed

feed = YFinanceFeed()
data = feed.history("AAPL", "2023-01-01", "2023-12-31")
timestamp, price = feed.last_price("AAPL")
```

## Interface Design

The abstract `MarketDataFeed` class allows strategies and backtests to swap data sources easily without code changes. This supports:
- Multiple data vendors (Yahoo Finance, Bloomberg, etc.)
- Different data frequencies (daily, intraday)
- Live vs historical data modes
- Testing with mock data feeds

## Extending

To add a new data source:
1. Inherit from `MarketDataFeed`
2. Implement `history()` and `last_price()` methods
3. Ensure data format matches the expected schema