import pytest
import pandas as pd
from trading.risk.position_sizing import calculate_position_size, check_margin_requirements


class TestPositionSizing:
    
    def test_calculate_position_size_basic(self):
        """Test basic position size calculation."""
        shares = calculate_position_size(
            available_cash=10000,
            target_allocation=5000,
            current_price=100.0,
            max_position_pct=0.5
        )
        
        # Should buy 50 shares (5000 / 100)
        assert shares == 50
    
    def test_calculate_position_size_max_constraint(self):
        """Test maximum position percentage constraint."""
        shares = calculate_position_size(
            available_cash=10000,
            target_allocation=8000,  # Want 80% allocation
            current_price=100.0,
            max_position_pct=0.1  # But max is 10%
        )
        
        # Should be limited to 10% = 1000, so 10 shares
        assert shares == 10
    
    def test_calculate_position_size_zero_cases(self):
        """Test edge cases with zero values."""
        # Zero cash
        shares = calculate_position_size(0, 5000, 100.0)
        assert shares == 0
        
        # Zero price
        shares = calculate_position_size(10000, 5000, 0)
        assert shares == 0
        
        # Negative price
        shares = calculate_position_size(10000, 5000, -50.0)
        assert shares == 0
    
    def test_calculate_position_size_fractional_shares(self):
        """Test that fractional shares are rounded down."""
        shares = calculate_position_size(
            available_cash=10000,
            target_allocation=999,  # Would buy 9.99 shares at $100
            current_price=100.0
        )
        
        # Should round down to 9 shares
        assert shares == 9
    
    def test_check_margin_requirements_cash_account(self):
        """Test margin check for cash account."""
        orders = pd.DataFrame([
            {"side": "BUY", "qty": 50, "price": 100.0, "value": -5000},
            {"side": "BUY", "qty": 30, "price": 100.0, "value": -3000},
            {"side": "SELL", "qty": 20, "price": 100.0, "value": 2000}
        ])
        
        # Cash account (1:1 buying power)
        # Total buy orders = 8000, available cash = 10000
        assert check_margin_requirements(orders, 10000, 1.0) == True
        
        # Not enough cash
        assert check_margin_requirements(orders, 7000, 1.0) == False
    
    def test_check_margin_requirements_margin_account(self):
        """Test margin check for margin account."""
        orders = pd.DataFrame([
            {"side": "BUY", "qty": 120, "price": 100.0, "value": -12000},
            {"side": "SELL", "qty": 20, "price": 100.0, "value": 2000}
        ])
        
        # Margin account (2:1 buying power)
        # Need 12000 cash, have 10000 * 2 = 20000 buying power
        assert check_margin_requirements(orders, 10000, 2.0) == True
        
        # Not enough buying power
        assert check_margin_requirements(orders, 5000, 2.0) == False
    
    def test_check_margin_requirements_empty_orders(self):
        """Test margin check with empty orders."""
        empty_orders = pd.DataFrame(columns=["side", "qty", "price", "value"])
        
        assert check_margin_requirements(empty_orders, 1000, 1.0) == True
    
    def test_check_margin_requirements_no_buy_orders(self):
        """Test margin check with only sell orders."""
        sell_orders = pd.DataFrame([
            {"side": "SELL", "qty": 50, "price": 100.0, "value": 5000},
            {"side": "SELL", "qty": 30, "price": 100.0, "value": 3000}
        ])
        
        # No cash requirement for sell orders
        assert check_margin_requirements(sell_orders, 1000, 1.0) == True
    
    def test_position_sizing_integration(self):
        """Test position sizing with realistic portfolio parameters."""
        portfolio_size = 100000
        position_limit = 0.05  # 5% max per position
        stock_price = 150.0
        target_allocation = 8000
        
        shares = calculate_position_size(
            available_cash=portfolio_size,
            target_allocation=target_allocation,
            current_price=stock_price,
            max_position_pct=position_limit
        )
        
        # Max allocation = 100000 * 0.05 = 5000
        # Min(8000, 5000) = 5000
        # Shares = 5000 / 150 = 33.33 -> 33
        assert shares == 33
        
        # Verify actual allocation doesn't exceed limits
        actual_allocation = shares * stock_price
        assert actual_allocation <= portfolio_size * position_limit
        assert actual_allocation <= target_allocation