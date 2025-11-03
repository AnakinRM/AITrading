"""
Technical indicators calculation module
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

from ..utils.logger import get_logger


class TechnicalIndicators:
    """Calculate technical indicators for trading signals"""
    
    def __init__(self):
        """Initialize technical indicators calculator"""
        self.logger = get_logger()
    
    def calculate_sma(self, df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
        """
        Calculate Simple Moving Average
        
        Args:
            df: DataFrame with OHLCV data
            period: Period for SMA
            column: Column to calculate SMA on
        
        Returns:
            Series with SMA values
        """
        return df[column].rolling(window=period).mean()
    
    def calculate_ema(self, df: pd.DataFrame, period: int = 12, column: str = 'close') -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            df: DataFrame with OHLCV data
            period: Period for EMA
            column: Column to calculate EMA on
        
        Returns:
            Series with EMA values
        """
        return df[column].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
        """
        Calculate Relative Strength Index
        
        Args:
            df: DataFrame with OHLCV data
            period: Period for RSI
            column: Column to calculate RSI on
        
        Returns:
            Series with RSI values
        """
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(
        self,
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
        column: str = 'close'
    ) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame with OHLCV data
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            column: Column to calculate MACD on
        
        Returns:
            Dictionary with 'macd', 'signal', and 'histogram' series
        """
        ema_fast = self.calculate_ema(df, period=fast, column=column)
        ema_slow = self.calculate_ema(df, period=slow, column=column)
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(
        self,
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0,
        column: str = 'close'
    ) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            df: DataFrame with OHLCV data
            period: Period for moving average
            std_dev: Number of standard deviations
            column: Column to calculate bands on
        
        Returns:
            Dictionary with 'upper', 'middle', and 'lower' series
        """
        middle = self.calculate_sma(df, period=period, column=column)
        std = df[column].rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range
        
        Args:
            df: DataFrame with OHLCV data
            period: Period for ATR
        
        Returns:
            Series with ATR values
        """
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def calculate_volume_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate volume profile
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            Dictionary with volume profile data
        """
        total_volume = df['volume'].sum()
        avg_volume = df['volume'].mean()
        
        # Volume trend (increasing or decreasing)
        recent_volume = df['volume'].tail(10).mean()
        volume_trend = "increasing" if recent_volume > avg_volume else "decreasing"
        
        return {
            'total_volume': total_volume,
            'avg_volume': avg_volume,
            'recent_volume': recent_volume,
            'volume_trend': volume_trend
        }
    
    def calculate_all_indicators(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any] = None
    ) -> pd.DataFrame:
        """
        Calculate all technical indicators and add to DataFrame
        
        Args:
            df: DataFrame with OHLCV data
            config: Configuration for indicator parameters
        
        Returns:
            DataFrame with all indicators added
        """
        if df.empty:
            self.logger.warning("Empty DataFrame provided for indicator calculation")
            return df
        
        # Default configuration
        if config is None:
            config = {
                'sma_period': 20,
                'ema_period': 12,
                'rsi_period': 14,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'bbands_period': 20,
                'bbands_std': 2,
                'atr_period': 14
            }
        
        result_df = df.copy()
        
        try:
            # Moving averages
            result_df['sma'] = self.calculate_sma(df, period=config['sma_period'])
            result_df['ema'] = self.calculate_ema(df, period=config['ema_period'])
            
            # RSI
            result_df['rsi'] = self.calculate_rsi(df, period=config['rsi_period'])
            
            # MACD
            macd_data = self.calculate_macd(
                df,
                fast=config['macd_fast'],
                slow=config['macd_slow'],
                signal=config['macd_signal']
            )
            result_df['macd'] = macd_data['macd']
            result_df['macd_signal'] = macd_data['signal']
            result_df['macd_histogram'] = macd_data['histogram']
            
            # Bollinger Bands
            bbands = self.calculate_bollinger_bands(
                df,
                period=config['bbands_period'],
                std_dev=config['bbands_std']
            )
            result_df['bb_upper'] = bbands['upper']
            result_df['bb_middle'] = bbands['middle']
            result_df['bb_lower'] = bbands['lower']
            
            # ATR
            result_df['atr'] = self.calculate_atr(df, period=config['atr_period'])
            
            self.logger.debug(f"Calculated all indicators for {len(result_df)} rows")
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
        
        return result_df
    
    def get_market_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get market summary with key indicators
        
        Args:
            df: DataFrame with OHLCV and indicator data
        
        Returns:
            Dictionary with market summary
        """
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        
        summary = {
            'price': float(latest['close']),
            'sma': float(latest.get('sma', 0)),
            'ema': float(latest.get('ema', 0)),
            'rsi': float(latest.get('rsi', 0)),
            'macd': float(latest.get('macd', 0)),
            'macd_signal': float(latest.get('macd_signal', 0)),
            'bb_upper': float(latest.get('bb_upper', 0)),
            'bb_lower': float(latest.get('bb_lower', 0)),
            'atr': float(latest.get('atr', 0)),
            'volume': float(latest['volume'])
        }
        
        # Add trend analysis
        if 'sma' in df.columns and not pd.isna(latest['sma']):
            summary['trend'] = 'bullish' if latest['close'] > latest['sma'] else 'bearish'
        
        # Add RSI signal
        if 'rsi' in df.columns and not pd.isna(latest['rsi']):
            if latest['rsi'] > 70:
                summary['rsi_signal'] = 'overbought'
            elif latest['rsi'] < 30:
                summary['rsi_signal'] = 'oversold'
            else:
                summary['rsi_signal'] = 'neutral'
        
        # Add MACD signal
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            if not pd.isna(latest['macd']) and not pd.isna(latest['macd_signal']):
                summary['macd_signal'] = 'bullish' if latest['macd'] > latest['macd_signal'] else 'bearish'
        
        return summary
