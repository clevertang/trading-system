import pytest
import pandas as pd
from trading.backtest.engine import run_backtest


class TestBacktestEngine:
    
    def test_empty_orders(self):
        """Test backtest with no orders."""
        empty_orders = pd.DataFrame(columns=["time", "side", "qty", "price", "value"])
        initial_cash = 10000.0
        
        result = run_backtest(empty_orders, initial_cash)
        
        assert result["initial_cash"] == initial_cash
        assert result["ending_cash"] == initial_cash
        assert result["remaining_shares"] == 0
        assert result["pnl"] == 0.0
        assert result["return_pct"] == 0.0
    
    def test_buy_only_orders(self, sample_orders):
        """Test backtest with only buy orders."""
        buy_orders = sample_orders[sample_orders["side"] == "BUY"].copy()
        initial_cash = 20000.0
        
        result = run_backtest(buy_orders, initial_cash)
        
        # Should have spent money on stocks
        assert result["ending_cash"] < initial_cash
        assert result["remaining_shares"] > 0
        # With remaining shares, total value should include mark-to-market
        assert result["remaining_value_mark"] > 0
    
    def test_buy_and_sell_orders(self, sample_orders):
        """Test backtest with mixed buy/sell orders."""
        initial_cash = 20000.0
        
        result = run_backtest(sample_orders, initial_cash)
        
        # Calculate expected values
        total_cash_flow = sample_orders["value"].sum()
        expected_ending_cash = initial_cash + total_cash_flow
        
        bought = sample_orders.loc[sample_orders["side"] == "BUY", "qty"].sum()
        sold = sample_orders.loc[sample_orders["side"] == "SELL", "qty"].sum()
        expected_remaining_shares = bought - sold
        
        assert result["ending_cash"] == expected_ending_cash
        assert result["remaining_shares"] == expected_remaining_shares
        assert result["initial_cash"] == initial_cash
    
    def test_position_tracking(self):
        """Test accurate position tracking."""
        orders = pd.DataFrame([
            {"time": pd.Timestamp("2023-01-01"), "side": "BUY", "qty": 100, "price": 50.0, "value": -5000.0},
            {"time": pd.Timestamp("2023-01-02"), "side": "BUY", "qty": 50, "price": 60.0, "value": -3000.0},
            {"time": pd.Timestamp("2023-01-03"), "side": "SELL", "qty": 75, "price": 55.0, "value": 4125.0},
        ])
        
        result = run_backtest(orders, 10000.0)
        
        # 100 + 50 - 75 = 75 remaining shares
        assert result["remaining_shares"] == 75
        # Mark to market at last price (55.0)
        assert result["remaining_value_mark"] == 75 * 55.0
    
    def test_pnl_calculation(self):
        """Test P&L calculation accuracy."""
        orders = pd.DataFrame([
            {"time": pd.Timestamp("2023-01-01"), "side": "BUY", "qty": 100, "price": 100.0, "value": -10000.0},
            {"time": pd.Timestamp("2023-01-02"), "side": "SELL", "qty": 100, "price": 110.0, "value": 11000.0},
        ])
        initial_cash = 15000.0
        
        result = run_backtest(orders, initial_cash)
        
        # Should have made 1000 profit
        assert result["pnl"] == 1000.0
        assert result["return_pct"] == pytest.approx(1000.0 / 15000.0)
        assert result["remaining_shares"] == 0
    
    def test_return_percentage(self):
        """Test return percentage calculation."""
        orders = pd.DataFrame([
            {"time": pd.Timestamp("2023-01-01"), "side": "BUY", "qty": 50, "price": 100.0, "value": -5000.0},
        ])
        initial_cash = 10000.0
        
        result = run_backtest(orders, initial_cash)
        
        # With 50 shares at 100, remaining value = 5000
        # Total value = 5000 (cash) + 5000 (shares) = 10000
        # No gain/loss, return should be 0%
        assert result["return_pct"] == 0.0