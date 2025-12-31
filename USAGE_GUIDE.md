# LLM Trading Lab - Usage Guide

This guide walks you through using the LLM Trading Lab to test trading bots with real market data.

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Sean-Kenneth-Doherty/photon
cd photon

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Lab

```bash
# Run with default configuration (Binance crypto data)
python -m llm_trading_lab.main
```

The lab will:
1. Connect to Binance WebSocket streams for BTC and ETH prices
2. Load all bots from `llm_trading_lab/bots/` directory
3. Start the main event loop (1 tick per second by default)
4. Display a real-time CLI dashboard showing bot performance

### 3. Stop the Lab

Press `Ctrl+C` to gracefully shut down the lab. All data is automatically saved to `lab.db`.

## Writing Your First Bot

### Basic Bot Structure

Create a new file in `llm_trading_lab/bots/`, for example `my_bot.py`:

```python
"""
My first trading bot.
"""

NAME = "My Bot"
SYMBOLS = ["BTCUSDT"]  # Which markets to trade


def init(ctx):
    """Optional: Called once when bot loads."""
    ctx.log("My bot is ready!")


def on_tick(ctx, tick):
    """Called every tick (default: 1 second)."""
    # Get current price
    price = ctx.get_price("BTCUSDT")
    if price is None:
        return
    
    # Get bot state
    cash = ctx.get_cash()
    position = ctx.get_position("BTCUSDT")
    
    # Simple strategy: buy if price drops below 60k
    if price < 60000 and position == 0 and cash > 1000:
        ctx.submit_order(symbol="BTCUSDT", side="BUY", size=0.01)
        ctx.log(f"Bought at {price}")
    
    # Sell if price goes above 70k
    elif price > 70000 and position > 0:
        ctx.submit_order(symbol="BTCUSDT", side="SELL", size=position)
        ctx.log(f"Sold at {price}")
```

### Bot API Reference

#### Context Methods

**`ctx.get_price(symbol: str) -> float | None`**
- Get current market price for a symbol
- Returns `None` if no price available

**`ctx.get_cash() -> float`**
- Get available cash balance

**`ctx.get_position(symbol: str) -> float`**
- Get current position size for a symbol
- Returns 0 if no position

**`ctx.submit_order(symbol: str, side: str, size: float) -> None`**
- Submit a market order
- `side`: "BUY" or "SELL"
- `size`: Quantity to trade

**`ctx.log(message: str) -> None`**
- Log a message (appears in console)

#### Tick Data Structure

The `tick` parameter passed to `on_tick()` contains:

```python
{
    "time": 1704067200.0,  # Unix timestamp
    "prices": {
        "BTCUSDT": 69234.1,
        "ETHUSDT": 3456.7
    },
    "bot": {
        "cash": 10000.0,
        "positions": {"BTCUSDT": 0.01},
        "equity": 10692.34,
        "realized_pnl": 50.0,
        "unrealized_pnl": 642.34
    }
}
```

## Configuration

Edit `llm_trading_lab/config.py` to customize:

### Starting Capital

```python
STARTING_CASH = 10_000.0  # Default: $10,000 per bot
```

### Tick Interval

```python
TICK_INTERVAL_SECONDS = 1.0  # How often bots are called
```

### Enable/Disable Data Sources

```python
DATA_SOURCES = {
    "binance": {
        "enabled": True,  # Always enabled by default
        "symbols": ["BTCUSDT", "ETHUSDT"],
    },
    "alpaca": {
        "enabled": False,  # Set to True if you have API keys
        "symbols": ["AAPL", "TSLA"],
    },
}
```

### Database Path

```python
DB_PATH = "lab.db"  # SQLite database for trade history
```

## Data Sources

### Binance (Default)

**No setup required!** Works out of the box with real-time crypto prices.

Supported symbols: Any crypto pair on Binance Spot (BTCUSDT, ETHUSDT, etc.)

### Alpaca (Optional)

For US stocks and crypto with paper trading:

1. Sign up for free paper trading account at [alpaca.markets](https://alpaca.markets)
2. Get API key and secret
3. Create `.env` file:
   ```
   ALPACA_API_KEY=your_key_here
   ALPACA_SECRET_KEY=your_secret_here
   ```
4. Enable in `config.py`:
   ```python
   DATA_SOURCES["alpaca"]["enabled"] = True
   ```

### Manifold Markets (Optional)

For prediction markets:

1. Enable in `config.py`:
   ```python
   DATA_SOURCES["manifold"]["enabled"] = True
   DATA_SOURCES["manifold"]["markets"] = ["market_id_here"]
   ```

### StockData.org (Optional)

For low-frequency stock data (100 requests/day free):

1. Sign up at [stockdata.org](https://stockdata.org)
2. Get API key
3. Add to `.env`:
   ```
   STOCKDATA_API_KEY=your_key_here
   ```
4. Enable in `config.py`:
   ```python
   DATA_SOURCES["stockdata"]["enabled"] = True
   ```

## Analyzing Results

All trades and equity snapshots are logged to SQLite database (`lab.db`).

### Using Pandas

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('lab.db')

# Load trades
trades = pd.read_sql_query("SELECT * FROM trades", conn)
print(trades)

# Load equity history
equity = pd.read_sql_query("SELECT * FROM equity", conn)
print(equity)

# Calculate bot performance
bot_performance = equity.groupby('bot_name').agg({
    'equity': 'last',
    'realized_pnl': 'last'
})
print(bot_performance)
```

### Database Schema

**trades table:**
- `id`: Trade ID
- `time`: Unix timestamp
- `bot_name`: Bot that made the trade
- `symbol`: Trading symbol
- `side`: "BUY" or "SELL"
- `size`: Quantity traded
- `price`: Execution price
- `cash_after`: Cash balance after trade
- `position_after`: Position after trade

**equity table:**
- `id`: Snapshot ID
- `time`: Unix timestamp
- `bot_name`: Bot name
- `equity`: Total equity (cash + positions)
- `realized_pnl`: Realized profit/loss
- `unrealized_pnl`: Unrealized profit/loss

## Example Bots

### Random Trader

Randomly buys and sells with small positions. Good for testing the system.

Location: `llm_trading_lab/bots/example_random.py`

### Trend Follower

Simple moving average strategy:
- Buy when price > 10-tick moving average
- Sell when price < 10-tick moving average

Location: `llm_trading_lab/bots/example_trend.py`

## Advanced Usage

### Multiple Bots

Create multiple bot files in `bots/` directory. They all run simultaneously and independently.

```
llm_trading_lab/bots/
  ├── momentum_bot.py
  ├── mean_reversion_bot.py
  ├── breakout_bot.py
  └── arbitrage_bot.py
```

### Bot State Management

Use global variables in your bot file to maintain state across ticks:

```python
# Global state
last_prices = []
entry_price = None

def on_tick(ctx, tick):
    global last_prices, entry_price
    
    price = ctx.get_price("BTCUSDT")
    last_prices.append(price)
    
    # Keep only last 100 prices
    if len(last_prices) > 100:
        last_prices.pop(0)
```

### Error Handling

The lab automatically catches exceptions in bot code. Check the console for error messages:

```
[ERROR] llm_trading_lab.bot_manager: Error in bot 'My Bot' on_tick: division by zero
```

Bots with errors continue running on subsequent ticks.

## Troubleshooting

### "No prices available yet, waiting..."

This means data sources haven't received prices yet. Wait a few seconds for WebSocket connections to establish.

### "Bot has insufficient cash"

Your bot tried to buy more than available cash. Check position sizes in your strategy.

### "No price available for SYMBOL"

The symbol isn't in your enabled data sources. Add it to `config.py`:

```python
DATA_SOURCES["binance"]["symbols"].append("SYMBOL")
```

### WebSocket connection errors

If running in a restricted network, the Binance connector may fail. Try a different network or use local test data.

## Best Practices

1. **Start small**: Test with small position sizes (0.001 BTC) before scaling up
2. **Log frequently**: Use `ctx.log()` to understand bot behavior
3. **Check prices**: Always verify `get_price()` returns non-None before trading
4. **Manage risk**: Implement stop-losses and position limits
5. **Analyze results**: Review `lab.db` after runs to understand performance

## Tips for LLM-Generated Bots

When asking an LLM to generate a trading bot:

1. **Provide the bot API**: Show the context methods and tick structure
2. **Specify strategy**: Clearly describe the trading logic
3. **Set constraints**: Define position limits, symbols, and risk parameters
4. **Request logging**: Ask for ctx.log() calls to track decisions
5. **Test incrementally**: Start with simple strategies before complex ones

Example prompt:
```
Write a Python trading bot for the LLM Trading Lab that trades BTCUSDT.
The bot should:
- Use a 20-tick exponential moving average
- Buy when price crosses above EMA with cash available
- Sell when price crosses below EMA with a position
- Use position size of 0.01 BTC
- Log all trades with ctx.log()

The bot must define NAME, SYMBOLS, and on_tick(ctx, tick) function.
Use ctx.get_price(), ctx.get_cash(), ctx.get_position(), and ctx.submit_order().
```

## Next Steps

- Experiment with different strategies (momentum, mean reversion, breakout)
- Add multiple data sources (stocks + crypto)
- Run longer backtests and analyze results
- Optimize bot parameters based on historical performance
- Share your best bots with the community!

## Support

For issues or questions:
- Check logs in console output
- Review `lab.db` for trade history
- See example bots for working patterns
- Consult README.md for setup instructions
