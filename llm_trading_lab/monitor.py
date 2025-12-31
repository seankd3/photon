"""
CLI monitoring dashboard.

Displays bot performance in a simple text-based table.
"""

import time
from datetime import datetime
from typing import Dict
from .engine.models import BotState
from .bot_manager import LoadedBot


def render(bot_states: Dict[str, BotState], bots_info: Dict[str, LoadedBot]) -> None:
    """
    Render CLI dashboard showing bot performance.

    Args:
        bot_states: Current state for each bot
        bots_info: Information about loaded bots
    """
    # Clear screen (works on Windows and Unix)
    print("\033[2J\033[H", end="")

    # Header
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 100)
    print(f"LLM TRADING LAB - {current_time}")
    print("=" * 100)
    print()

    if not bot_states:
        print("No bots loaded. Add bot files to llm_trading_lab/bots/")
        return

    # Table header
    print(
        f"{'BOT':<20} {'STATUS':<10} {'CASH':>12} {'EQUITY':>12} "
        f"{'REAL_PNL':>12} {'UNREAL_PNL':>12}"
    )
    print("-" * 100)

    # Bot rows
    for bot_name, state in bot_states.items():
        bot_info = bots_info.get(bot_name)
        status = bot_info.status if bot_info else "UNKNOWN"

        # Format numbers with colors
        real_pnl_str = format_pnl(state.realized_pnl)
        unreal_pnl_str = format_pnl(state.unrealized_pnl)

        print(
            f"{bot_name:<20} {status:<10} "
            f"${state.cash:>11,.2f} ${state.equity:>11,.2f} "
            f"{real_pnl_str:>12} {unreal_pnl_str:>12}"
        )

        # Show positions if any
        if state.positions:
            positions_str = ", ".join([f"{sym}: {amt:.6f}" for sym, amt in state.positions.items()])
            print(f"  └─ Positions: {positions_str}")

        # Show errors if any
        if bot_info and bot_info.last_error:
            print(f"  └─ ERROR: {bot_info.last_error[:70]}")

    print()
    print("Commands: p <bot_name> (pause) | r <bot_name> (resume) | q (quit)")
    print()


def format_pnl(pnl: float) -> str:
    """
    Format PnL with color and sign.

    Args:
        pnl: PnL value

    Returns:
        Formatted string with ANSI color codes
    """
    if pnl > 0:
        return f"\033[92m+${pnl:,.2f}\033[0m"  # Green
    elif pnl < 0:
        return f"\033[91m${pnl:,.2f}\033[0m"  # Red
    else:
        return f"${pnl:,.2f}"


def print_startup_banner():
    """Print startup banner."""
    print()
    print("=" * 100)
    print(" _     _     __  __   _____               _ _               _          _     ")
    print("| |   | |   |  \\/  | |_   _| __ __ _  __| (_)_ __   __ _  | |    __ _| |__  ")
    print("| |   | |   | |\\/| |   | || '__/ _` |/ _` | | '_ \\ / _` | | |   / _` | '_ \\ ")
    print("| |___| |___| |  | |   | || | | (_| | (_| | | | | | (_| | | |__| (_| | |_) |")
    print("|_____|_____|_|  |_|   |_||_|  \\__,_|\\__,_|_|_| |_|\\__, | |_____\\__,_|_.__/ ")
    print("                                                     |___/                    ")
    print()
    print("  Real-time trading bot laboratory with live market data")
    print("=" * 100)
    print()
