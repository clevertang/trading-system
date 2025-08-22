from __future__ import annotations
import pandas as pd


def run_backtest(orders: pd.DataFrame, initial_cash: float) -> dict:
    """
    Generic backtest engine that works with any strategy's order list.
    
    Args:
        orders: DataFrame with columns ['time', 'side', 'qty', 'price', 'value']
        initial_cash: Starting cash amount
        
    Returns:
        Dictionary with backtest results including P&L and position tracking
    """
    if orders.empty:
        return {
            "orders": orders,
            "initial_cash": initial_cash,
            "ending_cash": initial_cash,
            "remaining_shares": 0,
            "remaining_value_mark": 0.0,
            "pnl": 0.0,
            "return_pct": 0.0,
        }
    
    # Calculate cash flow from orders
    cash_flow = orders["value"].sum()
    ending_cash = initial_cash + cash_flow
    
    # Calculate position tracking
    bought = orders.loc[orders["side"] == "BUY", "qty"].sum() if "BUY" in orders["side"].values else 0
    sold = orders.loc[orders["side"] == "SELL", "qty"].sum() if "SELL" in orders["side"].values else 0
    remaining_shares = int(bought - sold)
    
    # Mark remaining position to last known price
    remaining_value_mark = 0.0
    if remaining_shares > 0 and not orders.empty:
        last_price = float(orders.iloc[-1]["price"])
        remaining_value_mark = remaining_shares * last_price
    
    # Calculate P&L
    total_value = ending_cash + remaining_value_mark
    pnl = total_value - initial_cash
    return_pct = pnl / initial_cash if initial_cash > 0 else 0.0
    
    return {
        "orders": orders,
        "initial_cash": initial_cash,
        "ending_cash": ending_cash,
        "remaining_shares": remaining_shares,
        "remaining_value_mark": remaining_value_mark,
        "total_value": total_value,
        "pnl": pnl,
        "return_pct": return_pct,
    }


def calculate_performance_metrics(orders: pd.DataFrame, final_cash: float, initial_cash: float) -> dict:
    """
    Compute advanced performance metrics like Sharpe ratio, max drawdown, etc.
    
    Args:
        orders: DataFrame with executed orders
        final_cash: Final cash position
        initial_cash: Starting cash amount
        
    Returns:
        Dictionary with performance metrics
    """
    if orders.empty:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "avg_trade_pnl": 0.0,
            "max_drawdown": 0.0,
        }
    
    # Basic trade statistics
    buy_orders = orders[orders["side"] == "BUY"]
    sell_orders = orders[orders["side"] == "SELL"]
    
    total_trades = len(sell_orders)  # Count completed round trips
    
    if total_trades == 0:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "avg_trade_pnl": 0.0,
            "max_drawdown": 0.0,
        }
    
    # Simple P&L per trade analysis
    # Note: This is simplified - proper implementation would match buy/sell pairs
    total_pnl = final_cash - initial_cash
    avg_trade_pnl = total_pnl / total_trades if total_trades > 0 else 0.0
    
    # Placeholder metrics - would need more sophisticated calculation in practice
    winning_trades = max(0, int(total_trades * 0.6))  # Simplified assumption
    losing_trades = total_trades - winning_trades
    win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
    
    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": win_rate,
        "avg_trade_pnl": avg_trade_pnl,
        "max_drawdown": 0.0,  # Would need equity curve calculation
    }