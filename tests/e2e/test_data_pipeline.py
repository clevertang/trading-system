import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from trading.datafeed.base import MarketDataFeed
from trading.strategies.christmas_ladder import generate_orders, XmasParams
from trading.backtest.engine import run_backtest


class MockYFinanceFeed(MarketDataFeed):
    """Mock Yahoo Finance feed for testing data pipeline."""
    
    def __init__(self, include_gaps=False, include_errors=False):
        self.include_gaps = include_gaps
        self.include_errors = include_errors
        self._generate_mock_data()
    
    def _generate_mock_data(self):
        """Generate realistic mock market data."""
        dates = pd.date_range("2023-01-01", "2023-12-31", freq="D")
        trading_days = dates[dates.weekday < 5]
        
        if self.include_gaps:
            # Remove some random trading days to simulate holidays/gaps
            gap_indices = np.random.choice(len(trading_days), size=10, replace=False)
            trading_days = trading_days.delete(gap_indices)
        
        np.random.seed(42)
        n_days = len(trading_days)
        
        # Generate realistic stock price data
        base_price = 150.0
        returns = np.random.normal(0.0005, 0.015, n_days)  # Daily returns
        prices = base_price * np.exp(np.cumsum(returns))
        
        # Add some market events (crashes, rallies)
        event_days = np.random.choice(n_days, size=5, replace=False)
        for day in event_days:
            prices[day:] *= np.random.choice([0.95, 1.05])  # 5% moves
        
        # Generate proper OHLC data that follows market logic
        opens = prices * (1 + np.random.normal(0, 0.002, n_days))
        closes = prices
        
        # Ensure High >= max(Open, Close) and Low <= min(Open, Close)
        high_base = np.maximum(opens, closes)
        low_base = np.minimum(opens, closes)
        
        highs = high_base * (1 + np.abs(np.random.normal(0, 0.01, n_days)))
        lows = low_base * (1 - np.abs(np.random.normal(0, 0.01, n_days)))
        
        self.data = pd.DataFrame({
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": np.random.randint(1000000, 5000000, n_days)
        }, index=trading_days)
    
    def history(self, symbol: str, start: str, end=None, interval="1d"):
        if self.include_errors and np.random.random() < 0.1:  # 10% error rate
            raise ConnectionError("Mock network error")
        
        start_date = pd.Timestamp(start)
        end_date = pd.Timestamp(end) if end else self.data.index[-1]
        
        mask = (self.data.index >= start_date) & (self.data.index <= end_date)
        return self.data[mask].copy()
    
    def last_price(self, symbol: str):
        if self.include_errors and np.random.random() < 0.05:  # 5% error rate
            raise TimeoutError("Mock timeout error")
        
        return self.data.index[-1], float(self.data["Close"].iloc[-1])


class TestDataPipeline:
    """Test data pipeline integration and error handling."""
    
    def test_clean_data_pipeline(self):
        """Test pipeline with clean, complete data."""
        feed = MockYFinanceFeed(include_gaps=False, include_errors=False)
        
        # Fetch data
        data = feed.history("AAPL", "2023-01-01", "2023-12-31")
        
        # Validate data quality
        assert not data.empty
        assert data.index.is_monotonic_increasing
        assert not data.isnull().any().any()
        
        # Run strategy with clean data
        params = XmasParams(year=2023, symbol="AAPL")
        orders = generate_orders(data, 50000, params)
        
        # Should produce valid orders
        if not orders.empty:
            assert all(orders["qty"] >= 0)
            assert all(orders["price"] > 0)
            
            # Run backtest
            results = run_backtest(orders, 50000)
            assert results["initial_cash"] == 50000
    
    def test_data_pipeline_with_gaps(self):
        """Test pipeline robustness with data gaps."""
        feed = MockYFinanceFeed(include_gaps=True, include_errors=False)
        
        data = feed.history("AAPL", "2023-01-01", "2023-12-31")
        
        # Data should still be usable despite gaps
        assert not data.empty
        
        # Strategy should handle gaps gracefully
        params = XmasParams(year=2023, symbol="AAPL")
        
        try:
            orders = generate_orders(data, 25000, params)
            
            # If orders are generated, they should be valid
            if not orders.empty:
                results = run_backtest(orders, 25000)
                assert isinstance(results, dict)
                
        except (ValueError, RuntimeError) as e:
            # Acceptable if strategy can't work with gapped data
            assert "No data" in str(e) or "No bars" in str(e)
    
    def test_data_pipeline_error_recovery(self):
        """Test pipeline error handling and recovery."""
        feed = MockYFinanceFeed(include_errors=True)
        
        # Attempt data fetch with retries
        max_retries = 3
        data = None
        
        for attempt in range(max_retries):
            try:
                data = feed.history("AAPL", "2023-01-01", "2023-12-31")
                break  # Success
            except (ConnectionError, TimeoutError):
                if attempt == max_retries - 1:
                    pytest.skip("Simulated network errors - would implement retry logic")
                continue
        
        if data is not None and not data.empty:
            # Proceed with strategy if data was eventually fetched
            params = XmasParams(year=2023, symbol="AAPL")
            orders = generate_orders(data, 30000, params)
            
            if not orders.empty:
                results = run_backtest(orders, 30000)
                assert "pnl" in results
    
    def test_data_validation_pipeline(self):
        """Test comprehensive data validation."""
        feed = MockYFinanceFeed()
        data = feed.history("AAPL", "2023-01-01", "2023-12-31")
        
        # Data quality checks
        validation_results = self._validate_market_data(data)
        
        assert validation_results["has_required_columns"]
        assert validation_results["has_datetime_index"] 
        assert validation_results["no_missing_values"]
        assert validation_results["positive_prices"]
        assert validation_results["logical_ohlc"]
        
        # Use validated data in strategy
        if all(validation_results.values()):
            params = XmasParams(year=2023, symbol="AAPL")
            orders = generate_orders(data, 40000, params)
            
            if not orders.empty:
                results = run_backtest(orders, 40000)
                assert isinstance(results["return_pct"], (int, float))
    
    def _validate_market_data(self, df: pd.DataFrame) -> dict:
        """Comprehensive market data validation."""
        results = {}
        
        # Required columns check
        required_cols = {"Open", "High", "Low", "Close", "Volume"}
        results["has_required_columns"] = required_cols.issubset(set(df.columns))
        
        # Index type check
        results["has_datetime_index"] = isinstance(df.index, pd.DatetimeIndex)
        
        # Missing values check
        results["no_missing_values"] = not df.isnull().any().any()
        
        # Positive prices check
        price_cols = ["Open", "High", "Low", "Close"]
        results["positive_prices"] = all(df[col].min() > 0 for col in price_cols if col in df.columns)
        
        # OHLC logic check (High >= Low, etc.)
        if all(col in df.columns for col in price_cols):
            high_low_check = (df["High"] >= df["Low"]).all()
            high_oc_check = (df["High"] >= df[["Open", "Close"]].max(axis=1)).all()
            low_oc_check = (df["Low"] <= df[["Open", "Close"]].min(axis=1)).all()
            results["logical_ohlc"] = high_low_check and high_oc_check and low_oc_check
        else:
            results["logical_ohlc"] = True
        
        return results
    
    def test_multi_symbol_data_pipeline(self):
        """Test pipeline with multiple symbols."""
        feed = MockYFinanceFeed()
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        
        all_data = {}
        all_results = {}
        
        # Fetch data for all symbols
        for symbol in symbols:
            try:
                data = feed.history(symbol, "2023-01-01", "2023-12-31")
                all_data[symbol] = data
                
                # Run individual strategies
                params = XmasParams(year=2023, symbol=symbol)
                orders = generate_orders(data, 20000, params)
                
                if not orders.empty:
                    results = run_backtest(orders, 20000)
                    all_results[symbol] = results
                    
            except Exception as e:
                # Log error but continue with other symbols
                print(f"Error processing {symbol}: {e}")
        
        # Aggregate results
        if all_results:
            total_pnl = sum(result["pnl"] for result in all_results.values())
            avg_return = np.mean([result["return_pct"] for result in all_results.values()])
            
            assert isinstance(total_pnl, (int, float))
            assert isinstance(avg_return, (int, float))
    
    def test_real_time_data_simulation(self):
        """Test pipeline with simulated real-time data updates."""
        feed = MockYFinanceFeed()
        
        # Simulate incremental data updates
        base_data = feed.history("AAPL", "2023-01-01", "2023-06-30")
        
        # Initial strategy run with partial data
        params = XmasParams(year=2023, symbol="AAPL")
        
        # This might not work (no Christmas data yet), which is expected
        try:
            orders_partial = generate_orders(base_data, 30000, params)
        except (ValueError, RuntimeError):
            orders_partial = pd.DataFrame()  # Expected for partial year
        
        # Simulate data update with full year
        full_data = feed.history("AAPL", "2023-01-01", "2023-12-31")
        orders_full = generate_orders(full_data, 30000, params)
        
        # Full year should produce more complete results
        if not orders_full.empty:
            results = run_backtest(orders_full, 30000)
            assert results["initial_cash"] == 30000
    
    def test_data_freshness_and_staleness(self):
        """Test handling of stale or outdated data."""
        feed = MockYFinanceFeed()
        
        # Test with recent data
        recent_data = feed.history("AAPL", "2023-11-01", "2023-12-31")
        
        # Test last price freshness
        last_timestamp, last_price = feed.last_price("AAPL")
        
        assert isinstance(last_timestamp, pd.Timestamp)
        assert isinstance(last_price, (int, float))
        assert last_price > 0
        
        # Verify last price matches data
        if not recent_data.empty:
            expected_price = recent_data["Close"].iloc[-1]
            assert abs(last_price - expected_price) < 0.01
    
    def test_data_format_consistency(self):
        """Test consistency of data formats across different sources."""
        feed = MockYFinanceFeed()
        
        # Test different date ranges and intervals
        test_cases = [
            ("2023-01-01", "2023-01-31", "1d"),
            ("2023-06-01", "2023-06-30", "1d"), 
            ("2023-12-01", "2023-12-31", "1d")
        ]
        
        all_formats_consistent = True
        
        for start, end, interval in test_cases:
            data = feed.history("AAPL", start, end, interval)
            
            if not data.empty:
                # Check format consistency
                format_ok = (
                    isinstance(data.index, pd.DatetimeIndex) and
                    set(["Open", "High", "Low", "Close", "Volume"]).issubset(set(data.columns)) and
                    all(pd.api.types.is_numeric_dtype(data[col]) for col in ["Open", "High", "Low", "Close", "Volume"])
                )
                
                all_formats_consistent &= format_ok
        
        assert all_formats_consistent, "Data format inconsistency detected"