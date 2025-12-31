"""
Bot framework: BotContext and bot loader.

Provides the API that bots use to interact with the trading lab.
"""

import asyncio
import importlib.util
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any

from .engine.broker import PaperBroker
from .engine.models import Order

logger = logging.getLogger(__name__)


class BotContext:
    """
    Context object provided to bots.

    Bots use this to:
    - Query prices, cash, positions
    - Submit orders
    - Log messages
    """

    def __init__(self, bot_name: str, broker: PaperBroker, get_prices_func: Callable):
        self.bot_name = bot_name
        self._broker = broker
        self._get_prices = get_prices_func

    def get_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price for a symbol.

        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")

        Returns:
            Current price, or None if not available
        """
        prices = self._get_prices()
        return prices.get(symbol)

    def get_position(self, symbol: str) -> float:
        """
        Get current position size for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Position size (positive for long, 0 for no position)
        """
        state = self._broker.get_bot_state(self.bot_name)
        return state.positions.get(symbol, 0.0)

    def get_cash(self) -> float:
        """
        Get available cash balance.

        Returns:
            Cash balance
        """
        state = self._broker.get_bot_state(self.bot_name)
        return state.cash

    def submit_order(self, symbol: str, side: str, size: float) -> None:
        """
        Submit a market order.

        Args:
            symbol: Trading symbol
            side: "BUY" or "SELL"
            size: Order size (quantity)
        """
        order = Order(
            bot_name=self.bot_name,
            symbol=symbol,
            side=side,
            size=size,
            time=time.time(),
        )

        # Queue order (async operation called from sync context)
        asyncio.create_task(self._broker.enqueue_order(order))

        logger.info(f"{self.bot_name} submitted {side} {size} {symbol}")

    def log(self, message: str) -> None:
        """
        Log a message from the bot.

        Args:
            message: Message to log
        """
        logger.info(f"[{self.bot_name}] {message}")


class LoadedBot:
    """Represents a loaded bot module."""

    def __init__(
        self,
        name: str,
        symbols: List[str],
        init_func: Optional[Callable],
        on_tick_func: Callable,
        module_path: str,
    ):
        self.name = name
        self.symbols = symbols
        self.init_func = init_func
        self.on_tick_func = on_tick_func
        self.module_path = module_path
        self.status = "RUNNING"
        self.last_tick_time = 0.0
        self.last_error: Optional[str] = None


class BotManager:
    """
    Manages loading and execution of trading bots.
    """

    def __init__(self, bots_dir: Path, broker: PaperBroker, get_prices_func: Callable):
        self.bots_dir = bots_dir
        self.broker = broker
        self._get_prices = get_prices_func
        self._bots: Dict[str, LoadedBot] = {}
        self._contexts: Dict[str, BotContext] = {}

    def load_bots(self) -> None:
        """
        Scan bots directory and load all bot modules.

        Looks for .py files (excluding those starting with _).
        """
        if not self.bots_dir.exists():
            logger.warning(f"Bots directory does not exist: {self.bots_dir}")
            return

        for bot_file in self.bots_dir.glob("*.py"):
            # Skip private modules
            if bot_file.name.startswith("_"):
                continue

            try:
                self._load_bot(bot_file)
            except Exception as e:
                logger.error(f"Failed to load bot {bot_file}: {e}", exc_info=True)

        logger.info(f"Loaded {len(self._bots)} bot(s)")

    def _load_bot(self, bot_file: Path) -> None:
        """Load a single bot module."""
        module_name = bot_file.stem

        # Import module
        spec = importlib.util.spec_from_file_location(module_name, bot_file)
        if not spec or not spec.loader:
            raise ValueError(f"Failed to load spec for {bot_file}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Validate required attributes
        if not hasattr(module, "NAME"):
            raise ValueError(f"Bot {module_name} missing NAME constant")
        if not hasattr(module, "SYMBOLS"):
            raise ValueError(f"Bot {module_name} missing SYMBOLS constant")
        if not hasattr(module, "on_tick"):
            raise ValueError(f"Bot {module_name} missing on_tick function")

        bot_name = module.NAME
        symbols = module.SYMBOLS
        init_func = getattr(module, "init", None)
        on_tick_func = module.on_tick

        # Create bot context
        context = BotContext(bot_name, self.broker, self._get_prices)
        self._contexts[bot_name] = context

        # Initialize bot if it has init function
        if init_func:
            try:
                init_func(context)
                logger.info(f"Initialized bot '{bot_name}'")
            except Exception as e:
                logger.error(f"Error initializing bot '{bot_name}': {e}", exc_info=True)

        # Register bot
        bot = LoadedBot(bot_name, symbols, init_func, on_tick_func, str(bot_file))
        self._bots[bot_name] = bot

        logger.info(f"Loaded bot '{bot_name}' from {bot_file.name}")

    async def tick_all_bots(self, tick_data: Dict[str, Any]) -> None:
        """
        Call on_tick for all active bots.

        Args:
            tick_data: Tick data dictionary to pass to bots
        """
        for bot_name, bot in self._bots.items():
            if bot.status != "RUNNING":
                continue

            try:
                context = self._contexts[bot_name]

                # Add bot-specific data to tick
                bot_tick = tick_data.copy()
                bot_tick["bot"] = {
                    "cash": context.get_cash(),
                    "positions": self.broker.get_bot_state(bot_name).positions.copy(),
                    "equity": self.broker.get_bot_state(bot_name).equity,
                    "realized_pnl": self.broker.get_bot_state(bot_name).realized_pnl,
                    "unrealized_pnl": self.broker.get_bot_state(bot_name).unrealized_pnl,
                }

                # Call bot's on_tick
                bot.on_tick_func(context, bot_tick)
                bot.last_tick_time = time.time()
                bot.last_error = None

            except Exception as e:
                error_msg = f"Error in bot '{bot_name}' on_tick: {e}"
                logger.error(error_msg, exc_info=True)
                bot.last_error = str(e)

    def pause_bot(self, bot_name: str) -> bool:
        """Pause a bot."""
        if bot_name in self._bots:
            self._bots[bot_name].status = "STOPPED"
            logger.info(f"Paused bot '{bot_name}'")
            return True
        return False

    def resume_bot(self, bot_name: str) -> bool:
        """Resume a bot."""
        if bot_name in self._bots:
            self._bots[bot_name].status = "RUNNING"
            logger.info(f"Resumed bot '{bot_name}'")
            return True
        return False

    def get_all_bots(self) -> Dict[str, LoadedBot]:
        """Get all loaded bots."""
        return self._bots.copy()
