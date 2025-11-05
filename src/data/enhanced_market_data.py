"""
Enhanced Market Data Collector with Technical Indicators
"""
import time
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..utils.logger import get_logger


class EnhancedMarketDataCollector:
    """
    Enhanced market data collector that provides detailed technical indicators
    matching the nof1.ai Alpha Arena format
    """
    
    def __init__(self, market_data_collector):
        """
        Initialize enhanced market data collector
        
        Args:
            market_data_collector: Base MarketDataCollector instance
        """
        self.market_data = market_data_collector
        self.logger = get_logger()
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate EMA for given prices"""
        if len(prices) < period:
            return [np.nan] * len(prices)
        
        ema = []
        multiplier = 2 / (period + 1)
        
        # First EMA is SMA
        sma = sum(prices[:period]) / period
        ema.append(sma)
        
        # Calculate rest of EMAs
        for price in prices[period:]:
            ema_value = (price - ema[-1]) * multiplier + ema[-1]
            ema.append(ema_value)
        
        # Pad beginning with NaN
        result = [np.nan] * (period - 1) + ema
        return result
    
    def calculate_macd(self, prices: List[float], fast=12, slow=26, signal=9) -> List[float]:
        """Calculate MACD line (not including signal line)"""
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        macd = []
        for i in range(len(prices)):
            if np.isnan(ema_fast[i]) or np.isnan(ema_slow[i]):
                macd.append(np.nan)
            else:
                macd.append(ema_fast[i] - ema_slow[i])
        
        return macd
    
    def calculate_rsi(self, prices: List[float], period: int) -> List[float]:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return [np.nan] * len(prices)
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        rsi = [np.nan]  # First value is NaN
        
        # First RSI uses simple average
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))
        
        # Subsequent RSIs use smoothed average
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
        
        return rsi
    
    def calculate_atr(self, df: pd.DataFrame, period: int) -> List[float]:
        """Calculate ATR from OHLC data"""
        if len(df) < period:
            return [np.nan] * len(df)
        
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        tr = []
        for i in range(len(df)):
            if i == 0:
                tr.append(high[i] - low[i])
            else:
                hl = high[i] - low[i]
                hc = abs(high[i] - close[i-1])
                lc = abs(low[i] - close[i-1])
                tr.append(max(hl, hc, lc))
        
        # Calculate ATR as EMA of TR
        atr = self.calculate_ema(tr, period)
        return atr
    
    def get_comprehensive_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive market data for a symbol including all technical indicators
        
        Args:
            symbol: Trading symbol (e.g., 'BTC', 'ETH')
        
        Returns:
            Dictionary with all market data and indicators
        """
        try:
            result = {
                'symbol': symbol,
                'available': True,
                'error': None
            }
            
            # Get current price
            mids = self.market_data.get_all_mids()
            if symbol not in mids:
                result['available'] = False
                result['error'] = 'Price not available'
                return result
            
            current_price = float(mids[symbol])
            result['current_price'] = current_price
            
            # Get 3-minute candles for intraday analysis
            # Need at least 50 candles for proper indicator calculation (MACD needs 26+9=35)
            end_time = int(time.time() * 1000)
            start_time = end_time - (150 * 60 * 1000)  # 150 minutes = 50 candles
            
            df_3m = self.market_data.get_candles(symbol, '3m', start_time, end_time)
            
            if df_3m.empty:
                result['available'] = False
                result['error'] = 'Candle data not available'
                return result
            
            # Use all available candles for calculation, but only show last 10 in output
            prices_3m = df_3m['close'].tolist()
            
            # Calculate intraday indicators
            ema_20_3m = self.calculate_ema(prices_3m, 20)
            macd_3m = self.calculate_macd(prices_3m)
            rsi_7_3m = self.calculate_rsi(prices_3m, 7)
            rsi_14_3m = self.calculate_rsi(prices_3m, 14)
            
            result['intraday'] = {
                'mid_prices': prices_3m[-10:],  # Only last 10 for display
                'ema_20': ema_20_3m[-10:],
                'macd': macd_3m[-10:],
                'rsi_7': rsi_7_3m[-10:],
                'rsi_14': rsi_14_3m[-10:],
                'current_ema20': ema_20_3m[-1] if ema_20_3m else np.nan,
                'current_macd': macd_3m[-1] if macd_3m else np.nan,
                'current_rsi7': rsi_7_3m[-1] if rsi_7_3m else np.nan
            }
            
            # Get 4-hour candles for longer-term context (last 40 candles = ~7 days)
            start_time_4h = end_time - (40 * 4 * 60 * 60 * 1000)
            df_4h = self.market_data.get_candles(symbol, '4h', start_time_4h, end_time)
            
            if not df_4h.empty:
                df_4h = df_4h.tail(40)
                prices_4h = df_4h['close'].tolist()
                
                ema_20_4h = self.calculate_ema(prices_4h, 20)
                ema_50_4h = self.calculate_ema(prices_4h, 50)
                atr_3_4h = self.calculate_atr(df_4h, 3)
                atr_14_4h = self.calculate_atr(df_4h, 14)
                macd_4h = self.calculate_macd(prices_4h)
                rsi_14_4h = self.calculate_rsi(prices_4h, 14)
                
                # Get last 10 values for arrays
                result['longer_term'] = {
                    'ema_20': ema_20_4h[-1] if len(ema_20_4h) > 0 else np.nan,
                    'ema_50': ema_50_4h[-1] if len(ema_50_4h) > 0 else np.nan,
                    'atr_3': atr_3_4h[-1] if len(atr_3_4h) > 0 else np.nan,
                    'atr_14': atr_14_4h[-1] if len(atr_14_4h) > 0 else np.nan,
                    'current_volume': df_4h['volume'].iloc[-1] if len(df_4h) > 0 else 0,
                    'avg_volume': df_4h['volume'].mean() if len(df_4h) > 0 else 0,
                    'macd_series': macd_4h[-10:] if len(macd_4h) >= 10 else macd_4h,
                    'rsi_14_series': rsi_14_4h[-10:] if len(rsi_14_4h) >= 10 else rsi_14_4h
                }
            else:
                result['longer_term'] = None
            
            # Get Open Interest and Funding Rate
            try:
                meta = self.market_data.get_meta()
                universe = meta.get('universe', [])
                
                for asset in universe:
                    if asset.get('name') == symbol:
                        # Get funding rate
                        result['funding_rate'] = float(asset.get('funding', 0))
                        
                        # Get open interest (approximation from available data)
                        # Note: HyperLiquid API may provide this differently
                        result['open_interest'] = {
                            'latest': 0,  # Placeholder
                            'average': 0   # Placeholder
                        }
                        break
            except Exception as e:
                self.logger.warning(f"Could not get funding/OI for {symbol}: {e}")
                result['funding_rate'] = 0
                result['open_interest'] = {'latest': 0, 'average': 0}
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'available': False,
                'error': str(e)
            }
    
    def format_market_data_for_prompt(self, market_data: Dict[str, Any]) -> str:
        """
        Format market data into the nof1.ai Alpha Arena prompt format
        
        Args:
            market_data: Market data dictionary from get_comprehensive_market_data
        
        Returns:
            Formatted string for prompt
        """
        if not market_data.get('available'):
            return f"ALL {market_data['symbol']} DATA\nData not available: {market_data.get('error', 'Unknown error')}\n"
        
        symbol = market_data['symbol']
        intraday = market_data.get('intraday', {})
        longer_term = market_data.get('longer_term')
        
        # Format current state
        cp = float(market_data['current_price'])
        ema20 = float(intraday.get('current_ema20', 0)) if not np.isnan(intraday.get('current_ema20', 0)) else 0
        macd = float(intraday.get('current_macd', 0)) if not np.isnan(intraday.get('current_macd', 0)) else 0
        rsi7 = float(intraday.get('current_rsi7', 0)) if not np.isnan(intraday.get('current_rsi7', 0)) else 0
        
        output = [
            f"ALL {symbol} DATA",
            f"current_price = {cp:.6g}, current_ema20 = {ema20:.6g}, current_macd = {macd:.6g}, current_rsi (7 period) = {rsi7:.6g}",
            "",
            f"In addition, here is the latest {symbol} open interest and funding rate for perps:",
            ""
        ]
        
        # Open Interest
        oi = market_data.get('open_interest', {})
        output.append(f"Open Interest: Latest: {oi.get('latest', 0):.2f} Average: {oi.get('average', 0):.2f}")
        output.append("")
        
        # Funding Rate
        output.append(f"Funding Rate: {market_data.get('funding_rate', 0):.6g}")
        output.append("")
        
        # Intraday series
        output.append("Intraday series (3-minute intervals, oldest → latest):")
        output.append("")
        
        mid_prices = intraday.get('mid_prices', [])
        output.append(f"{symbol} mid prices: {mid_prices}")
        output.append("")
        
        ema_20 = intraday.get('ema_20', [])
        output.append(f"EMA indicators (20-period): {[round(x, 3) if not np.isnan(x) else 0 for x in ema_20]}")
        output.append("")
        
        macd = intraday.get('macd', [])
        output.append(f"MACD indicators: {[round(x, 3) if not np.isnan(x) else 0 for x in macd]}")
        output.append("")
        
        rsi_7 = intraday.get('rsi_7', [])
        output.append(f"RSI indicators (7-Period): {[round(x, 3) if not np.isnan(x) else 0 for x in rsi_7]}")
        output.append("")
        
        rsi_14 = intraday.get('rsi_14', [])
        output.append(f"RSI indicators (14-Period): {[round(x, 3) if not np.isnan(x) else 0 for x in rsi_14]}")
        output.append("")
        
        # Longer-term context
        if longer_term:
            output.append("Longer-term context (4-hour timeframe):")
            output.append("")
            output.append(f"20-Period EMA: {longer_term.get('ema_20', 0):.3f} vs. 50-Period EMA: {longer_term.get('ema_50', 0):.3f}")
            output.append("")
            output.append(f"3-Period ATR: {longer_term.get('atr_3', 0):.3f} vs. 14-Period ATR: {longer_term.get('atr_14', 0):.3f}")
            output.append("")
            output.append(f"Current Volume: {longer_term.get('current_volume', 0):.3f} vs. Average Volume: {longer_term.get('avg_volume', 0):.3f}")
            output.append("")
            
            macd_series = longer_term.get('macd_series', [])
            output.append(f"MACD indicators: {[round(x, 3) if not np.isnan(x) else 0 for x in macd_series]}")
            output.append("")
            
            rsi_series = longer_term.get('rsi_14_series', [])
            output.append(f"RSI indicators (14-Period): {[round(x, 3) if not np.isnan(x) else 0 for x in rsi_series]}")
            output.append("")
        
        return "\n".join(output)
