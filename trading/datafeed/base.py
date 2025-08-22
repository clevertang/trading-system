from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Tuple

class MarketDataFeed(ABC):
    """Abstract market data interface so strategies/backtests can swap feeds."""

    @abstractmethod
    def history(
        self, symbol: str, start: str, end: Optional[str] = None, interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Return historical bars with a DatetimeIndex and at least columns:
        ['Open','High','Low','Close','Volume'].
        """

    @abstractmethod
    def last_price(self, symbol: str) -> Tuple[pd.Timestamp, float]:
        """
        Return (timestamp, last_trade_price) for live/order decisions.
        """
