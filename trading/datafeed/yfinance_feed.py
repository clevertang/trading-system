# trading/marketdata/yfinance_feed.py
from __future__ import annotations
import pandas as pd
import yfinance as yf
from typing import Optional, Tuple
from .base import MarketDataFeed

class YFinanceFeed(MarketDataFeed):
    """Yahoo Finance feed for quick prototyping."""

    def history(
        self, symbol: str, start: str, end: Optional[str] = None, interval: str = "1d"
    ) -> pd.DataFrame:
        df = yf.download(symbol, start=start, end=end, interval=interval, progress=False)
        # Ensure expected columns exist
        expected = {"Open", "High", "Low", "Close", "Volume"}
        if not expected.issubset(df.columns):
            raise ValueError(f"Missing columns from yfinance response: {df.columns}")
        # Normalize index to tz-naive for simplicity
        df.index = pd.to_datetime(df.index).tz_localize(None)
        return df

    def last_price(self, symbol: str) -> Tuple[pd.Timestamp, float]:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        if df.empty:
            raise RuntimeError("No intraday data returned.")
        ts = pd.to_datetime(df.index[-1]).to_pydatetime()
        return (pd.Timestamp(ts), float(df["Close"].iloc[-1]))
