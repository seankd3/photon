"""
Example bot: Random trader.

Randomly decides to buy or sell with small position sizes.
"""

import random

NAME = "Random Trader"
SYMBOLS = ["BTCUSDT"]


def init(ctx):
    """Initialize the bot."""
    ctx.log("Random trader initialized - trades randomly!")


def on_tick(ctx, tick):
    """
    Called every tick.
    
    Randomly decides whether to trade.
    """
    # Only trade occasionally (10% chance per tick)
    if random.random() > 0.1:
        return
    
    symbol = "BTCUSDT"
    price = ctx.get_price(symbol)
    
    if price is None:
        return
    
    cash = ctx.get_cash()
    position = ctx.get_position(symbol)
    
    # Randomly buy or sell
    action = random.choice(["BUY", "SELL", "NOTHING"])
    
    if action == "BUY" and cash > 100:
        # Buy a small amount (0.001 BTC)
        size = 0.001
        if cash >= price * size:
            ctx.submit_order(symbol=symbol, side="BUY", size=size)
            ctx.log(f"Random BUY {size} {symbol} @ ${price:.2f}")
    
    elif action == "SELL" and position > 0:
        # Sell half of position
        size = position * 0.5
        if size > 0:
            ctx.submit_order(symbol=symbol, side="SELL", size=size)
            ctx.log(f"Random SELL {size} {symbol} @ ${price:.2f}")
