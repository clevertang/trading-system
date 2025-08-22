import pytest
import pandas as pd
import numpy as np
from abc import ABC
from trading.datafeed.base import MarketDataFeed


class MockDataFeed(MarketDataFeed):
    """Mock implementation for testing."""
    
    def __init__(self):
        self.mock_data = pd.DataFrame({
            "Open": [100, 101, 102],
            "High": [102, 103, 104],
            "Low": [99, 100, 101],
            "Close": [101, 102, 103],
            "Volume": [1000000, 1100000, 1200000]
        }, index=pd.date_range("2023-01-01", periods=3, freq="D"))
    
    def history(self, symbol: str, start: str, end=None, interval="1d"):
        return self.mock_data.copy()
    
    def last_price(self, symbol: str):
        return self.mock_data.index[-1], self.mock_data["Close"].iloc[-1]


class TestMarketDataFeed:
    
    def test_abstract_base_class(self):
        """Test that MarketDataFeed is abstract."""
        with pytest.raises(TypeError):
            MarketDataFeed()
    
    def test_mock_implementation(self):
        """Test mock implementation works correctly."""
        feed = MockDataFeed()
        
        # Test history method
        data = feed.history("TEST", "2023-01-01")
        assert isinstance(data, pd.DataFrame)
        assert list(data.columns) == ["Open", "High", "Low", "Close", "Volume"]
        assert isinstance(data.index, pd.DatetimeIndex)
        assert len(data) == 3
    
    def test_last_price(self):
        """Test last price method."""
        feed = MockDataFeed()
        timestamp, price = feed.last_price("TEST")
        
        assert isinstance(timestamp, pd.Timestamp)
        assert isinstance(price, (int, float, np.integer, np.floating))
        assert price == 103  # Last close price in mock data
    
    def test_data_format_requirements(self):
        """Test that data format meets requirements."""
        feed = MockDataFeed()
        data = feed.history("TEST", "2023-01-01")
        
        # Must have required columns
        required_columns = {"Open", "High", "Low", "Close", "Volume"}
        assert required_columns.issubset(set(data.columns))
        
        # Must have DatetimeIndex
        assert isinstance(data.index, pd.DatetimeIndex)
        
        # Data should be numeric
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            assert pd.api.types.is_numeric_dtype(data[col])
    
    def test_interface_contract(self):
        """Test that interface contract is enforced."""
        feed = MockDataFeed()
        
        # history method should accept these parameters
        data = feed.history("AAPL", "2023-01-01", "2023-01-31", "1d")
        assert isinstance(data, pd.DataFrame)
        
        # last_price should return tuple
        result = feed.last_price("AAPL")
        assert isinstance(result, tuple)
        assert len(result) == 2