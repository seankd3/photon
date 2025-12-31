# Legacy Code (Photon Photo-Culling App)

This directory contains the original Photon photo-culling application code.

## What Was Photon?

Photon was a desktop photo-culling application designed for photographers using Adobe Lightroom Classic. It provided a fast, PyQt5-based GUI for rating and flagging photos directly in Lightroom catalogs.

## Why The Change?

The repository has been transformed into the **LLM Trading Lab** - a Python application for testing AI-generated trading bots with real-world market data. This new direction better demonstrates AI coding capabilities and provides a platform for algorithmic trading experimentation.

## Legacy Code Contents

- `catalog.py` - Lightroom catalog SQLite reader
- `cli.py` - Command-line interface for photo operations
- `grid_view.py` - PyQt5 thumbnail grid widget
- `main.py` - Main PyQt5 application window
- `thumbnail_loader.py` - Async thumbnail loading
- `worker.py` - Qt worker thread for background tasks

## If You Need The Photo-Culling App

The legacy Photon photo-culling code is preserved in this directory but is no longer maintained. If you need the original functionality:

1. Check the git history before the trading lab transformation
2. Create a branch from the last photo-culling commit
3. Or contact the maintainers for the legacy codebase

## New Project

The current project is the **LLM Trading Lab**. See:
- `README.md` - Main project documentation
- `USAGE_GUIDE.md` - Detailed usage instructions
- `llm_trading_lab/` - New trading lab codebase

All new development focuses on the trading lab functionality.
