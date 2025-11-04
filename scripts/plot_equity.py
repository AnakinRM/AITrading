"""
Real-time equity curve viewer.
Run: python scripts/plot_equity.py
Requires matplotlib (installed via requirements).
"""
import time
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EQUITY_LOG = PROJECT_ROOT / "logs" / "equity_history.csv"
REFRESH_SECONDS = 30


def load_equity() -> Optional[pd.DataFrame]:
    """Load equity history if it exists."""
    if not EQUITY_LOG.exists():
        return None
    df = pd.read_csv(EQUITY_LOG, parse_dates=["timestamp"])
    if df.empty:
        return None
    df.sort_values("timestamp", inplace=True)
    return df


def update_chart(ax: plt.Axes) -> None:
    """Reload data from CSV and redraw the equity curve."""
    df = load_equity()
    ax.clear()

    if df is None:
        ax.set_title("Waiting for equity data…")
        ax.set_xlabel("Time")
        ax.set_ylabel("Capital (USD)")
        return

    ax.plot(df["timestamp"], df["capital"], label="Capital", color="#1f77b4")
    ax.fill_between(df["timestamp"], df["capital"], alpha=0.1, color="#1f77b4")
    ax.set_title("AITrading Equity Curve")
    ax.set_xlabel("Time")
    ax.set_ylabel("Capital (USD)")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="best")
    ax.tick_params(axis="x", rotation=30)


def main() -> None:
    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(10, 6))

    def refresh(_frame):
        update_chart(ax)

    # Initial draw
    update_chart(ax)
    plt.tight_layout()

    # Manual refresh loop (no animation to keep deps minimal)
    while True:
        plt.pause(0.1)
        refresh(None)
        plt.draw()
        plt.pause(REFRESH_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting equity viewer.")
