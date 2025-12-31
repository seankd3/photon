# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- LLM Trading Lab - complete rewrite from photo-culling app to trading bot platform
- Real-time market data from Binance (crypto), Alpaca (stocks), Manifold (prediction markets), and StockData.org
- Paper trading execution engine with position tracking
- Simple bot interface - bots are Python files with on_tick() function
- SQLite logging of all trades and equity snapshots
- CLI monitoring dashboard showing bot performance
- Dynamic bot loading from bots/ directory
- Example bots: random trader and trend follower

### Removed
- All Photon photo-culling functionality (PyQt5 GUI, Lightroom integration, image processing)
