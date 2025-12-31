"""
Data models for the trading engine.
"""

from dataclasses import dataclass, field
from typing import Dict, Literal


@dataclass
class BotState:
    """
    Represents the current state of a trading bot.
    """

    cash: float
    positions: Dict[str, float] = field(default_factory=dict)  # symbol -> size
    avg_price: Dict[str, float] = field(default_factory=dict)  # symbol -> avg entry price
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    equity: float = 0.0


@dataclass
class Order:
    """
    Represents a market order submitted by a bot.
    """

    bot_name: str
    symbol: str
    side: Literal["BUY", "SELL"]
    size: float
    time: float


@dataclass
class Trade:
    """
    Represents an executed trade (filled order).
    """

    order: Order
    price: float  # Execution price
    cash_after: float
    position_after: float


@dataclass
class EquitySnapshot:
    """
    Represents a point-in-time snapshot of bot equity.
    """

    time: float
    bot_name: str
    equity: float
    realized_pnl: float
    unrealized_pnl: float
