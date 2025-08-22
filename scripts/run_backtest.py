# scripts/run_backtest.py
from __future__ import annotations
import pandas as pd

from trading.datafeed.yfinance_feed import YFinanceFeed
from trading.strategies.christmas_ladder import XmasParams, generate_orders
from trading.execution.simulator import execute_orders
from trading.backtest.engine import run_backtest, calculate_performance_metrics

def main():
    """Main backtest orchestration using the new modular architecture."""
    # 1. Initialize data feed
    feed = YFinanceFeed()
    symbol = "SPY"  # change to your symbol
    
    # Use minute bars in December for realistic 10:30 fills; daily bars also work but 10:30 collapses to day close.
    print(f"Loading market data for {symbol}...")
    df = feed.history(symbol, start="2024-11-15", end="2025-01-15", interval="1m")
    
    # 2. Configure strategy parameters
    params = XmasParams(year=2024, symbol=symbol, buy_days=5, sell_days=10, sell_execution_time="10:30")
    
    # 3. Generate order intentions from strategy
    print("Generating strategy orders...")
    order_intentions = generate_orders(df, initial_cash=100_000, p=params)
    
    # 4. Simulate realistic order execution
    print("Simulating order execution...")
    executed_orders = execute_orders(order_intentions, df, slippage_bps=1.0)
    
    # 5. Run backtest analysis
    print("Running backtest analysis...")
    backtest_results = run_backtest(executed_orders, initial_cash=100_000)
    
    # 6. Calculate performance metrics
    performance_metrics = calculate_performance_metrics(
        executed_orders, 
        backtest_results["ending_cash"], 
        backtest_results["initial_cash"]
    )
    
    # 7. Display results
    print("\n=== ORDER EXECUTION SUMMARY ===")
    if not executed_orders.empty:
        print(executed_orders.head(20))
        print(f"\nTotal orders executed: {len(executed_orders)}")
        print(f"Orders with slippage: {len(executed_orders[executed_orders.get('slippage_bps', 0) != 0])}")
    else:
        print("No orders were executed.")
    
    print("\n=== BACKTEST RESULTS ===")
    for k, v in backtest_results.items():
        if k != "orders":
            if isinstance(v, float):
                print(f"{k}: {v:,.2f}")
            else:
                print(f"{k}: {v}")
    
    print("\n=== PERFORMANCE METRICS ===")
    for k, v in performance_metrics.items():
        if isinstance(v, float):
            if k == "win_rate":
                print(f"{k}: {v:.1%}")
            else:
                print(f"{k}: {v:.2f}")
        else:
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
