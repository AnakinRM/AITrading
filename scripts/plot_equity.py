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
from matplotlib import dates as mdates
import numpy as np

try:
    import mplcursors  # type: ignore
except ImportError:  # pragma: no cover
    mplcursors = None

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
    df.reset_index(drop=True, inplace=True)
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

    line, = ax.plot(df["timestamp"], df["capital"], label="Capital", color="#1f77b4")
    ax.fill_between(df["timestamp"], df["capital"], alpha=0.1, color="#1f77b4")
    ax.set_title("AITrading Equity Curve")
    ax.set_xlabel("Time")
    ax.set_ylabel("Capital (USD)")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="best")
    ax.tick_params(axis="x", rotation=30)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M"))

    latest_time = df["timestamp"].iloc[-1]
    latest_capital = df["capital"].iloc[-1]
    latest_unrealized = df["unrealized"].iloc[-1] if "unrealized" in df.columns else 0.0
    latest_positions = df["num_positions"].iloc[-1] if "num_positions" in df.columns else 0
    info = (
        f"Latest capital: ${latest_capital:,.2f}\n"
        f"Unrealized PnL: ${latest_unrealized:,.2f}\n"
        f"Open positions: {latest_positions}\n"
        f"Updated: {latest_time:%Y-%m-%d %H:%M:%S}"
    )

    prior_text = getattr(ax, "_latest_label", None)
    if prior_text is not None:
        try:
            prior_text.remove()
        except NotImplementedError:
            prior_text.set_visible(False)
    ax._latest_label = ax.text(
        0.02,
        0.95,
        info,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
    )

    if mplcursors:
        prior_cursor = getattr(ax, "_cursor", None)
        if prior_cursor is not None:
            try:
                prior_cursor.remove()
            except NotImplementedError:
                prior_cursor.enabled = False

        cursor = mplcursors.cursor(line, hover=True)
        x_data = line.get_xdata()

        @cursor.connect("add")
        def _on_add(sel):
            idx = getattr(sel, "index", None)
            if idx is None:
                target_x = sel.target[0]
                # Ensure numpy array for subtraction
                idx = int(np.abs(x_data - target_x).argmin())
            idx = max(0, min(len(df) - 1, int(idx)))
            timestamp = df["timestamp"].iloc[idx]
            capital = df["capital"].iloc[idx]
            sel.annotation.set_text(
                f"{timestamp:%Y-%m-%d %H:%M:%S}\nCapital: ${capital:,.2f}"
            )

        ax._cursor = cursor


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
