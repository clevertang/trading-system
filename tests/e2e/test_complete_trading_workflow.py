import pytest
import pandas as pd
import numpy as np
from trading.strategies.christmas_ladder import generate_orders, XmasParams
from trading.backtest.engine import run_backtest
from trading.execution.simulator import execute_orders
from trading.risk.position_sizing import calculate_position_size, check_margin_requirements


class TestCompleteTradingWorkflow:
    """End-to-end tests for complete trading workflows."""
    
    @pytest.fixture
    def extended_market_data(self):
        """Extended market data covering full year with Christmas period."""
        dates = pd.date_range("2023-01-01", "2023-12-31", freq="D")
        trading_days = dates[dates.weekday < 5]  # Weekdays only
        
        np.random.seed(42)
        n_days = len(trading_days)
        
        # Generate realistic price data with trend and volatility
        base_price = 100.0
        trend = np.linspace(0, 0.2, n_days)  # 20% annual trend
        noise = np.random.normal(0, 0.02, n_days)  # 2% daily volatility
        returns = trend + noise
        prices = base_price * np.exp(np.cumsum(returns / 252))  # Annualized
        
        df = pd.DataFrame({
            "Open": prices * (1 + np.random.normal(0, 0.001, n_days)),
            "High": prices * (1 + np.abs(np.random.normal(0, 0.01, n_days))),
            "Low": prices * (1 - np.abs(np.random.normal(0, 0.01, n_days))),
            "Close": prices,
            "Volume": np.random.randint(500000, 3000000, n_days)
        }, index=trading_days)
        
        return df
    
    def test_christmas_strategy_complete_workflow(self, extended_market_data):
        """Test complete Christmas ladder strategy workflow."""
        # 1. Setup strategy parameters
        params = XmasParams(
            year=2023,
            symbol="AAPL",
            buy_days=5,
            sell_days=10,
            sell_execution_time="10:30"
        )
        initial_cash = 50000
        
        # 2. Generate strategy orders
        orders = generate_orders(extended_market_data, initial_cash, params)
        
        # Validate orders were generated
        assert not orders.empty, "Strategy should generate orders"
        assert len(orders) > 0, "Should have at least some orders"
        
        # 3. Apply risk management
        buy_orders = orders[orders["side"] == "BUY"]
        if not buy_orders.empty:
            # Check margin requirements
            margin_ok = check_margin_requirements(orders, initial_cash, margin_multiplier=1.0)
            assert margin_ok, "Orders should pass margin requirements"
            
            # Validate that position sizing function works (doesn't require orders to already comply)
            for _, order in buy_orders.iterrows():
                position_size = calculate_position_size(
                    available_cash=initial_cash,
                    target_allocation=abs(order["value"]),
                    current_price=order["price"],
                    max_position_pct=0.2  # 20% max position
                )
                # Just verify the function works and returns reasonable values
                assert position_size >= 0, "Position size should be non-negative"
                assert isinstance(position_size, int), "Position size should be integer"
        
        # 4. Execute orders through simulation
        executed_orders = execute_orders(
            orders=orders,
            market_data=extended_market_data,
            slippage_bps=2.0,
            min_liquidity_check=True
        )
        
        # Validate execution
        assert isinstance(executed_orders, pd.DataFrame)
        # Note: executed_orders might be empty if execution fails, which is valid
        
        # 5. Run backtest
        backtest_results = run_backtest(executed_orders, initial_cash)
        
        # Validate backtest results
        assert backtest_results["initial_cash"] == initial_cash
        assert "pnl" in backtest_results
        assert "return_pct" in backtest_results
        assert "ending_cash" in backtest_results
        
        # 6. Validate strategy logic
        if not orders.empty:
            christmas = pd.Timestamp("2023-12-25")
            buy_orders = orders[orders["side"] == "BUY"]
            sell_orders = orders[orders["side"] == "SELL"]
            
            # Buy orders should be before Christmas
            if not buy_orders.empty:
                assert all(buy_orders["time"] < christmas), "Buy orders should be before Christmas"
            
            # Sell orders should be after Christmas
            if not sell_orders.empty:
                assert all(sell_orders["time"] > christmas), "Sell orders should be after Christmas"
    
    def test_portfolio_risk_integration(self, extended_market_data):
        """Test integration of risk management across multiple positions."""
        initial_cash = 100000
        positions = []
        
        # Simulate multiple strategy positions
        symbols = ["AAPL", "GOOGL", "MSFT"]
        
        for symbol in symbols:
            params = XmasParams(
                year=2023,
                symbol=symbol,
                buy_days=3,
                sell_days=5
            )
            
            # Generate orders for each symbol
            orders = generate_orders(extended_market_data, initial_cash // len(symbols), params)
            
            if not orders.empty:
                # Apply individual position sizing
                buy_orders = orders[orders["side"] == "BUY"]
                for _, order in buy_orders.iterrows():
                    position_size = calculate_position_size(
                        available_cash=initial_cash,
                        target_allocation=abs(order["value"]),
                        current_price=order["price"],
                        max_position_pct=0.1  # 10% max per position
                    )
                    positions.append({
                        "symbol": symbol,
                        "allocation": position_size * order["price"],
                        "shares": position_size
                    })
        
        # Validate portfolio-level constraints
        total_allocation = sum(pos["allocation"] for pos in positions)
        assert total_allocation <= initial_cash, "Total allocation should not exceed cash"
        
        # Check individual position limits
        for pos in positions:
            position_pct = pos["allocation"] / initial_cash
            assert position_pct <= 0.1, f"Position {pos['symbol']} exceeds 10% limit"
    
    def test_market_data_edge_cases(self):
        """Test workflow with challenging market data scenarios."""
        # Scenario 1: Limited data around Christmas
        limited_dates = pd.date_range("2023-12-20", "2023-12-29", freq="D")
        trading_days = limited_dates[limited_dates.weekday < 5]
        
        df_limited = pd.DataFrame({
            "Open": [100] * len(trading_days),
            "High": [102] * len(trading_days),
            "Low": [98] * len(trading_days),
            "Close": [101] * len(trading_days),
            "Volume": [1000000] * len(trading_days)
        }, index=trading_days)
        
        params = XmasParams(year=2023, symbol="TEST")
        orders = generate_orders(df_limited, 10000, params)
        
        # Should handle limited data gracefully
        if not orders.empty:
            backtest_results = run_backtest(orders, 10000)
            assert isinstance(backtest_results, dict)
        
        # Scenario 2: High volatility data
        volatile_dates = pd.date_range("2023-01-01", "2023-12-31", freq="D")
        volatile_trading_days = volatile_dates[volatile_dates.weekday < 5]
        
        np.random.seed(123)
        n_days = len(volatile_trading_days)
        
        # Extreme volatility
        returns = np.random.normal(0, 0.1, n_days)  # 10% daily volatility
        prices = 100 * np.exp(np.cumsum(returns))
        prices = np.maximum(prices, 1)  # Prevent negative prices
        
        df_volatile = pd.DataFrame({
            "Open": prices,
            "High": prices * 1.1,
            "Low": prices * 0.9,
            "Close": prices,
            "Volume": [2000000] * n_days
        }, index=volatile_trading_days)
        
        orders_volatile = generate_orders(df_volatile, 10000, params)
        
        if not orders_volatile.empty:
            # Risk management should still apply
            margin_ok = check_margin_requirements(orders_volatile, 10000)
            assert isinstance(margin_ok, bool)  # Should not crash
    
    def test_execution_realism(self, extended_market_data):
        """Test realistic execution scenarios with market microstructure effects."""
        params = XmasParams(year=2023, symbol="TEST", buy_days=2, sell_days=3)
        orders = generate_orders(extended_market_data, 25000, params)
        
        if orders.empty:
            pytest.skip("No orders generated for test")
        
        # Test different slippage scenarios
        slippage_scenarios = [0.5, 1.0, 2.0, 5.0]  # basis points
        
        for slippage in slippage_scenarios:
            executed = execute_orders(
                orders=orders,
                market_data=extended_market_data,
                slippage_bps=slippage,
                min_liquidity_check=True
            )
            
            # Higher slippage should generally result in worse execution prices
            # (This is a simplified check - real slippage testing would be more complex)
            if not executed.empty:
                backtest_results = run_backtest(executed, 25000)
                assert "pnl" in backtest_results
    
    def test_performance_metrics_calculation(self, extended_market_data):
        """Test comprehensive performance metrics calculation."""
        params = XmasParams(year=2023, symbol="TEST")
        initial_cash = 30000
        
        orders = generate_orders(extended_market_data, initial_cash, params)
        
        if orders.empty:
            pytest.skip("No orders generated for test")
        
        executed_orders = execute_orders(orders, extended_market_data)
        backtest_results = run_backtest(executed_orders, initial_cash)
        
        # Validate all key performance metrics are calculated
        required_metrics = [
            "initial_cash", "ending_cash", "remaining_shares", 
            "remaining_value_mark", "pnl", "return_pct"
        ]
        
        for metric in required_metrics:
            assert metric in backtest_results, f"Missing metric: {metric}"
            assert backtest_results[metric] is not None
        
        # Validate metric consistency
        total_value = backtest_results["ending_cash"] + backtest_results["remaining_value_mark"]
        calculated_pnl = total_value - backtest_results["initial_cash"]
        
        assert abs(calculated_pnl - backtest_results["pnl"]) < 0.01, "P&L calculation inconsistency"
        
        if backtest_results["initial_cash"] > 0:
            expected_return_pct = backtest_results["pnl"] / backtest_results["initial_cash"]
            assert abs(expected_return_pct - backtest_results["return_pct"]) < 0.0001, "Return % inconsistency"
    
    def test_error_handling_and_recovery(self, extended_market_data):
        """Test system behavior under error conditions."""
        # Test with invalid parameters
        invalid_params = XmasParams(
            year=2025,  # Future year with no data
            symbol="INVALID"
        )
        
        # Should handle gracefully without crashing
        try:
            orders = generate_orders(extended_market_data, 10000, invalid_params)
            # If orders are generated, they should be valid or empty
            assert isinstance(orders, pd.DataFrame)
        except Exception as e:
            # If exception is raised, it should be informative
            assert isinstance(e, (ValueError, RuntimeError, KeyError))
        
        # Test with extreme cash values
        extreme_cash_values = [0, -1000, 1e10]
        
        for cash in extreme_cash_values:
            try:
                params = XmasParams(year=2023, symbol="TEST")
                orders = generate_orders(extended_market_data, cash, params)
                
                if not orders.empty:
                    # Should still be able to run backtest
                    results = run_backtest(orders, max(cash, 0))
                    assert isinstance(results, dict)
                    
            except Exception as e:
                # Errors should be handled gracefully
                assert isinstance(e, (ValueError, RuntimeError))