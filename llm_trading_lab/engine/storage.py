"""
SQLite storage for trade and equity logging.
"""

import aiosqlite
import logging
from typing import Optional
from .models import Trade, BotState

logger = logging.getLogger(__name__)


class Storage:
    """
    SQLite storage layer for persisting trades and equity snapshots.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def init_db(self) -> None:
        """Initialize database and create tables if they don't exist."""
        self._db = await aiosqlite.connect(self.db_path)

        # Create trades table
        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time REAL NOT NULL,
                bot_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                size REAL NOT NULL,
                price REAL NOT NULL,
                cash_after REAL NOT NULL,
                position_after REAL NOT NULL
            )
        """
        )

        # Create equity table
        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS equity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time REAL NOT NULL,
                bot_name TEXT NOT NULL,
                equity REAL NOT NULL,
                realized_pnl REAL NOT NULL,
                unrealized_pnl REAL NOT NULL
            )
        """
        )

        await self._db.commit()
        logger.info(f"Database initialized: {self.db_path}")

    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()
            logger.info("Database connection closed")

    async def log_trade(self, trade: Trade, bot_state: BotState) -> None:
        """
        Log a trade to the database.

        Args:
            trade: Trade to log
            bot_state: Bot state after trade
        """
        if not self._db:
            logger.error("Database not initialized")
            return

        await self._db.execute(
            """
            INSERT INTO trades
            (time, bot_name, symbol, side, size, price, cash_after, position_after)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trade.order.time,
                trade.order.bot_name,
                trade.order.symbol,
                trade.order.side,
                trade.order.size,
                trade.price,
                trade.cash_after,
                trade.position_after,
            ),
        )
        await self._db.commit()

    async def log_equity(self, time: float, bot_name: str, bot_state: BotState) -> None:
        """
        Log an equity snapshot to the database.

        Args:
            time: Unix timestamp
            bot_name: Name of the bot
            bot_state: Current bot state
        """
        if not self._db:
            logger.error("Database not initialized")
            return

        await self._db.execute(
            """
            INSERT INTO equity (time, bot_name, equity, realized_pnl, unrealized_pnl)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                time,
                bot_name,
                bot_state.equity,
                bot_state.realized_pnl,
                bot_state.unrealized_pnl,
            ),
        )
        await self._db.commit()
