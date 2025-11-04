"""
Constants and configuration values for the trading system.
"""

# Allowed trading symbols - WHITELIST
# Only these 6 symbols are permitted for trading on Hyperliquid
ALLOWED_SYMBOLS = ["XRP", "DOGE", "BTC", "ETH", "SOL", "BNB"]

# Trading directions
DIRECTION_LONG = "LONG"
DIRECTION_SHORT = "SHORT"
ALLOWED_DIRECTIONS = [DIRECTION_LONG, DIRECTION_SHORT]

# Order types
ORDER_TYPE_LIMIT = "limit"
ORDER_TYPE_MARKET = "market"

# Time in force
TIF_GTC = "Gtc"  # Good till cancel
TIF_IOC = "Ioc"  # Immediate or cancel
TIF_ALO = "Alo"  # Add liquidity only

# Trading modes
MODE_PAPER = "paper"
MODE_LIVE = "live"

# Log levels for symbol availability
LOG_SKIP_UNAVAILABLE = "skip_unavailable_symbol"
LOG_PRICE_FETCH_FAILED = "price_fetch_failed"
LOG_CONTRACT_UNAVAILABLE = "contract_unavailable"
