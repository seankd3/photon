"""
Base class and utilities for market data sources.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import asyncio


class MarketDataSource(ABC):
    """
    Abstract base class for market data sources.

    All connectors (Binance, Alpaca, etc.) implement this interface.
    """

    def __init__(self, name: str):
        self.name = name
        self._latest_prices: Dict[str, float] = {}
        self._lock = asyncio.Lock()
        self._connected = False

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data source."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the data source."""
        pass

    @abstractmethod
    async def subscribe(self, symbols: List[str]) -> None:
        """Subscribe to market data for the given symbols."""
        pass

    async def get_snapshot(self) -> Dict[str, float]:
        """
        Get latest prices for all subscribed symbols.

        Returns:
            Dictionary mapping symbol to price, e.g. {"BTCUSDT": 69234.1}
        """
        async with self._lock:
            return self._latest_prices.copy()

    async def _update_price(self, symbol: str, price: float) -> None:
        """Thread-safe update of a symbol's price."""
        async with self._lock:
            self._latest_prices[symbol] = price

    def is_connected(self) -> bool:
        """Check if the data source is connected."""
        return self._connected
