from __future__ import annotations
import pandas as pd


def find_execution_bar(df: pd.DataFrame, target_date: pd.Timestamp, time_str: str) -> pd.Timestamp:
    """
    Pick the bar at the requested time; fallback to the last bar of that day.
    
    Args:
        df: DataFrame with DatetimeIndex containing market data
        target_date: Date to find execution bar for
        time_str: Target time in "HH:MM" format (e.g., "10:30")
        
    Returns:
        Timestamp of the closest available bar for execution
        
    Raises:
        RuntimeError: If no bars exist for the target date
    """
    same_day = df[df.index.date == target_date.date()]
    if same_day.empty:
        raise RuntimeError(f"No bars on {target_date.date()}")
    
    # If only one bar for the day (e.g., daily data), use it
    if len(same_day) == 1:
        return same_day.index[0]
    
    # Try to find bar at or after the target time
    target_time = pd.Timestamp(f"{target_date.date()} {time_str}")
    later_bars = same_day.index[same_day.index >= target_time]
    
    # Return first bar at or after target time, or last bar of day if none found
    return later_bars[0] if len(later_bars) else same_day.index[-1]


def get_market_open_close(df: pd.DataFrame, date: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Determine market session boundaries for given date.
    
    Args:
        df: DataFrame with intraday market data
        date: Date to get session boundaries for
        
    Returns:
        Tuple of (market_open, market_close) timestamps
        
    Raises:
        RuntimeError: If no data exists for the given date
    """
    same_day = df[df.index.date == date.date()]
    if same_day.empty:
        raise RuntimeError(f"No market data for {date.date()}")
    
    market_open = same_day.index[0]
    market_close = same_day.index[-1]
    
    return market_open, market_close


def is_market_hours(timestamp: pd.Timestamp, market_open: str = "09:30", market_close: str = "16:00") -> bool:
    """
    Check if timestamp falls within market hours.
    
    Args:
        timestamp: Timestamp to check
        market_open: Market open time in "HH:MM" format
        market_close: Market close time in "HH:MM" format
        
    Returns:
        True if timestamp is within market hours
    """
    time_str = timestamp.strftime("%H:%M")
    return market_open <= time_str <= market_close