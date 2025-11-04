"""
Market data collection module
"""
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
from hyperliquid.info import Info
from hyperliquid.utils import constants

from ..utils.logger import get_logger
from ..utils.config_loader import get_config
from ..utils.constants import ALLOWED_SYMBOLS, LOG_SKIP_UNAVAILABLE, LOG_PRICE_FETCH_FAILED


class MarketDataCollector:
    """Collect market data from HyperLiquid"""
    
    def __init__(self, config: dict = None):
        """
        Initialize market data collector
        
        Args:
            config: Configuration dictionary
        """
        self.logger = get_logger()
        
        if config is None:
            config_loader = get_config()
            config = config_loader.get_section('hyperliquid')
        
        self.api_url = config.get('api_url', constants.MAINNET_API_URL)
        self.info = Info(self.api_url, skip_ws=True)
        
        # Whitelist of allowed trading symbols
        self.allowed_symbols = ALLOWED_SYMBOLS
        
        self.logger.info(f"MarketDataCollector initialized with API: {self.api_url}")
        self.logger.info(f"Allowed trading symbols: {self.allowed_symbols}")
    
    def get_all_mids(self) -> Dict[str, float]:
        """
        Get mid prices for all trading pairs
        
        Returns:
            Dictionary of coin -> mid price
        """
        try:
            mids = self.info.all_mids()
            self.logger.debug(f"Retrieved mid prices for {len(mids)} coins")
            return mids
        except Exception as e:
            self.logger.error(f"Error getting mid prices: {e}")
            return {}
    
    def get_l2_book(self, coin: str) -> Dict[str, Any]:
        """
        Get Level 2 order book for a coin
        
        Args:
            coin: Coin symbol (e.g., 'BTC')
        
        Returns:
            Order book data with bids and asks
        """
        try:
            book = self.info.l2_snapshot(coin)
            self.logger.debug(f"Retrieved L2 book for {coin}")
            return book
        except Exception as e:
            self.logger.error(f"Error getting L2 book for {coin}: {e}")
            return {}
    
    def get_candles(
        self,
        coin: str,
        interval: str = "1m",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get historical candle data
        
        Args:
            coin: Coin symbol
            interval: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Default to last 24 hours if not specified
            if end_time is None:
                end_time = int(time.time() * 1000)
            if start_time is None:
                start_time = end_time - (24 * 60 * 60 * 1000)
            
            candles = self.info.candles_snapshot(
                coin,
                interval,
                start_time,
                end_time
            )
            
            if not candles:
                self.logger.warning(f"No candle data returned for {coin}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(candles)
            
            # Rename columns to standard OHLCV format
            if 't' in df.columns:
                df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
                df['open'] = df['o'].astype(float)
                df['high'] = df['h'].astype(float)
                df['low'] = df['l'].astype(float)
                df['close'] = df['c'].astype(float)
                df['volume'] = df['v'].astype(float)
                
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                df.set_index('timestamp', inplace=True)
            
            self.logger.debug(f"Retrieved {len(df)} candles for {coin} ({interval})")
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting candles for {coin}: {e}")
            return pd.DataFrame()
    
    def get_user_state(self, address: str) -> Dict[str, Any]:
        """
        Get user account state
        
        Args:
            address: User wallet address
        
        Returns:
            User state including positions and balances
        """
        try:
            state = self.info.user_state(address)
            self.logger.debug(f"Retrieved user state for {address}")
            return state
        except Exception as e:
            self.logger.error(f"Error getting user state: {e}")
            return {}
    
    def get_open_orders(self, address: str) -> List[Dict[str, Any]]:
        """
        Get user's open orders
        
        Args:
            address: User wallet address
        
        Returns:
            List of open orders
        """
        try:
            orders = self.info.open_orders(address)
            self.logger.debug(f"Retrieved {len(orders)} open orders for {address}")
            return orders
        except Exception as e:
            self.logger.error(f"Error getting open orders: {e}")
            return []
    
    def get_user_fills(self, address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get user's recent fills
        
        Args:
            address: User wallet address
            limit: Maximum number of fills to retrieve
        
        Returns:
            List of fills
        """
        try:
            fills = self.info.user_fills(address)
            self.logger.debug(f"Retrieved {len(fills)} fills for {address}")
            return fills[:limit]
        except Exception as e:
            self.logger.error(f"Error getting user fills: {e}")
            return []
    
    def get_meta(self) -> Dict[str, Any]:
        """
        Get exchange metadata including available coins
        
        Returns:
            Exchange metadata
        """
        try:
            meta = self.info.meta()
            self.logger.debug("Retrieved exchange metadata")
            return meta
        except Exception as e:
            self.logger.error(f"Error getting metadata: {e}")
            return {}
    
    def get_funding_history(self, coin: str, start_time: int, end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get funding rate history for a coin
        
        Args:
            coin: Coin symbol
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
        
        Returns:
            List of funding rate data
        """
        try:
            funding = self.info.funding_history(
                coin=coin,
                startTime=start_time,
                endTime=end_time
            )
            self.logger.debug(f"Retrieved funding history for {coin}")
            return funding
        except Exception as e:
            self.logger.error(f"Error getting funding history for {coin}: {e}")
            return []
    
    def get_available_symbols(self) -> List[str]:
        """
        Get list of symbols that are currently available for trading
        Filters by ALLOWED_SYMBOLS whitelist and checks availability on Hyperliquid
        
        Returns:
            List of available symbol strings
        """
        available = []
        all_mids = self.get_all_mids()
        
        for symbol in self.allowed_symbols:
            if symbol in all_mids and all_mids[symbol] is not None and all_mids[symbol] > 0:
                available.append(symbol)
                self.logger.debug(f"Symbol {symbol} is available: ${all_mids[symbol]}")
            else:
                self.logger.warning(
                    f"{LOG_SKIP_UNAVAILABLE}={symbol} - Symbol not available or no price data",
                    extra={"event": LOG_SKIP_UNAVAILABLE, "symbol": symbol}
                )
        
        self.logger.info(f"Available symbols: {available} (out of {len(self.allowed_symbols)} allowed)")
        return available
    
    def get_price_safe(self, symbol: str) -> Optional[float]:
        """
        Safely get price for a symbol with error handling
        Returns None if symbol is not available or price fetch fails
        
        Args:
            symbol: Symbol to get price for
        
        Returns:
            Price as float or None if unavailable
        """
        # Check if symbol is in whitelist
        if symbol not in self.allowed_symbols:
            self.logger.warning(
                f"Symbol {symbol} not in allowed list: {self.allowed_symbols}",
                extra={"event": "symbol_not_allowed", "symbol": symbol}
            )
            return None
        
        try:
            all_mids = self.get_all_mids()
            
            if symbol not in all_mids:
                self.logger.warning(
                    f"{LOG_SKIP_UNAVAILABLE}={symbol} - Symbol not found in market data",
                    extra={"event": LOG_SKIP_UNAVAILABLE, "symbol": symbol}
                )
                return None
            
            price = all_mids[symbol]
            
            if price is None or price <= 0:
                self.logger.warning(
                    f"{LOG_PRICE_FETCH_FAILED}={symbol} - Invalid price: {price}",
                    extra={"event": LOG_PRICE_FETCH_FAILED, "symbol": symbol, "price": price}
                )
                return None
            
            return float(price)
            
        except Exception as e:
            self.logger.error(
                f"{LOG_PRICE_FETCH_FAILED}={symbol} - Exception: {e}",
                extra={"event": LOG_PRICE_FETCH_FAILED, "symbol": symbol, "error": str(e)}
            )
            return None
    
    def get_market_data_for_symbols(self, symbols: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get market data for multiple symbols with error handling
        Automatically skips unavailable symbols instead of failing
        
        Args:
            symbols: List of symbols to fetch (defaults to allowed_symbols)
        
        Returns:
            Dictionary mapping symbol -> market data
            Only includes successfully fetched symbols
        """
        if symbols is None:
            symbols = self.allowed_symbols
        
        market_data = {}
        
        for symbol in symbols:
            try:
                # Get price
                price = self.get_price_safe(symbol)
                if price is None:
                    continue  # Skip this symbol
                
                # Get order book (optional, may fail)
                l2_book = {}
                try:
                    l2_book = self.get_l2_book(symbol)
                except Exception as e:
                    self.logger.debug(f"Could not fetch L2 book for {symbol}: {e}")
                
                # Get recent candles (optional, may fail)
                candles = pd.DataFrame()
                try:
                    candles = self.get_candles(symbol, interval="1h")
                except Exception as e:
                    self.logger.debug(f"Could not fetch candles for {symbol}: {e}")
                
                market_data[symbol] = {
                    "symbol": symbol,
                    "price": price,
                    "l2_book": l2_book,
                    "candles": candles,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.logger.debug(f"Successfully fetched market data for {symbol}")
                
            except Exception as e:
                self.logger.warning(
                    f"{LOG_SKIP_UNAVAILABLE}={symbol} - Failed to fetch market data: {e}",
                    extra={"event": LOG_SKIP_UNAVAILABLE, "symbol": symbol, "error": str(e)}
                )
                continue  # Skip this symbol and continue with others
        
        self.logger.info(f"Fetched market data for {len(market_data)}/{len(symbols)} symbols")
        return market_data


class MarketDataCache:
    """Cache for market data to reduce API calls"""
    
    def __init__(self, ttl: int = 60):
        """
        Initialize cache
        
        Args:
            ttl: Time to live in seconds
        """
        self.cache: Dict[str, tuple] = {}
        self.ttl = ttl
        self.logger = get_logger()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if expired/not found
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                del self.cache[key]
                self.logger.debug(f"Cache expired for key: {key}")
        return None
    
    def set(self, key: str, value: Any):
        """
        Set cached value
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = (value, time.time())
        self.logger.debug(f"Cached value for key: {key}")
    
    def clear(self):
        """Clear all cached values"""
        self.cache.clear()
        self.logger.debug("Cache cleared")
