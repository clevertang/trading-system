from __future__ import annotations
import pandas as pd


def get_trading_days_around_date(df: pd.DataFrame, anchor_date: pd.Timestamp, 
                                before_days: int, after_days: int) -> tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    """
    Return trading dates before and after anchor_date based on data availability.
    
    Args:
        df: DataFrame with DatetimeIndex containing market data
        anchor_date: Reference date (e.g., Dec-25 for Christmas strategy)
        before_days: Number of trading days before anchor to return
        after_days: Number of trading days after anchor to return
        
    Returns:
        Tuple of (pre_dates, post_dates) as DatetimeIndex
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be DatetimeIndex.")
    
    year = anchor_date.year
    dfy = df[df.index.year == year]
    if dfy.empty:
        raise ValueError(f"No data for year {year}")
        
    dates = pd.DatetimeIndex(sorted(pd.to_datetime(dfy.index.date).unique()))
    pre = dates[dates < anchor_date]
    post = dates[dates > anchor_date]
    
    return _pick_last_n(pre, before_days), _pick_first_n(post, after_days)


def _pick_last_n(dates: pd.DatetimeIndex, n: int) -> pd.DatetimeIndex:
    """Select the last n dates from DatetimeIndex."""
    return pd.DatetimeIndex(dates[-n:]) if len(dates) >= n else dates


def _pick_first_n(dates: pd.DatetimeIndex, n: int) -> pd.DatetimeIndex:
    """Select the first n dates from DatetimeIndex."""
    return pd.DatetimeIndex(dates[:n]) if len(dates) >= n else dates


def filter_business_days(dates: pd.DatetimeIndex, market_calendar: str = "NYSE") -> pd.DatetimeIndex:
    """
    Remove weekends and holidays from date list.
    
    Args:
        dates: DatetimeIndex to filter
        market_calendar: Market calendar to use (currently only supports basic weekday filtering)
        
    Returns:
        Filtered DatetimeIndex containing only business days
    """
    # Basic implementation - filter weekends
    # In production, would integrate with pandas_market_calendars or similar
    weekdays = dates[dates.dayofweek < 5]  # Monday=0, Sunday=6
    return weekdays