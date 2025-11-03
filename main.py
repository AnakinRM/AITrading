#!/usr/bin/env python3
"""
HyperLiquid AI Trading Bot - Main Entry Point
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.trading_bot import TradingBot
from src.utils.logger import get_logger


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="HyperLiquid AI Trading Bot powered by Deepseek"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file (default: config/config.yaml)"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["paper", "live"],
        default=None,
        help="Trading mode (overrides config file)"
    )
    
    args = parser.parse_args()
    
    # Initialize logger
    logger = get_logger()
    
    try:
        # Create and start bot
        logger.info("Starting HyperLiquid AI Trading Bot...")
        bot = TradingBot(config_path=args.config)
        
        # Override mode if specified
        if args.mode:
            bot.config.config['trading']['mode'] = args.mode
            logger.info(f"Trading mode overridden to: {args.mode}")
        
        # Start trading
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
