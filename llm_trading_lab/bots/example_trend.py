"""
Example bot: Simple trend follower.

Buys when price is above the moving average, sells when below.
"""

from collections import deque

NAME = "Trend Follower"
SYMBOLS = ["BTCUSDT"]

# Global state for price history
price_history = deque(maxlen=10)  # Last 10 prices


def init(ctx):
    """Initialize the bot."""
    ctx.log("Trend follower initialized - follows 10-tick moving average")


def on_tick(ctx, tick):
    """
    Called every tick.

    Simple moving average strategy:
    - Buy when price > MA and no position
    - Sell when price < MA and have position
    """
    symbol = "BTCUSDT"
    price = ctx.get_price(symbol)

    if price is None:
        return

    # Update price history
    price_history.append(price)

    # Need at least 10 prices for moving average
    if len(price_history) < 10:
        return

    # Calculate moving average
    ma = sum(price_history) / len(price_history)

    cash = ctx.get_cash()
    position = ctx.get_position(symbol)

    # Buy signal: price above MA and no position
    if price > ma and position == 0 and cash > 100:
        # Buy 0.005 BTC
        size = 0.005
        if cash >= price * size:
            ctx.submit_order(symbol=symbol, side="BUY", size=size)
            ctx.log(f"TREND BUY {size} {symbol} @ ${price:.2f} (MA: ${ma:.2f})")

    # Sell signal: price below MA and have position
    elif price < ma and position > 0:
        # Sell entire position
        ctx.submit_order(symbol=symbol, side="SELL", size=position)
        ctx.log(f"TREND SELL {position} {symbol} @ ${price:.2f} (MA: ${ma:.2f})")
