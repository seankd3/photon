# Design Decisions Log

This document records significant architectural and design decisions made during the development of LLM Trading Lab.

---

## 2025-12-31: Project Pivot - Photon to LLM Trading Lab

**Decision:** Transform the repository from a photo-culling desktop application into an LLM trading bot laboratory.

**Rationale:** The new specification provides a clear use case for testing LLM-generated trading strategies with real market data in a paper trading environment. This is a better fit for demonstrating AI code generation capabilities.

**Implications:**
- Complete codebase replacement
- Removed all GUI/PyQt5 dependencies
- Focus on async Python for real-time data handling
- Simple CLI interface instead of desktop app

---

## 2025-12-31: WebSocket-first for Market Data

**Decision:** Use WebSocket connections as the primary data source for real-time market data (Binance, Alpaca).

**Rationale:**
- WebSockets provide true real-time updates with minimal latency
- More efficient than polling REST endpoints every second
- Matches professional trading system architecture
- Binance and Alpaca both provide robust WebSocket APIs

**Alternatives considered:**
- REST polling: Higher latency, more API calls, rate limit concerns
- Historical data only: Doesn't provide the real-time trading experience

---

## 2025-12-31: SQLite for Trade/Equity Logging

**Decision:** Use SQLite for persistent storage of trades and equity snapshots.

**Rationale:**
- Zero-config embedded database - no separate server required
- Sufficient performance for single-machine deployment
- Easy to analyze with Pandas for backtesting/analysis
- Cross-platform and included in Python standard library

**Alternatives considered:**
- CSV files: Less queryable, no transactional integrity
- PostgreSQL: Overkill for single-machine deployment
- In-memory only: Lose all history on restart

---

## 2025-12-31: Market Orders Only (v1)

**Decision:** Only support market orders in the initial version, not limit orders or other order types.

**Rationale:**
- Simplifies the paper broker implementation significantly
- Market orders execute immediately using current price
- Sufficient for most momentum/trend-following strategies
- Can add limit orders in future versions if needed

---

## 2025-12-31: Single Process, Async Event Loop

**Decision:** Run all components (data sources, bots, broker) in a single process using asyncio.

**Rationale:**
- Simpler deployment and debugging
- No need for inter-process communication
- Asyncio provides sufficient concurrency for I/O-bound workload
- Matches the spec requirement for "single-machine Python app"

**Alternatives considered:**
- Multi-process: Added complexity without clear benefit at this scale
- Threading: More complex state management, GIL concerns
- Microservices: Explicitly out of scope per spec

---

## 2025-12-31: Bot Interface Design

**Decision:** Bots define NAME, SYMBOLS constants and on_tick(ctx, tick) function. They call ctx.submit_order() to trade.

**Rationale:**
- Extremely simple for LLMs to generate
- No need for bots to return values or understand complex protocols
- Context object provides all needed functionality
- Bots are isolated and can't affect each other or the system

**Key principle:** Bots decide WHEN to trade by calling submit_order, not forced to trade on every tick.

---

## 2025-12-31: Binance as Default Data Source

**Decision:** Make Binance the default, always-enabled data source with no authentication required.

**Rationale:**
- Binance provides free, public WebSocket streams for market data
- No signup or API keys required - works out of the box
- Covers popular crypto markets (BTC, ETH, etc.)
- Global availability

**Other sources (Alpaca, Manifold, StockData)** are optional and require configuration.

---
