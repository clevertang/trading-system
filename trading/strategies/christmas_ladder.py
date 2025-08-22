# trading/strategies/tangxin_demo.py
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

from ..utils.calendar import get_trading_days_around_date
from ..execution.timing import find_execution_bar

@dataclass
class XmasParams:
    year: int
    symbol: str
    buy_days: int = 5                 # number of trading days BEFORE Dec-25 to accumulate
    sell_days: int = 10               # number of trading days AFTER Dec-25 to distribute
    sell_execution_time: str = "10:30"  # local exchange time to execute sales


def generate_orders(df: pd.DataFrame, cash: float, p: XmasParams) -> pd.DataFrame:
    """
    Create orders for the Xmas ladder strategy:
      - Accumulate equal notional on the last `buy_days` trading days before Dec-25 (use 'close' of the day).
      - Starting from the first trading day after Dec-25, sell 1/10 of remaining shares each day at `sell_execution_time`.
    """
    # Use utility functions for date calculations
    xmas = pd.Timestamp(year=p.year, month=12, day=25)
    buy_dates, sell_dates = get_trading_days_around_date(df, xmas, p.buy_days, p.sell_days)

    orders = []
    position = 0
    # Buys (use day close = last bar of the day)
    alloc = cash / max(len(buy_dates), 1)
    for d in buy_dates:
        bars = df[df.index.date == d.date()]
        ts = bars.index[-1]
        px = float(df.loc[ts, "Close"])
        qty = int(alloc // px)
        if qty <= 0:
            continue
        orders.append({"time": ts, "side": "BUY", "qty": qty, "price": px, "value": -qty * px})
        cash -= qty * px
        position += qty

    # Sells (10:30 or closest bar)
    for i, d in enumerate(sell_dates, start=1):
        if position <= 0:
            break
        sell_qty = position // (p.sell_days - i + 1) if i < p.sell_days else position
        if sell_qty <= 0:
            continue
        ts = find_execution_bar(df, d, p.sell_execution_time)
        px = float(df.loc[ts, "Close"])
        orders.append({"time": ts, "side": "SELL", "qty": int(sell_qty), "price": px, "value": sell_qty * px})
        cash += sell_qty * px
        position -= sell_qty

    if not orders:
        return pd.DataFrame(columns=["time", "side", "qty", "price", "value"])
    
    return (pd.DataFrame(orders)
            .sort_values("time")
            .reset_index(drop=True))


