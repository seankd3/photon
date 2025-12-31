"""
Paper broker / execution engine.

Manages bot portfolios, executes orders, and tracks PnL.
"""

import asyncio
import logging
from typing import Dict, List
from .models import BotState, Order, Trade

logger = logging.getLogger(__name__)


class PaperBroker:
    """
    Paper trading execution engine.
    
    Maintains state for each bot and executes market orders.
    """
    
    def __init__(self, starting_cash: float):
        self.starting_cash = starting_cash
        self._bot_states: Dict[str, BotState] = {}
        self._order_queue: asyncio.Queue = asyncio.Queue()
        self._trades: List[Trade] = []
        self._lock = asyncio.Lock()
    
    def init_bot_state(self, bot_name: str) -> BotState:
        """
        Initialize a new bot with starting cash.
        
        Args:
            bot_name: Name of the bot
            
        Returns:
            Initialized BotState
        """
        state = BotState(cash=self.starting_cash)
        self._bot_states[bot_name] = state
        logger.info(f"Initialized bot '{bot_name}' with ${self.starting_cash:,.2f}")
        return state
    
    def get_bot_state(self, bot_name: str) -> BotState:
        """Get current state for a bot."""
        if bot_name not in self._bot_states:
            return self.init_bot_state(bot_name)
        return self._bot_states[bot_name]
    
    async def enqueue_order(self, order: Order) -> None:
        """
        Queue an order for execution.
        
        Args:
            order: Order to execute
        """
        await self._order_queue.put(order)
    
    async def process_orders(self, current_prices: Dict[str, float]) -> List[Trade]:
        """
        Process all queued orders using current market prices.
        
        Args:
            current_prices: Current market prices for all symbols
            
        Returns:
            List of executed trades
        """
        trades = []
        
        # Process all orders in queue
        while not self._order_queue.empty():
            try:
                order = self._order_queue.get_nowait()
                trade = await self._execute_order(order, current_prices)
                if trade:
                    trades.append(trade)
                    self._trades.append(trade)
            except asyncio.QueueEmpty:
                break
        
        return trades
    
    async def _execute_order(self, order: Order, current_prices: Dict[str, float]) -> Trade | None:
        """
        Execute a single market order.
        
        Args:
            order: Order to execute
            current_prices: Current market prices
            
        Returns:
            Trade if successful, None if failed
        """
        async with self._lock:
            # Validate symbol has a price
            if order.symbol not in current_prices:
                logger.warning(f"No price available for {order.symbol}, skipping order")
                return None
            
            price = current_prices[order.symbol]
            state = self.get_bot_state(order.bot_name)
            
            # Validate order
            if order.size <= 0:
                logger.warning(f"Invalid order size {order.size} for {order.bot_name}")
                return None
            
            # Execute based on side
            if order.side == "BUY":
                return await self._execute_buy(order, price, state)
            elif order.side == "SELL":
                return await self._execute_sell(order, price, state)
            else:
                logger.error(f"Unknown order side: {order.side}")
                return None
    
    async def _execute_buy(self, order: Order, price: float, state: BotState) -> Trade | None:
        """Execute a BUY order."""
        required_cash = price * order.size
        
        # Check if bot has enough cash
        if state.cash < required_cash:
            logger.warning(
                f"Bot {order.bot_name} has insufficient cash: "
                f"${state.cash:.2f} < ${required_cash:.2f}"
            )
            return None
        
        # Update position and average price
        current_position = state.positions.get(order.symbol, 0.0)
        current_avg = state.avg_price.get(order.symbol, 0.0)
        
        new_position = current_position + order.size
        new_avg = ((current_avg * current_position) + (price * order.size)) / new_position
        
        state.positions[order.symbol] = new_position
        state.avg_price[order.symbol] = new_avg
        state.cash -= required_cash
        
        logger.info(
            f"{order.bot_name} BUY {order.size} {order.symbol} @ ${price:.2f} "
            f"(cash: ${state.cash:.2f})"
        )
        
        return Trade(
            order=order,
            price=price,
            cash_after=state.cash,
            position_after=new_position,
        )
    
    async def _execute_sell(self, order: Order, price: float, state: BotState) -> Trade | None:
        """Execute a SELL order."""
        current_position = state.positions.get(order.symbol, 0.0)
        
        # Don't allow short selling (position can't go negative)
        if current_position <= 0:
            logger.warning(f"Bot {order.bot_name} has no position in {order.symbol} to sell")
            return None
        
        # Limit sell size to current position
        actual_size = min(order.size, current_position)
        
        # Calculate realized PnL
        avg_price = state.avg_price.get(order.symbol, price)
        realized_pnl = (price - avg_price) * actual_size
        
        # Update state
        new_position = current_position - actual_size
        state.positions[order.symbol] = new_position
        state.cash += price * actual_size
        state.realized_pnl += realized_pnl
        
        # Clear avg price if position closed
        if new_position == 0:
            state.avg_price.pop(order.symbol, None)
        
        logger.info(
            f"{order.bot_name} SELL {actual_size} {order.symbol} @ ${price:.2f} "
            f"(PnL: ${realized_pnl:+.2f}, cash: ${state.cash:.2f})"
        )
        
        return Trade(
            order=order,
            price=price,
            cash_after=state.cash,
            position_after=new_position,
        )
    
    def mark_to_market(self, bot_name: str, current_prices: Dict[str, float]) -> None:
        """
        Update unrealized PnL and equity for a bot based on current prices.
        
        Args:
            bot_name: Name of the bot
            current_prices: Current market prices
        """
        state = self.get_bot_state(bot_name)
        
        unrealized_pnl = 0.0
        for symbol, position in state.positions.items():
            if position != 0 and symbol in current_prices:
                current_price = current_prices[symbol]
                avg_price = state.avg_price.get(symbol, current_price)
                unrealized_pnl += (current_price - avg_price) * position
        
        state.unrealized_pnl = unrealized_pnl
        
        # Calculate total position value
        position_value = 0.0
        for symbol, position in state.positions.items():
            if symbol in current_prices:
                position_value += current_prices[symbol] * position
        
        state.equity = state.cash + position_value
    
    def get_all_bot_states(self) -> Dict[str, BotState]:
        """Get states for all bots."""
        return self._bot_states.copy()
    
    def get_trades(self) -> List[Trade]:
        """Get all executed trades."""
        return self._trades.copy()
