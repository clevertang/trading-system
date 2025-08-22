import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    dates = pd.date_range("2023-01-01", "2023-12-31", freq="D")
    # Filter to weekdays only (rough approximation of trading days)
    trading_days = dates[dates.weekday < 5]
    
    np.random.seed(42)  # For reproducible tests
    n_days = len(trading_days)
    
    # Generate realistic price data
    base_price = 100.0
    returns = np.random.normal(0.0005, 0.02, n_days)  # ~0.05% daily return, 2% volatility
    prices = base_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        "Open": prices * (1 + np.random.normal(0, 0.001, n_days)),
        "High": prices * (1 + np.abs(np.random.normal(0, 0.01, n_days))),
        "Low": prices * (1 - np.abs(np.random.normal(0, 0.01, n_days))),
        "Close": prices,
        "Volume": np.random.randint(100000, 2000000, n_days)
    }, index=trading_days)
    
    return df


@pytest.fixture
def sample_orders():
    """Sample orders DataFrame for testing."""
    return pd.DataFrame([
        {"time": pd.Timestamp("2023-01-15"), "side": "BUY", "qty": 100, "price": 105.0, "value": -10500.0},
        {"time": pd.Timestamp("2023-02-15"), "side": "BUY", "qty": 50, "price": 110.0, "value": -5500.0},
        {"time": pd.Timestamp("2023-03-15"), "side": "SELL", "qty": 30, "price": 115.0, "value": 3450.0},
    ])


@pytest.fixture
def christmas_params():
    """Sample Christmas ladder strategy parameters."""
    from trading.strategies.christmas_ladder import XmasParams
    return XmasParams(
        year=2023,
        symbol="TEST",
        buy_days=3,
        sell_days=5,
        sell_execution_time="10:30"
    )