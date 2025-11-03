#!/usr/bin/env python3
"""
Quick Start Example
This script demonstrates basic usage of the trading bot components
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.market_data import MarketDataCollector
from src.data.indicators import TechnicalIndicators
from src.utils.logger import get_logger


def main():
    """Quick start example"""
    logger = get_logger()
    logger.info("=" * 60)
    logger.info("HyperLiquid Trading Bot - Quick Start Example")
    logger.info("=" * 60)
    
    # Initialize components
    logger.info("Initializing components...")
    
    # Market data collector (using testnet)
    market_data = MarketDataCollector({
        'api_url': 'https://api.hyperliquid-testnet.xyz'
    })
    
    # Technical indicators calculator
    indicators = TechnicalIndicators()
    
    # Example 1: Get current market prices
    logger.info("\n--- Example 1: Get Current Market Prices ---")
    mids = market_data.get_all_mids()
    
    for coin in ['BTC', 'ETH', 'SOL']:
        if coin in mids:
            price = float(mids[coin])
            logger.info(f"{coin}: ${price:,.2f}")
    
    # Example 2: Get historical candles and calculate indicators
    logger.info("\n--- Example 2: Technical Analysis ---")
    coin = 'BTC'
    
    logger.info(f"Fetching {coin} candle data...")
    candles = market_data.get_candles(coin, interval='1h')
    
    if not candles.empty:
        logger.info(f"Retrieved {len(candles)} candles")
        
        # Calculate indicators
        logger.info("Calculating technical indicators...")
        candles_with_indicators = indicators.calculate_all_indicators(candles)
        
        # Get market summary
        summary = indicators.get_market_summary(candles_with_indicators)
        
        logger.info(f"\n{coin} Market Summary:")
        logger.info(f"  Price: ${summary.get('price', 0):,.2f}")
        logger.info(f"  SMA(20): ${summary.get('sma', 0):,.2f}")
        logger.info(f"  RSI(14): {summary.get('rsi', 0):.2f} ({summary.get('rsi_signal', 'N/A')})")
        logger.info(f"  Trend: {summary.get('trend', 'N/A')}")
        logger.info(f"  MACD Signal: {summary.get('macd_signal', 'N/A')}")
    else:
        logger.warning(f"No candle data available for {coin}")
    
    # Example 3: Get exchange metadata
    logger.info("\n--- Example 3: Exchange Metadata ---")
    meta = market_data.get_meta()
    
    if meta and 'universe' in meta:
        logger.info(f"Available trading pairs: {len(meta['universe'])}")
        logger.info("First 5 pairs:")
        for i, pair in enumerate(meta['universe'][:5]):
            logger.info(f"  {i+1}. {pair.get('name', 'N/A')}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Quick start example completed!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
