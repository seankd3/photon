"""Time utilities."""

import time
from datetime import datetime


def now_unix() -> float:
    """Get current Unix timestamp."""
    return time.time()


def format_timestamp(unix_time: float) -> str:
    """Format Unix timestamp as human-readable string."""
    return datetime.fromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")
