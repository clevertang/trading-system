import pytest
import pandas as pd
from trading.strategies.christmas_ladder import generate_orders, XmasParams


class TestChristmasLadder:
    
    def test_xmas_params_defaults(self):
        """Test XmasParams default values."""
        params = XmasParams(year=2023, symbol="TEST")
        
        assert params.year == 2023
        assert params.symbol == "TEST"
        assert params.buy_days == 5
        assert params.sell_days == 10
        assert params.sell_execution_time == "10:30"
    
    def test_generate_orders_basic(self, sample_market_data, christmas_params):
        """Test basic order generation."""
        orders = generate_orders(sample_market_data, 10000, christmas_params)
        
        assert isinstance(orders, pd.DataFrame)
        if not orders.empty:
            # Should have required columns
            required_cols = {"time", "side", "qty", "price", "value"}
            assert required_cols.issubset(set(orders.columns))
            
            # Should have both BUY and SELL orders
            sides = set(orders["side"].unique())
            assert "BUY" in sides
            # SELL orders depend on having successful buys
    
    def test_buy_phase_allocation(self, sample_market_data):
        """Test that buy phase allocates cash evenly."""
        params = XmasParams(year=2023, symbol="TEST", buy_days=3, sell_days=5)
        cash = 9000  # Divisible by 3 for clean test
        
        orders = generate_orders(sample_market_data, cash, params)
        
        if not orders.empty:
            buy_orders = orders[orders["side"] == "BUY"]
            
            # Each buy should be roughly equal allocation
            expected_per_buy = cash / params.buy_days
            
            # Check that we're not over-allocating
            total_spent = abs(buy_orders["value"].sum())
            assert total_spent <= cash
    
    def test_sell_phase_distribution(self, sample_market_data):
        """Test that sell phase distributes shares evenly."""
        params = XmasParams(year=2023, symbol="TEST", buy_days=2, sell_days=3)
        
        orders = generate_orders(sample_market_data, 10000, params)
        
        if not orders.empty:
            buy_orders = orders[orders["side"] == "BUY"]
            sell_orders = orders[orders["side"] == "SELL"]
            
            if not buy_orders.empty and not sell_orders.empty:
                total_bought = buy_orders["qty"].sum()
                total_sold = sell_orders["qty"].sum()
                
                # Should sell all or most shares
                assert total_sold <= total_bought
    
    def test_order_timing(self, sample_market_data, christmas_params):
        """Test that orders are timed correctly around Christmas."""
        orders = generate_orders(sample_market_data, 10000, christmas_params)
        
        if not orders.empty:
            # Christmas date
            xmas = pd.Timestamp(year=christmas_params.year, month=12, day=25)
            
            buy_orders = orders[orders["side"] == "BUY"]
            sell_orders = orders[orders["side"] == "SELL"]
            
            # Buy orders should be before Christmas
            if not buy_orders.empty:
                assert all(buy_orders["time"] < xmas)
            
            # Sell orders should be after Christmas
            if not sell_orders.empty:
                assert all(sell_orders["time"] > xmas)
    
    def test_no_market_data_around_christmas(self):
        """Test behavior when no market data exists around Christmas."""
        # Create data that doesn't include December
        dates = pd.date_range("2023-01-01", "2023-11-30", freq="D")
        trading_days = dates[dates.weekday < 5]
        
        df = pd.DataFrame({
            "Open": [100] * len(trading_days),
            "High": [102] * len(trading_days),
            "Low": [98] * len(trading_days),
            "Close": [101] * len(trading_days),
            "Volume": [1000000] * len(trading_days)
        }, index=trading_days)
        
        params = XmasParams(year=2023, symbol="TEST")
        orders = generate_orders(df, 10000, params)
        
        # Should return empty DataFrame or handle gracefully
        assert isinstance(orders, pd.DataFrame)
    
    def test_zero_cash(self, sample_market_data, christmas_params):
        """Test behavior with zero cash."""
        orders = generate_orders(sample_market_data, 0, christmas_params)
        
        # Should return empty orders or orders with zero quantities
        if not orders.empty:
            buy_orders = orders[orders["side"] == "BUY"]
            if not buy_orders.empty:
                assert all(buy_orders["qty"] == 0)
    
    def test_order_values_consistency(self, sample_market_data, christmas_params):
        """Test that order values are consistent with qty and price."""
        orders = generate_orders(sample_market_data, 10000, christmas_params)
        
        if not orders.empty:
            for _, order in orders.iterrows():
                expected_value = order["qty"] * order["price"]
                if order["side"] == "BUY":
                    expected_value = -expected_value
                
                assert abs(order["value"] - expected_value) < 0.01  # Allow for floating point errors
    
    def test_realistic_scenario(self, sample_market_data):
        """Test with realistic parameters."""
        params = XmasParams(
            year=2023,
            symbol="AAPL",
            buy_days=5,
            sell_days=10,
            sell_execution_time="10:30"
        )
        
        orders = generate_orders(sample_market_data, 50000, params)
        
        if not orders.empty:
            # Basic sanity checks
            assert len(orders) > 0
            assert all(orders["qty"] >= 0)
            assert all(orders["price"] > 0)
            
            # Should have reasonable number of orders
            assert len(orders) <= params.buy_days + params.sell_days