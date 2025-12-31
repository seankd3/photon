"""
Binance market data connector.

Connects to Binance WebSocket streams to get real-time crypto prices.
No authentication required - uses public market data endpoints.
"""

import asyncio
import json
import logging
from typing import List
import websockets

from . import MarketDataSource


logger = logging.getLogger(__name__)


class BinanceConnector(MarketDataSource):
    """
    Binance WebSocket connector for real-time crypto market data.

    Uses public ticker streams that don't require authentication.
    Example: wss://stream.binance.com:9443/ws/btcusdt@ticker
    """

    def __init__(self, base_url: str = "wss://stream.binance.com:9443/ws"):
        super().__init__("binance")
        self.base_url = base_url
        self._ws = None
        self._symbols: List[str] = []
        self._tasks = []

    async def connect(self) -> None:
        """Establish connection (actual connection happens in subscribe)."""
        logger.info("Binance connector initialized")
        self._connected = True

    async def disconnect(self) -> None:
        """Close WebSocket connections and cancel tasks."""
        logger.info("Disconnecting from Binance")
        self._connected = False

        # Cancel all running tasks
        for task in self._tasks:
            task.cancel()

        # Wait for tasks to complete cancellation
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        self._tasks.clear()
        logger.info("Binance disconnected")

    async def subscribe(self, symbols: List[str]) -> None:
        """
        Subscribe to ticker streams for the given symbols.

        Args:
            symbols: List of symbols to subscribe to, e.g. ["BTCUSDT", "ETHUSDT"]
        """
        self._symbols = symbols

        # Start a WebSocket connection for each symbol
        for symbol in symbols:
            task = asyncio.create_task(self._subscribe_symbol(symbol))
            self._tasks.append(task)
            logger.info(f"Subscribed to Binance {symbol}")

    async def _subscribe_symbol(self, symbol: str) -> None:
        """
        Subscribe to a single symbol's ticker stream.

        Reconnects automatically on disconnection.
        """
        stream_name = f"{symbol.lower()}@ticker"
        ws_url = f"{self.base_url}/{stream_name}"

        while self._connected:
            try:
                async with websockets.connect(ws_url) as websocket:
                    logger.info(f"Connected to Binance stream: {symbol}")

                    async for message in websocket:
                        if not self._connected:
                            break

                        try:
                            data = json.loads(message)

                            # Binance ticker format:
                            # {"s": "BTCUSDT", "c": "69234.10", ...}
                            # 's' = symbol, 'c' = current price
                            if "c" in data:
                                price = float(data["c"])
                                await self._update_price(symbol, price)
                                logger.debug(f"Updated {symbol}: {price}")

                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse message: {message}")
                        except (KeyError, ValueError) as e:
                            logger.error(f"Failed to extract price from {data}: {e}")

            except websockets.exceptions.WebSocketException as e:
                logger.error(f"WebSocket error for {symbol}: {e}")
                if self._connected:
                    logger.info(f"Reconnecting to {symbol} in 5 seconds...")
                    await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Unexpected error for {symbol}: {e}", exc_info=True)
                if self._connected:
                    await asyncio.sleep(5)
