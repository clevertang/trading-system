# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python-based trading system designed for backtesting strategies. The project implements a Christmas ladder strategy that accumulates positions before December 25th and distributes them over the following trading days.

## Core Architecture

The system follows a modular architecture with distinct components:

- **Data Feeds** (`trading/datafeed/`): Abstract market data interface with Yahoo Finance implementation
- **Strategies** (`trading/strategies/`): Trading strategy implementations (currently features the Christmas ladder strategy)
- **Backtest Engine**: Built into strategy modules for testing historical performance
- **Scripts** (`scripts/`): Executable scripts for data fetching and running backtests

Key architectural patterns:
- Abstract base classes for data feeds (`MarketDataFeed`) allow swapping data sources
- Strategy parameters use dataclasses for clean configuration
- Pandas DataFrames as the primary data structure for price/volume data
- Timestamp-aware order generation with flexible execution timing

## Key Components

### Data Management
- `trading/datafeed/base.py`: Abstract interface requiring `history()` and `last_price()` methods
- `trading/datafeed/yfinance_feed.py`: Yahoo Finance implementation for quick prototyping
- All data feeds return standardized DataFrames with ['Open','High','Low','Close','Volume'] columns

### Strategy Framework
- `trading/strategies/tangxin_demo.py`: Christmas ladder strategy implementation
- Strategies generate order DataFrames with timing, side, quantity, and price information
- Backtesting is integrated directly into strategy modules

### Script Usage
- `scripts/run_backtest.py`: Main entry point for running backtests
- `scripts/fetch_data.py`: Data retrieval utilities (currently empty)

## Development Commands

The project uses a Python virtual environment located at `.venv/`. Key dependencies include:
- pandas for data manipulation
- yfinance for market data
- Standard Python dataclass and typing modules

### Running Backtests
```bash
cd /Users/tang.xin/PycharmProjects/trading-system
python -m scripts.run_backtest
```

### Virtual Environment
The project includes a pre-configured virtual environment:
```bash
source .venv/bin/activate  # Activate virtual environment
```

## Data Expectations

- All price data uses pandas DataFrames with DatetimeIndex
- Timestamps are normalized to timezone-naive for consistency
- Market data requires at minimum: Open, High, Low, Close, Volume columns
- Strategy backtests expect minute-level data for realistic execution timing (10:30 fills)

## Strategy Development Guidelines

When creating new strategies:
1. Follow the pattern in `tangxin_demo.py` with dataclass parameters
2. Implement `generate_orders()` function returning structured DataFrame
3. Include `backtest()` function for performance evaluation
4. Use `_trading_days()` pattern for date-based strategy logic
5. Handle execution timing with `_bar_at_time()` for intraday precision