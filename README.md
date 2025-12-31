# LLM Trading Lab

A single-machine Python application for testing trading bots with real-world, real-time market data. Designed for LLM agents to write bots as simple Python files that can trade crypto, stocks, and prediction markets in a paper trading environment.

## Features

- **Real-time market data** from multiple sources (Binance, Alpaca, Manifold, StockData.org)
- **Simple bot interface** - bots are just Python files with `on_tick()` function
- **Paper trading execution** - simulated order fills with position tracking
- **Performance tracking** - SQLite logging of trades, PnL, and equity over time
- **CLI monitoring** - real-time dashboard showing bot performance
- **Dynamic bot loading** - drop new bot `.py` files into `bots/` directory

## Architecture

```
llm_trading_lab/
  ├── config.py              # Configuration (symbols, data sources, starting cash)
  ├── main.py                # Main event loop
  ├── monitor.py             # CLI dashboard
  ├── data_sources/          # Market data connectors
  │   ├── __init__.py
  │   ├── binance.py         # Crypto (required, no auth)
  │   ├── alpaca.py          # US stocks/crypto (optional, requires API key)
  │   ├── manifold.py        # Prediction markets (optional)
  │   └── stockdata.py       # Low-frequency equities (optional)
  ├── engine/                # Paper trading engine
  │   ├── __init__.py
  │   ├── models.py          # BotState, Order, Trade data models
  │   ├── broker.py          # Order execution and position tracking
  │   └── storage.py         # SQLite logging
  ├── bots/                  # Trading bot modules
  │   ├── example_random.py
  │   └── example_trend.py
  └── utils/                 # Utility modules
      ├── time_utils.py
      └── logging_utils.py
```

## Getting Started (Windows)

**Prerequisites:** Python 3.11+

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/Sean-Kenneth-Doherty/photon
   cd photon
   ```

2. **Set up virtual environment:**
   ```powershell
   py -3.11 -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure data sources (optional):**
   - Copy `.env.example` to `.env`
   - Add API keys for optional data sources (Alpaca, StockData.org)
   - Edit `llm_trading_lab/config.py` to enable/disable sources

5. **Run the lab:**
   ```powershell
   python llm_trading_lab/main.py
   ```

## Getting Started (Linux/macOS)

**Prerequisites:** Python 3.11+

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Sean-Kenneth-Doherty/photon
   cd photon
   ```

2. **Set up virtual environment:**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure data sources (optional):**
   - Copy `.env.example` to `.env`
   - Add API keys for optional data sources (Alpaca, StockData.org)
   - Edit `llm_trading_lab/config.py` to enable/disable sources

5. **Run the lab:**
   ```bash
   python llm_trading_lab/main.py
   ```

## Writing Trading Bots

Bots are simple Python files placed in the `llm_trading_lab/bots/` directory:

```python
# example_bot.py

NAME = "My Trading Bot"
SYMBOLS = ["BTCUSDT"]  # Markets this bot trades

def init(ctx):
    """Called once when bot loads (optional)"""
    ctx.log("Bot initialized")

def on_tick(ctx, tick):
    """Called every tick (e.g., every second)"""
    price = ctx.get_price("BTCUSDT")
    cash = ctx.get_cash()
    position = ctx.get_position("BTCUSDT")
    
    # Example: buy if we have cash and no position
    if cash > 100 and position == 0:
        ctx.submit_order(symbol="BTCUSDT", side="BUY", size=0.001)
    
    # Example: sell if we have a position and price is high
    if position > 0 and price > 70000:
        ctx.submit_order(symbol="BTCUSDT", side="SELL", size=position)
```

### Bot API

**Context methods available in `on_tick()`:**

- `ctx.get_price(symbol)` - Get current market price
- `ctx.get_cash()` - Get available cash
- `ctx.get_position(symbol)` - Get current position size
- `ctx.submit_order(symbol, side, size)` - Submit a market order
- `ctx.log(message)` - Log a message

**Tick data structure:**

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

## Data Sources

### Binance (Crypto) - Default

- **Enabled by default** - no API key required
- Real-time WebSocket streams for BTC, ETH, and other crypto pairs
- Public market data endpoints

### Alpaca (US Stocks/Crypto) - Optional

- **Requires free paper trading account** at [alpaca.markets](https://alpaca.markets)
- Set environment variables:
  ```
  ALPACA_API_KEY=your_key
  ALPACA_SECRET_KEY=your_secret
  ```
- Enable in `config.py`: `DATA_SOURCES["alpaca"]["enabled"] = True`

### Manifold Markets (Prediction Markets) - Optional

- Public API for prediction market data
- Enable in `config.py`: `DATA_SOURCES["manifold"]["enabled"] = True`

### StockData.org (Low-frequency Equities) - Optional

- **100 free requests/day** on free plan
- Best for low-frequency strategies
- Set environment variable: `STOCKDATA_API_KEY=your_key`
- Enable in `config.py`: `DATA_SOURCES["stockdata"]["enabled"] = True`

## Configuration

Edit `llm_trading_lab/config.py` to customize:

- Starting cash per bot
- Tick interval (seconds between bot updates)
- Enabled data sources
- Trading symbols
- SQLite database path

## Monitoring

The CLI dashboard shows:
- Bot status (running/stopped)
- Current equity and PnL
- Recent trades
- Positions

Commands during runtime:
- `p <bot_name>` - Pause a bot
- `r <bot_name>` - Resume a bot
- `q` - Quit the lab

## Data & Logs

All trades and equity snapshots are logged to SQLite (`lab.db` by default):

- **trades** table: Every executed order
- **equity** table: Periodic snapshots of bot performance

Analyze with Pandas:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('lab.db')
trades = pd.read_sql_query("SELECT * FROM trades", conn)
equity = pd.read_sql_query("SELECT * FROM equity", conn)
```

## License

MIT
