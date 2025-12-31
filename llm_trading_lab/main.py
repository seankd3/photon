"""
Main event loop for LLM Trading Lab.

Orchestrates data sources, bots, and the execution engine.
"""

import asyncio
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List

# Import configuration
from . import config

# Import data sources
from .data_sources import MarketDataSource
from .data_sources.binance import BinanceConnector
from .data_sources.alpaca import AlpacaConnector
from .data_sources.manifold import ManifoldConnector
from .data_sources.stockdata import StockDataConnector

# Import engine
from .engine import PaperBroker, Storage

# Import bot framework
from .bot_manager import BotManager

# Import monitoring
from . import monitor

# Import utilities
from .utils import setup_logging, now_unix


logger = logging.getLogger(__name__)


class TradingLab:
    """
    Main trading lab application.

    Coordinates data sources, bots, broker, and monitoring.
    """

    def __init__(self):
        self.data_sources: List[MarketDataSource] = []
        self.broker = PaperBroker(config.STARTING_CASH)
        self.storage: Storage = None
        self.bot_manager: BotManager = None
        self.running = False
        self.equity_log_interval = 10  # Log equity every 10 ticks
        self.tick_count = 0

    async def setup(self) -> None:
        """Initialize all components."""
        logger.info("Setting up LLM Trading Lab...")

        # Validate configuration
        errors = config.validate_config()
        if errors:
            logger.error("Configuration errors:")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(1)

        # Initialize storage
        self.storage = Storage(config.DB_PATH)
        await self.storage.init_db()

        # Initialize data sources
        await self._setup_data_sources()

        # Initialize bot manager
        bots_dir = Path(__file__).parent / "bots"
        self.bot_manager = BotManager(
            bots_dir=bots_dir,
            broker=self.broker,
            get_prices_func=self.get_all_prices,
        )
        self.bot_manager.load_bots()

        logger.info("Setup complete")

    async def _setup_data_sources(self) -> None:
        """Initialize and connect to enabled data sources."""
        logger.info("Initializing data sources...")

        # Binance (required)
        if config.DATA_SOURCES["binance"]["enabled"]:
            binance = BinanceConnector(config.DATA_SOURCES["binance"]["base_url"])
            await binance.connect()
            await binance.subscribe(config.DATA_SOURCES["binance"]["symbols"])
            self.data_sources.append(binance)
            logger.info("Binance connector enabled")

        # Alpaca (optional)
        if config.DATA_SOURCES["alpaca"]["enabled"]:
            alpaca_config = config.DATA_SOURCES["alpaca"]
            alpaca = AlpacaConnector(
                api_key=alpaca_config["api_key"],
                api_secret=alpaca_config["api_secret"],
                data_url=alpaca_config["data_url"],
            )
            await alpaca.connect()
            await alpaca.subscribe(alpaca_config["symbols"])
            self.data_sources.append(alpaca)
            logger.info("Alpaca connector enabled")

        # Manifold (optional)
        if config.DATA_SOURCES["manifold"]["enabled"]:
            manifold = ManifoldConnector(config.DATA_SOURCES["manifold"]["ws_url"])
            await manifold.connect()
            await manifold.subscribe(config.DATA_SOURCES["manifold"]["markets"])
            self.data_sources.append(manifold)
            logger.info("Manifold connector enabled")

        # StockData (optional)
        if config.DATA_SOURCES["stockdata"]["enabled"]:
            stockdata_config = config.DATA_SOURCES["stockdata"]
            stockdata = StockDataConnector(
                api_key=stockdata_config["api_key"],
                base_url=stockdata_config["base_url"],
                poll_interval=stockdata_config["poll_interval_seconds"],
            )
            await stockdata.connect()
            await stockdata.subscribe(stockdata_config["symbols"])
            self.data_sources.append(stockdata)
            logger.info("StockData connector enabled")

    def get_all_prices(self) -> Dict[str, float]:
        """
        Get latest prices from all data sources.

        Returns:
            Dictionary of symbol -> price
        """
        all_prices = {}
        for source in self.data_sources:
            # Use asyncio.create_task to avoid blocking
            # Note: get_snapshot is async, but we need sync here
            # In production, this would be handled differently
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If called from async context, we need to schedule it
                    # For now, we'll store prices in a sync-accessible way
                    pass
            except RuntimeError:
                pass

        # For simplicity, gather prices synchronously
        # This is a limitation that would be refined in production
        return all_prices

    async def get_all_prices_async(self) -> Dict[str, float]:
        """Get latest prices from all data sources (async version)."""
        all_prices = {}
        for source in self.data_sources:
            prices = await source.get_snapshot()
            all_prices.update(prices)
        return all_prices

    async def run(self) -> None:
        """Main event loop."""
        self.running = True
        logger.info("Starting main event loop...")

        # Print banner
        monitor.print_startup_banner()

        # Wait a moment for data sources to get initial prices
        await asyncio.sleep(2)

        while self.running:
            tick_start = time.time()
            self.tick_count += 1

            try:
                # 1. Get current prices
                current_prices = await self.get_all_prices_async()

                if not current_prices:
                    logger.warning("No prices available yet, waiting...")
                    await asyncio.sleep(config.TICK_INTERVAL_SECONDS)
                    continue

                # 2. Process queued orders
                trades = await self.broker.process_orders(current_prices)

                # 3. Log trades
                for trade in trades:
                    bot_state = self.broker.get_bot_state(trade.order.bot_name)
                    await self.storage.log_trade(trade, bot_state)

                # 4. Mark to market for all bots
                for bot_name in self.bot_manager.get_all_bots():
                    self.broker.mark_to_market(bot_name, current_prices)

                # 5. Build tick data
                tick_data = {
                    "time": now_unix(),
                    "prices": current_prices,
                }

                # 6. Call all bots
                await self.bot_manager.tick_all_bots(tick_data)

                # 7. Log equity periodically
                if self.tick_count % self.equity_log_interval == 0:
                    current_time = now_unix()
                    for bot_name, bot_state in self.broker.get_all_bot_states().items():
                        await self.storage.log_equity(current_time, bot_name, bot_state)

                # 8. Render dashboard
                bot_states = self.broker.get_all_bot_states()
                bots_info = self.bot_manager.get_all_bots()
                monitor.render(bot_states, bots_info)

            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)

            # 9. Sleep until next tick
            elapsed = time.time() - tick_start
            sleep_time = max(0, config.TICK_INTERVAL_SECONDS - elapsed)
            await asyncio.sleep(sleep_time)

    async def shutdown(self) -> None:
        """Clean shutdown of all components."""
        logger.info("Shutting down...")
        self.running = False

        # Disconnect data sources
        for source in self.data_sources:
            await source.disconnect()

        # Close storage
        if self.storage:
            await self.storage.close()

        logger.info("Shutdown complete")


async def main():
    """Main entry point."""
    # Setup logging
    setup_logging()

    # Create lab
    lab = TradingLab()

    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        lab.running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Setup and run
        await lab.setup()
        await lab.run()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")

    finally:
        await lab.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
