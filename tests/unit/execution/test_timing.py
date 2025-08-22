import pytest
import pandas as pd
from trading.execution.timing import find_execution_bar, get_market_open_close, is_market_hours


class TestTiming:
    
    @pytest.fixture
    def intraday_data(self):
        """Sample intraday market data."""
        # Create intraday data for one trading day
        base_date = "2023-06-15"
        times = pd.date_range(f"{base_date} 09:30", f"{base_date} 16:00", freq="30min")
        
        return pd.DataFrame({
            "Open": [100 + i for i in range(len(times))],
            "High": [102 + i for i in range(len(times))],
            "Low": [99 + i for i in range(len(times))],
            "Close": [101 + i for i in range(len(times))],
            "Volume": [1000000] * len(times)
        }, index=times)
    
    def test_find_execution_bar_exact_time(self, intraday_data):
        """Test finding execution bar at exact available time."""
        target_date = pd.Timestamp("2023-06-15")
        target_time = "10:00"
        
        result = find_execution_bar(intraday_data, target_date, target_time)
        
        expected = pd.Timestamp("2023-06-15 10:00:00")
        assert result == expected
    
    def test_find_execution_bar_between_bars(self, intraday_data):
        """Test finding execution bar between available times."""
        target_date = pd.Timestamp("2023-06-15")
        target_time = "10:15"  # Between 10:00 and 10:30
        
        result = find_execution_bar(intraday_data, target_date, target_time)
        
        # Should return next available bar (10:30)
        expected = pd.Timestamp("2023-06-15 10:30:00")
        assert result == expected
    
    def test_find_execution_bar_after_market_close(self, intraday_data):
        """Test finding execution bar after market close."""
        target_date = pd.Timestamp("2023-06-15")
        target_time = "17:00"  # After market close
        
        result = find_execution_bar(intraday_data, target_date, target_time)
        
        # Should return last bar of the day
        expected = intraday_data.index[-1]
        assert result == expected
    
    def test_find_execution_bar_before_market_open(self, intraday_data):
        """Test finding execution bar before market open."""
        target_date = pd.Timestamp("2023-06-15")
        target_time = "09:00"  # Before market open
        
        result = find_execution_bar(intraday_data, target_date, target_time)
        
        # Should return first available bar (market open)
        expected = pd.Timestamp("2023-06-15 09:30:00")
        assert result == expected
    
    def test_find_execution_bar_daily_data(self, sample_market_data):
        """Test finding execution bar with daily data."""
        target_date = pd.Timestamp("2023-06-15")
        target_time = "10:30"
        
        result = find_execution_bar(sample_market_data, target_date, target_time)
        
        # With daily data, should return the single available bar for that date
        expected_date = target_date.date()
        assert result.date() == expected_date
    
    def test_find_execution_bar_no_data(self, intraday_data):
        """Test error when no data exists for target date."""
        target_date = pd.Timestamp("2023-01-01")  # Date not in data
        target_time = "10:30"
        
        with pytest.raises(RuntimeError, match="No bars on"):
            find_execution_bar(intraday_data, target_date, target_time)
    
    def test_get_market_open_close(self, intraday_data):
        """Test getting market open/close times."""
        target_date = pd.Timestamp("2023-06-15")
        
        market_open, market_close = get_market_open_close(intraday_data, target_date)
        
        assert market_open == pd.Timestamp("2023-06-15 09:30:00")
        assert market_close == pd.Timestamp("2023-06-15 16:00:00")
    
    def test_get_market_open_close_no_data(self, intraday_data):
        """Test error when no market data for date."""
        target_date = pd.Timestamp("2023-01-01")
        
        with pytest.raises(RuntimeError, match="No market data for"):
            get_market_open_close(intraday_data, target_date)
    
    def test_is_market_hours_during_session(self):
        """Test market hours check during trading session."""
        timestamp = pd.Timestamp("2023-06-15 10:30:00")
        
        assert is_market_hours(timestamp) == True
        assert is_market_hours(timestamp, "09:30", "16:00") == True
    
    def test_is_market_hours_before_open(self):
        """Test market hours check before market open."""
        timestamp = pd.Timestamp("2023-06-15 09:00:00")
        
        assert is_market_hours(timestamp) == False
        assert is_market_hours(timestamp, "09:30", "16:00") == False
    
    def test_is_market_hours_after_close(self):
        """Test market hours check after market close."""
        timestamp = pd.Timestamp("2023-06-15 17:00:00")
        
        assert is_market_hours(timestamp) == False
        assert is_market_hours(timestamp, "09:30", "16:00") == False
    
    def test_is_market_hours_at_boundaries(self):
        """Test market hours check at exact open/close times."""
        open_time = pd.Timestamp("2023-06-15 09:30:00")
        close_time = pd.Timestamp("2023-06-15 16:00:00")
        
        assert is_market_hours(open_time, "09:30", "16:00") == True
        assert is_market_hours(close_time, "09:30", "16:00") == True
    
    def test_is_market_hours_custom_session(self):
        """Test market hours check with custom session times."""
        timestamp = pd.Timestamp("2023-06-15 08:30:00")
        
        # Regular session
        assert is_market_hours(timestamp, "09:30", "16:00") == False
        
        # Extended session
        assert is_market_hours(timestamp, "08:00", "17:00") == True
    
    def test_timing_integration_workflow(self, intraday_data):
        """Test integration of timing functions in trading workflow."""
        target_date = pd.Timestamp("2023-06-15")
        
        # Get market session boundaries
        market_open, market_close = get_market_open_close(intraday_data, target_date)
        
        # Find execution time for order
        execution_time = find_execution_bar(intraday_data, target_date, "10:30")
        
        # Verify execution time is within market hours
        assert is_market_hours(execution_time, "09:30", "16:00")
        assert market_open <= execution_time <= market_close
    
    def test_execution_bar_with_gaps(self):
        """Test execution bar finding with gaps in data."""
        # Create data with gaps (missing some time periods)
        times = [
            "2023-06-15 09:30:00",
            "2023-06-15 10:00:00",
            # Gap: missing 10:30
            "2023-06-15 11:00:00",
            "2023-06-15 16:00:00"
        ]
        
        df = pd.DataFrame({
            "Close": [100, 101, 102, 103]
        }, index=pd.to_datetime(times))
        
        target_date = pd.Timestamp("2023-06-15")
        
        # Target time falls in gap
        result = find_execution_bar(df, target_date, "10:30")
        
        # Should return next available bar (11:00)
        expected = pd.Timestamp("2023-06-15 11:00:00")
        assert result == expected