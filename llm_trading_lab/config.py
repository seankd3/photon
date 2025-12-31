"""
Configuration for LLM Trading Lab.

Defines data sources, trading symbols, starting capital, and other settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Starting capital per bot (USD)
STARTING_CASH = 10_000.0

# Tick interval in seconds (how often bots are called)
TICK_INTERVAL_SECONDS = 1.0

# SQLite database path for trade/equity logging
DB_PATH = "lab.db"

# Data sources configuration
# Each data source can be enabled/disabled and configured with symbols
DATA_SOURCES = {
    "binance": {
        "enabled": True,
        "symbols": ["BTCUSDT", "ETHUSDT"],
        "base_url": "wss://stream.binance.com:9443/ws",
    },
    "alpaca": {
        "enabled": False,  # Requires API keys
        "symbols": ["AAPL", "TSLA", "GOOGL"],
        "api_key": os.getenv("ALPACA_API_KEY", ""),
        "api_secret": os.getenv("ALPACA_SECRET_KEY", ""),
        "base_url": "https://paper-api.alpaca.markets",
        "data_url": "https://data.alpaca.markets",
    },
    "manifold": {
        "enabled": False,
        "markets": [],  # Market IDs to subscribe to
        "ws_url": "wss://api.manifold.markets/ws",
    },
    "stockdata": {
        "enabled": False,  # Requires API key, 100 requests/day on free plan
        "symbols": ["SPY", "QQQ"],
        "api_key": os.getenv("STOCKDATA_API_KEY", ""),
        "base_url": "https://api.stockdata.org/v1",
        "poll_interval_seconds": 10,  # Respect rate limits
    },
}


# Get all enabled symbols across all data sources
def get_all_symbols():
    """Return list of all symbols from enabled data sources."""
    symbols = []
    for source_name, config in DATA_SOURCES.items():
        if config.get("enabled", False):
            if "symbols" in config:
                symbols.extend(config["symbols"])
    return list(set(symbols))  # Remove duplicates


# Validate configuration
def validate_config():
    """Validate configuration and check for required API keys."""
    errors = []

    # Check if at least one data source is enabled
    enabled_sources = [name for name, cfg in DATA_SOURCES.items() if cfg.get("enabled")]
    if not enabled_sources:
        errors.append("At least one data source must be enabled")

    # Check for required API keys
    if DATA_SOURCES["alpaca"]["enabled"]:
        if not DATA_SOURCES["alpaca"]["api_key"] or not DATA_SOURCES["alpaca"]["api_secret"]:
            errors.append("Alpaca is enabled but ALPACA_API_KEY or ALPACA_SECRET_KEY not set")

    if DATA_SOURCES["stockdata"]["enabled"]:
        if not DATA_SOURCES["stockdata"]["api_key"]:
            errors.append("StockData is enabled but STOCKDATA_API_KEY not set")

    # Check tick interval
    if TICK_INTERVAL_SECONDS <= 0:
        errors.append("TICK_INTERVAL_SECONDS must be positive")

    # Check starting cash
    if STARTING_CASH <= 0:
        errors.append("STARTING_CASH must be positive")

    return errors


if __name__ == "__main__":
    # Quick config validation when run directly
    errors = validate_config()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration valid")
        print(
            f"Enabled sources: {[name for name, cfg in DATA_SOURCES.items() if cfg.get('enabled')]}"
        )
        print(f"All symbols: {get_all_symbols()}")
