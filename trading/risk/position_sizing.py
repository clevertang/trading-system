from __future__ import annotations
import pandas as pd


def calculate_position_size(available_cash: float, target_allocation: float, 
                          current_price: float, max_position_pct: float = 0.1) -> int:
    """
    Determine appropriate position size based on risk parameters.
    
    Args:
        available_cash: Cash available for investment
        target_allocation: Dollar amount to allocate to this position
        current_price: Current price per share
        max_position_pct: Maximum percentage of available cash for single position
        
    Returns:
        Number of shares to purchase (integer)
    """
    if current_price <= 0 or available_cash <= 0:
        return 0
    
    # Apply maximum position size constraint
    max_allocation = available_cash * max_position_pct
    actual_allocation = min(target_allocation, max_allocation)
    
    # Calculate shares, rounded down to avoid exceeding allocation
    shares = int(actual_allocation // current_price)
    
    return max(0, shares)


def check_margin_requirements(orders: pd.DataFrame, available_cash: float, 
                            margin_multiplier: float = 1.0) -> bool:
    """
    Validate that orders don't exceed buying power.
    
    Args:
        orders: DataFrame with pending orders
        available_cash: Available cash for trading
        margin_multiplier: Buying power multiplier (1.0 = cash account, 2.0 = margin)
        
    Returns:
        True if orders can be executed within margin requirements
    """
    if orders.empty:
        return True
    
    # Calculate total cash requirement for buy orders
    buy_orders = orders[orders["side"] == "BUY"]
    if buy_orders.empty:
        return True
    
    total_cash_needed = (buy_orders["qty"] * buy_orders["price"]).sum()
    buying_power = available_cash * margin_multiplier
    
    return total_cash_needed <= buying_power


def validate_position_concentration(orders: pd.DataFrame, portfolio_value: float,
                                  max_single_position_pct: float = 0.1,
                                  max_sector_pct: float = 0.3) -> dict:
    """
    Check position concentration limits to prevent over-concentration.
    
    Args:
        orders: DataFrame with order details including symbol
        portfolio_value: Total portfolio value
        max_single_position_pct: Maximum percentage for single position
        max_sector_pct: Maximum percentage for single sector (simplified)
        
    Returns:
        Dictionary with validation results and warnings
    """
    if orders.empty or portfolio_value <= 0:
        return {"valid": True, "warnings": []}
    
    warnings = []
    
    # Group orders by symbol to check individual position sizes
    if "symbol" in orders.columns:
        symbol_exposure = orders.groupby("symbol").apply(
            lambda x: (x["qty"] * x["price"]).sum()
        )
        
        for symbol, exposure in symbol_exposure.items():
            exposure_pct = exposure / portfolio_value
            if exposure_pct > max_single_position_pct:
                warnings.append(
                    f"Position in {symbol} ({exposure_pct:.1%}) exceeds single position limit ({max_single_position_pct:.1%})"
                )
    
    return {
        "valid": len(warnings) == 0,
        "warnings": warnings,
        "max_single_exposure": symbol_exposure.max() / portfolio_value if "symbol" in orders.columns and not symbol_exposure.empty else 0.0
    }


def apply_kelly_criterion(win_rate: float, avg_win: float, avg_loss: float, 
                         current_capital: float, max_kelly_fraction: float = 0.25) -> float:
    """
    Calculate optimal position size using Kelly Criterion.
    
    Args:
        win_rate: Historical win rate (0.0 to 1.0)
        avg_win: Average winning trade amount
        avg_loss: Average losing trade amount (positive number)
        current_capital: Current available capital
        max_kelly_fraction: Maximum fraction of capital to risk (cap on Kelly)
        
    Returns:
        Recommended capital allocation for next trade
    """
    if avg_loss <= 0 or win_rate <= 0 or win_rate >= 1:
        return 0.0
    
    # Kelly formula: f = (bp - q) / b
    # where b = odds received (avg_win/avg_loss), p = win_rate, q = 1-p
    b = avg_win / avg_loss  # Odds ratio
    p = win_rate
    q = 1 - win_rate
    
    kelly_fraction = (b * p - q) / b
    
    # Apply safety caps
    kelly_fraction = max(0.0, min(kelly_fraction, max_kelly_fraction))
    
    return current_capital * kelly_fraction