"""
StockData.org connector (optional).

Polls StockData.org API for low-frequency equity data.
Free plan: 100 requests/day.
"""

import asyncio
import logging
from typing import List
import aiohttp

from . import MarketDataSource


logger = logging.getLogger(__name__)


class StockDataConnector(MarketDataSource):
    """
    StockData.org REST API connector for low-frequency equities.
    
    Polls the API periodically (respecting rate limits).
    """
    
    def __init__(self, api_key: str, base_url: str, poll_interval: float):
        super().__init__("stockdata")
        self.api_key = api_key
        self.base_url = base_url
        self.poll_interval = poll_interval
        self._symbols: List[str] = []
        self._task = None
    
    async def connect(self) -> None:
        """Initialize StockData connector."""
        logger.info("StockData connector initialized")
        self._connected = True
    
    async def disconnect(self) -> None:
        """Disconnect from StockData."""
        logger.info("Disconnecting from StockData")
        self._connected = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("StockData disconnected")
    
    async def subscribe(self, symbols: List[str]) -> None:
        """
        Subscribe to StockData symbols (start polling).
        
        Args:
            symbols: List of symbols, e.g. ["SPY", "QQQ"]
        """
        self._symbols = symbols
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(f"Subscribed to StockData symbols: {symbols}")
    
    async def _poll_loop(self) -> None:
        """Poll StockData API at configured interval."""
        logger.warning("StockData connector is a placeholder - not yet fully implemented")
        
        while self._connected:
            # Placeholder: would make actual API requests here
            for symbol in self._symbols:
                await self._update_price(symbol, 400.0)  # Dummy price
            
            await asyncio.sleep(self.poll_interval)
