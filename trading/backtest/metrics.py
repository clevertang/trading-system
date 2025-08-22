from __future__ import annotations
import pandas as pd
import numpy as np


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate annualized Sharpe ratio from return series.
    
    Args:
        returns: Series of periodic returns
        risk_free_rate: Annual risk-free rate (default 2%)
        
    Returns:
        Annualized Sharpe ratio
    """
    if returns.empty or returns.std() == 0:
        return 0.0
    
    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)


def calculate_max_drawdown(equity_curve: pd.Series) -> dict:
    """
    Calculate maximum drawdown and related statistics.
    
    Args:
        equity_curve: Series of portfolio values over time
        
    Returns:
        Dictionary with max_drawdown, drawdown_duration, recovery_time
    """
    if equity_curve.empty:
        return {"max_drawdown": 0.0, "drawdown_duration": 0, "recovery_time": 0}
    
    # Calculate running maximum (peak)
    peak = equity_curve.expanding().max()
    
    # Calculate drawdown as percentage from peak
    drawdown = (equity_curve - peak) / peak
    
    max_drawdown = drawdown.min()
    
    # Find longest drawdown period
    in_drawdown = drawdown < 0
    drawdown_periods = []
    start = None
    
    for i, is_dd in enumerate(in_drawdown):
        if is_dd and start is None:
            start = i
        elif not is_dd and start is not None:
            drawdown_periods.append(i - start)
            start = None
    
    # Handle case where drawdown continues to end
    if start is not None:
        drawdown_periods.append(len(in_drawdown) - start)
    
    max_duration = max(drawdown_periods) if drawdown_periods else 0
    
    return {
        "max_drawdown": abs(max_drawdown),
        "drawdown_duration": max_duration,
        "recovery_time": max_duration,  # Simplified - same as duration
    }


def calculate_win_loss_metrics(trades: pd.DataFrame) -> dict:
    """
    Calculate win/loss statistics from completed trades.
    
    Args:
        trades: DataFrame with trade P&L information
        
    Returns:
        Dictionary with win rate, average win/loss, profit factor
    """
    if trades.empty or "pnl" not in trades.columns:
        return {
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 0.0,
            "total_trades": 0,
        }
    
    winning_trades = trades[trades["pnl"] > 0]
    losing_trades = trades[trades["pnl"] < 0]
    
    total_trades = len(trades)
    win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0.0
    
    avg_win = winning_trades["pnl"].mean() if not winning_trades.empty else 0.0
    avg_loss = abs(losing_trades["pnl"].mean()) if not losing_trades.empty else 0.0
    
    gross_profit = winning_trades["pnl"].sum() if not winning_trades.empty else 0.0
    gross_loss = abs(losing_trades["pnl"].sum()) if not losing_trades.empty else 0.0
    
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
    
    return {
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "total_trades": total_trades,
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
    }


def calculate_volatility_metrics(returns: pd.Series) -> dict:
    """
    Calculate various volatility and risk metrics.
    
    Args:
        returns: Series of periodic returns
        
    Returns:
        Dictionary with volatility statistics
    """
    if returns.empty:
        return {
            "daily_volatility": 0.0,
            "annual_volatility": 0.0,
            "skewness": 0.0,
            "kurtosis": 0.0,
        }
    
    daily_vol = returns.std()
    annual_vol = daily_vol * np.sqrt(252)
    
    return {
        "daily_volatility": daily_vol,
        "annual_volatility": annual_vol,
        "skewness": returns.skew(),
        "kurtosis": returns.kurtosis(),
    }


def calculate_performance_summary(orders: pd.DataFrame, initial_capital: float, 
                                final_capital: float, benchmark_returns: pd.Series = None) -> dict:
    """
    Calculate comprehensive performance summary.
    
    Args:
        orders: DataFrame with executed orders
        initial_capital: Starting capital
        final_capital: Ending capital
        benchmark_returns: Optional benchmark return series for comparison
        
    Returns:
        Dictionary with comprehensive performance metrics
    """
    if orders.empty:
        return {
            "total_return": 0.0,
            "annual_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
        }
    
    # Calculate basic returns
    total_return = (final_capital - initial_capital) / initial_capital
    
    # Estimate annualized return (simplified)
    days_elapsed = (orders["time"].max() - orders["time"].min()).days
    annual_return = (1 + total_return) ** (365 / max(days_elapsed, 1)) - 1 if days_elapsed > 0 else 0.0
    
    # Create simplified equity curve from orders
    equity_curve = pd.Series(index=orders["time"], data=initial_capital)
    cumulative_pnl = 0
    
    for _, order in orders.iterrows():
        cumulative_pnl += order["value"]
        equity_curve[order["time"]] = initial_capital + cumulative_pnl
    
    # Calculate returns series
    returns = equity_curve.pct_change().dropna()
    
    # Calculate individual metrics
    sharpe = calculate_sharpe_ratio(returns)
    drawdown_metrics = calculate_max_drawdown(equity_curve)
    
    # Create trade-level data for win/loss analysis (simplified)
    trade_pnl = orders[orders["side"] == "SELL"]["value"]  # Only count completed sales
    trades_df = pd.DataFrame({"pnl": trade_pnl}) if not trade_pnl.empty else pd.DataFrame()
    win_loss_metrics = calculate_win_loss_metrics(trades_df)
    
    vol_metrics = calculate_volatility_metrics(returns)
    
    # Combine all metrics
    summary = {
        "total_return": total_return,
        "annual_return": annual_return,
        "sharpe_ratio": sharpe,
        "max_drawdown": drawdown_metrics["max_drawdown"],
        "win_rate": win_loss_metrics["win_rate"],
        "profit_factor": win_loss_metrics["profit_factor"],
        "annual_volatility": vol_metrics["annual_volatility"],
        "total_trades": win_loss_metrics["total_trades"],
    }
    
    # Add benchmark comparison if provided
    if benchmark_returns is not None and not benchmark_returns.empty:
        bench_total_return = (1 + benchmark_returns).prod() - 1
        summary["benchmark_return"] = bench_total_return
        summary["excess_return"] = total_return - bench_total_return
        summary["information_ratio"] = (returns.mean() - benchmark_returns.mean()) / (returns - benchmark_returns).std()
    
    return summary