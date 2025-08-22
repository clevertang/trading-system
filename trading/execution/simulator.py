from __future__ import annotations
import pandas as pd
from .timing import find_execution_bar, is_market_hours


def execute_orders(orders: pd.DataFrame, market_data: pd.DataFrame, 
                  slippage_bps: float = 1.0, min_liquidity_check: bool = True) -> pd.DataFrame:
    """
    Simulate order execution with realistic market microstructure effects.
    
    Args:
        orders: DataFrame with order intentions ['time', 'side', 'qty', 'price', 'value']
        market_data: DataFrame with OHLCV market data
        slippage_bps: Slippage in basis points (1.0 = 1bp = 0.01%)
        min_liquidity_check: Whether to check minimum liquidity requirements
        
    Returns:
        DataFrame with executed orders, potentially modified for realistic fills
    """
    if orders.empty:
        return orders.copy()
    
    executed_orders = []
    
    for _, order in orders.iterrows():
        try:
            # Validate order timing and market availability
            if not validate_order_timing(order, market_data):
                continue
            
            # Find actual execution bar
            execution_time = find_execution_bar(market_data, order["time"], "09:30")
            
            # Get market price at execution time
            market_bar = market_data.loc[execution_time]
            
            # Calculate execution price with slippage
            execution_price = _apply_slippage(
                intended_price=order["price"],
                market_bar=market_bar,
                side=order["side"],
                slippage_bps=slippage_bps
            )
            
            # Check liquidity constraints
            if min_liquidity_check and not _check_liquidity(order["qty"], market_bar["Volume"]):
                # Reduce order size or skip
                continue
            
            # Create executed order
            executed_order = {
                "time": execution_time,
                "side": order["side"],
                "qty": int(order["qty"]),
                "price": execution_price,
                "value": -order["qty"] * execution_price if order["side"] == "BUY" else order["qty"] * execution_price,
                "original_time": order["time"],  # Track original intention
                "slippage_bps": _calculate_slippage_bps(order["price"], execution_price)
            }
            
            executed_orders.append(executed_order)
            
        except (KeyError, RuntimeError) as e:
            # Skip orders that can't be executed (no market data, etc.)
            continue
    
    if not executed_orders:
        return pd.DataFrame(columns=orders.columns)
    
    return pd.DataFrame(executed_orders).sort_values("time").reset_index(drop=True)


def validate_order_timing(order: pd.Series, market_data: pd.DataFrame) -> bool:
    """
    Check if order timestamps align with available market data.
    Prevents look-ahead bias in backtests.
    
    Args:
        order: Single order row as pandas Series
        market_data: DataFrame with market data
        
    Returns:
        True if order timing is valid
    """
    order_date = pd.to_datetime(order["time"]).date()
    
    # Check if we have market data for this date
    market_dates = market_data.index.date
    if order_date not in market_dates:
        return False
    
    # Check if order time is during market hours (simplified)
    order_time = pd.to_datetime(order["time"])
    return is_market_hours(order_time)


def _apply_slippage(intended_price: float, market_bar: pd.Series, side: str, slippage_bps: float) -> float:
    """
    Apply realistic slippage based on market conditions.
    
    Args:
        intended_price: Price from strategy signal
        market_bar: OHLCV data for execution bar
        side: "BUY" or "SELL"
        slippage_bps: Slippage in basis points
        
    Returns:
        Adjusted execution price
    """
    slippage_multiplier = slippage_bps / 10000.0  # Convert bps to decimal
    
    if side == "BUY":
        # Buyers typically pay higher prices (positive slippage)
        execution_price = intended_price * (1 + slippage_multiplier)
        # Cap at high of bar
        return min(execution_price, market_bar["High"])
    else:  # SELL
        # Sellers typically receive lower prices (negative slippage)
        execution_price = intended_price * (1 - slippage_multiplier)
        # Floor at low of bar
        return max(execution_price, market_bar["Low"])


def _check_liquidity(order_qty: int, bar_volume: float, max_volume_pct: float = 0.01) -> bool:
    """
    Check if order size is reasonable relative to market volume.
    
    Args:
        order_qty: Number of shares to trade
        bar_volume: Volume in the execution bar
        max_volume_pct: Maximum percentage of bar volume to trade
        
    Returns:
        True if order passes liquidity check
    """
    if bar_volume <= 0:
        return False
    
    volume_pct = order_qty / bar_volume
    return volume_pct <= max_volume_pct


def _calculate_slippage_bps(intended_price: float, execution_price: float) -> float:
    """Calculate realized slippage in basis points."""
    if intended_price == 0:
        return 0.0
    
    slippage = (execution_price - intended_price) / intended_price
    return slippage * 10000.0  # Convert to basis points