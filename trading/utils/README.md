# Utils Package

This package provides utility functions for trading operations.

## Components

### `calendar.py`
Trading calendar and date manipulation utilities.

**Key Functions:**
- `get_trading_days_around_date(df, anchor_date, before_days, after_days)` - Find trading days around a reference date

## Usage

```python
from trading.utils.calendar import get_trading_days_around_date
import pandas as pd

# Get trading days around Christmas
xmas = pd.Timestamp(year=2023, month=12, day=25)
pre_dates, post_dates = get_trading_days_around_date(
    df=market_data,
    anchor_date=xmas,
    before_days=5,
    after_days=10
)
```

## Calendar Features

### Trading Day Calculation
- **Data-Driven**: Uses actual market data to determine trading days
- **Holiday Awareness**: Automatically excludes non-trading days
- **Year Filtering**: Works within specific year boundaries
- **Flexible Windows**: Configurable before/after day counts

### Date Handling
- Requires DatetimeIndex on input DataFrame
- Returns DatetimeIndex for easy integration
- Handles missing data gracefully
- Sorts and deduplicates dates

## Integration

Calendar utilities are commonly used by:
- **Strategies**: Finding execution dates around events (earnings, holidays)
- **Backtesting**: Ensuring realistic trading schedules
- **Risk Management**: Calculating position holding periods
- **Execution**: Scheduling order timing

## Error Handling

The functions validate:
- DataFrame has DatetimeIndex
- Data exists for target year
- Sufficient trading days available
- Valid date ranges