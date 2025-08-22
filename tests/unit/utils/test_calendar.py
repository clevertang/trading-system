import pytest
import pandas as pd
from trading.utils.calendar import get_trading_days_around_date


class TestCalendar:
    
    def test_get_trading_days_around_date_basic(self, sample_market_data):
        """Test basic functionality of get_trading_days_around_date."""
        anchor = pd.Timestamp("2023-07-04")  # July 4th
        
        pre_dates, post_dates = get_trading_days_around_date(
            sample_market_data, anchor, before_days=5, after_days=3
        )
        
        assert isinstance(pre_dates, pd.DatetimeIndex)
        assert isinstance(post_dates, pd.DatetimeIndex)
        assert len(pre_dates) <= 5  # May be fewer due to weekends/holidays
        assert len(post_dates) <= 3
        
        # All pre_dates should be before anchor
        assert all(pre_dates < anchor)
        
        # All post_dates should be after anchor
        assert all(post_dates > anchor)
    
    def test_christmas_dates(self, sample_market_data):
        """Test with Christmas date (common use case)."""
        xmas = pd.Timestamp("2023-12-25")
        
        pre_dates, post_dates = get_trading_days_around_date(
            sample_market_data, xmas, before_days=5, after_days=10
        )
        
        # Should find trading days before and after Christmas
        assert len(pre_dates) > 0
        assert len(post_dates) > 0
        
        # Dates should be properly ordered
        assert pre_dates.is_monotonic_increasing
        assert post_dates.is_monotonic_increasing
    
    def test_weekend_anchor_date(self, sample_market_data):
        """Test with weekend anchor date."""
        # Saturday
        weekend = pd.Timestamp("2023-07-01")  # Assuming this is a weekend
        
        pre_dates, post_dates = get_trading_days_around_date(
            sample_market_data, weekend, before_days=3, after_days=3
        )
        
        # Should still work even if anchor is not a trading day
        assert isinstance(pre_dates, pd.DatetimeIndex)
        assert isinstance(post_dates, pd.DatetimeIndex)
    
    def test_insufficient_data_before(self, sample_market_data):
        """Test when there aren't enough trading days before anchor."""
        # Use very early date in the year
        early_date = pd.Timestamp("2023-01-02")
        
        pre_dates, post_dates = get_trading_days_around_date(
            sample_market_data, early_date, before_days=10, after_days=5
        )
        
        # Should return whatever dates are available
        assert len(pre_dates) <= 10  # Likely fewer than requested
        assert len(post_dates) <= 5
    
    def test_insufficient_data_after(self, sample_market_data):
        """Test when there aren't enough trading days after anchor."""
        # Use very late date in the year
        late_date = pd.Timestamp("2023-12-28")
        
        pre_dates, post_dates = get_trading_days_around_date(
            sample_market_data, late_date, before_days=5, after_days=10
        )
        
        # Should return whatever dates are available
        assert len(pre_dates) <= 5
        assert len(post_dates) <= 10  # Likely fewer than requested
    
    def test_invalid_dataframe_index(self):
        """Test error handling with non-DatetimeIndex."""
        df = pd.DataFrame({
            "Close": [100, 101, 102]
        }, index=[0, 1, 2])  # Integer index instead of DatetimeIndex
        
        anchor = pd.Timestamp("2023-06-01")
        
        with pytest.raises(ValueError, match="DataFrame index must be DatetimeIndex"):
            get_trading_days_around_date(df, anchor, 5, 5)
    
    def test_no_data_for_year(self, sample_market_data):
        """Test error handling when no data exists for anchor year."""
        # Use anchor date from different year
        anchor = pd.Timestamp("2022-06-01")
        
        with pytest.raises(ValueError, match="No data for year"):
            get_trading_days_around_date(sample_market_data, anchor, 5, 5)
    
    def test_exact_requested_days(self):
        """Test with data that has exact number of requested days."""
        # Create minimal dataset
        dates = pd.date_range("2023-06-01", "2023-06-20", freq="D")
        trading_days = dates[dates.weekday < 5]  # Weekdays only
        
        df = pd.DataFrame({
            "Close": range(len(trading_days))
        }, index=trading_days)
        
        anchor = pd.Timestamp("2023-06-10")
        
        pre_dates, post_dates = get_trading_days_around_date(
            df, anchor, before_days=3, after_days=3
        )
        
        assert len(pre_dates) <= 3
        assert len(post_dates) <= 3
        
        # Verify dates are from the correct dataset
        assert all(date in df.index for date in pre_dates)
        assert all(date in df.index for date in post_dates)
    
    def test_date_uniqueness_and_sorting(self, sample_market_data):
        """Test that returned dates are unique and sorted."""
        anchor = pd.Timestamp("2023-06-15")
        
        pre_dates, post_dates = get_trading_days_around_date(
            sample_market_data, anchor, before_days=10, after_days=10
        )
        
        # Check uniqueness
        assert len(pre_dates) == len(pre_dates.unique())
        assert len(post_dates) == len(post_dates.unique())
        
        # Check sorting
        assert pre_dates.equals(pre_dates.sort_values())
        assert post_dates.equals(post_dates.sort_values())
    
    def test_integration_with_strategy_workflow(self, sample_market_data):
        """Test integration with strategy workflow."""
        # Simulate Christmas strategy workflow
        xmas = pd.Timestamp("2023-12-25")
        buy_days = 5
        sell_days = 10
        
        pre_dates, post_dates = get_trading_days_around_date(
            sample_market_data, xmas, buy_days, sell_days
        )
        
        # Should be able to use these dates for strategy execution
        assert len(pre_dates) > 0
        assert len(post_dates) > 0
        
        # Dates should be valid trading days (exist in market data)
        market_dates = set(sample_market_data.index.date)
        assert all(date.date() in market_dates for date in pre_dates)
        assert all(date.date() in market_dates for date in post_dates)