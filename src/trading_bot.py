"""
Main trading bot orchestrator
"""
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from .utils.logger import get_logger
from .utils.config_loader import get_config
from .data.market_data import MarketDataCollector, MarketDataCache
from .data.indicators import TechnicalIndicators
from .trading.executor import TradeExecutor
from .risk.risk_manager import RiskManager
from .ai.deepseek_agent import DeepseekAgent
from .strategy.ai_strategy import AITradingStrategy


class TradingBot:
    """Main trading bot that orchestrates all components"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize trading bot
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = get_config(config_path)
        self.config.validate()
        
        # Initialize logger
        log_config = self.config.get_section('logging')
        self.logger = get_logger(
            level=log_config.get('level', 'INFO'),
            log_to_file=log_config.get('log_to_file', True),
            log_file=log_config.get('log_file')
        )
        
        self.logger.info("=" * 60)
        self.logger.info("Initializing HyperLiquid AI Trading Bot")
        self.logger.info("=" * 60)
        
        # Initialize components
        self.market_data = MarketDataCollector(
            self.config.get_section('hyperliquid')
        )
        self.data_cache = MarketDataCache(
            ttl=self.config.get('data.cache_expiry', 300)
        )
        self.indicators = TechnicalIndicators()
        self.executor = TradeExecutor(
            config=self.config.get_section('hyperliquid'),
            paper_trading=self.config.get('trading.mode') == 'paper'
        )
        self.risk_manager = RiskManager(
            self.config.get_section('risk')
        )
        self.ai_agent = DeepseekAgent(
            self.config.get_section('deepseek')
        )
        self.strategy = AITradingStrategy(
            market_data=self.market_data,
            indicators=self.indicators,
            ai_agent=self.ai_agent,
            risk_manager=self.risk_manager,
            config=self.config.get_section('strategy')
        )
        
        # Trading state
        self.trading_pairs = self.config.get('trading.trading_pairs', [])
        self.trading_interval = self.config.get('trading.trading_interval', 60)
        self.is_running = False
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.trade_history: List[Dict[str, Any]] = []
        
        # Initialize capital
        initial_capital = self.config.get('trading.initial_capital', 10000)
        self.risk_manager.initialize_capital(initial_capital)
        
        self.logger.info("Trading Bot initialized successfully")
        self.logger.info(f"Trading pairs: {', '.join(self.trading_pairs)}")
        self.logger.info(f"Trading mode: {self.config.get('trading.mode')}")
        self.logger.info(f"Initial capital: ${initial_capital:,.2f}")
    
    def start(self):
        """Start the trading bot"""
        self.logger.info("Starting trading bot...")
        self.is_running = True
        
        try:
            while self.is_running:
                self._trading_loop()
                time.sleep(self.trading_interval)
        except KeyboardInterrupt:
            self.logger.info("Received stop signal")
            self.stop()
        except Exception as e:
            self.logger.error(f"Fatal error in trading loop: {e}", exc_info=True)
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        self.logger.info("Stopping trading bot...")
        self.is_running = False
        
        # Close all positions
        self._close_all_positions()
        
        # Print final statistics
        self._print_statistics()
        
        self.logger.info("Trading bot stopped")
    
    def _trading_loop(self):
        """Main trading loop iteration"""
        try:
            self.logger.info("-" * 60)
            self.logger.info(f"Trading loop iteration at {datetime.now()}")
            
            # Update account state
            self._update_account_state()
            
            # Check risk limits
            if not self.risk_manager.trading_enabled:
                self.logger.warning("Trading disabled due to risk limits")
                return
            
            # Analyze each trading pair
            for coin in self.trading_pairs:
                self._process_coin(coin)
            
            # Log current state
            self._log_current_state()
            
        except Exception as e:
            self.logger.error(f"Error in trading loop: {e}", exc_info=True)
    
    def _process_coin(self, coin: str):
        """
        Process a single coin
        
        Args:
            coin: Coin symbol
        """
        try:
            self.logger.debug(f"Processing {coin}...")
            
            # Get current position
            current_position = self.positions.get(coin)
            
            # Get trading decision from strategy
            decision = self.strategy.analyze_and_decide(coin, current_position)
            
            action = decision.get('action', 'hold')
            
            self.logger.info(
                f"{coin}: Action={action.upper()}, "
                f"Reason={decision.get('reason', 'N/A')}"
            )
            
            # Execute action
            if action == 'buy':
                self._execute_buy(coin, decision)
            elif action == 'sell':
                self._execute_sell(coin, decision)
            elif action == 'close':
                self._execute_close(coin, decision)
            
        except Exception as e:
            self.logger.error(f"Error processing {coin}: {e}")
    
    def _execute_buy(self, coin: str, decision: Dict[str, Any]):
        """Execute buy order"""
        try:
            size = decision.get('size', 0)
            price = decision.get('entry_price', 0)
            leverage = decision.get('leverage', 3)
            stop_loss = decision.get('stop_loss', 0)
            take_profit = decision.get('take_profit', 0)
            
            # Place order
            result = self.executor.place_order(
                coin=coin,
                is_buy=True,
                size=size,
                price=price,
                leverage=leverage
            )
            
            if result.get('status') == 'ok':
                # Add position to risk manager
                self.risk_manager.add_position(
                    coin=coin,
                    size=size,
                    entry_price=price,
                    is_long=True,
                    leverage=leverage
                )
                
                # Track position
                self.positions[coin] = {
                    'coin': coin,
                    'size': size,
                    'entry_price': price,
                    'is_long': True,
                    'leverage': leverage,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'entry_time': datetime.now()
                }
                
                self.logger.info(
                    f"BUY order executed: {coin} {size} @ ${price:.2f} "
                    f"(leverage: {leverage}x, SL: ${stop_loss:.2f}, TP: ${take_profit:.2f})"
                )
            else:
                self.logger.error(f"BUY order failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error executing buy order: {e}")
    
    def _execute_sell(self, coin: str, decision: Dict[str, Any]):
        """Execute sell order"""
        try:
            size = decision.get('size', 0)
            price = decision.get('entry_price', 0)
            leverage = decision.get('leverage', 3)
            stop_loss = decision.get('stop_loss', 0)
            take_profit = decision.get('take_profit', 0)
            
            # Place order
            result = self.executor.place_order(
                coin=coin,
                is_buy=False,
                size=size,
                price=price,
                leverage=leverage
            )
            
            if result.get('status') == 'ok':
                # Add position to risk manager
                self.risk_manager.add_position(
                    coin=coin,
                    size=size,
                    entry_price=price,
                    is_long=False,
                    leverage=leverage
                )
                
                # Track position
                self.positions[coin] = {
                    'coin': coin,
                    'size': size,
                    'entry_price': price,
                    'is_long': False,
                    'leverage': leverage,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'entry_time': datetime.now()
                }
                
                self.logger.info(
                    f"SELL order executed: {coin} {size} @ ${price:.2f} "
                    f"(leverage: {leverage}x, SL: ${stop_loss:.2f}, TP: ${take_profit:.2f})"
                )
            else:
                self.logger.error(f"SELL order failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error executing sell order: {e}")
    
    def _execute_close(self, coin: str, decision: Dict[str, Any]):
        """Execute close position"""
        try:
            if coin not in self.positions:
                return
            
            position = self.positions[coin]
            
            # Place opposite order to close
            result = self.executor.place_order(
                coin=coin,
                is_buy=not position['is_long'],
                size=position['size'],
                price=None,  # Market order
                reduce_only=True
            )
            
            if result.get('status') == 'ok':
                # Remove from tracking
                self.risk_manager.remove_position(coin)
                del self.positions[coin]
                
                # Record trade
                self.trade_history.append({
                    'coin': coin,
                    'entry_time': position['entry_time'],
                    'exit_time': datetime.now(),
                    'entry_price': position['entry_price'],
                    'size': position['size'],
                    'is_long': position['is_long'],
                    'reason': decision.get('reason', 'N/A')
                })
                
                self.logger.info(f"Position closed: {coin} - {decision.get('reason', 'N/A')}")
            else:
                self.logger.error(f"Close order failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
    
    def _close_all_positions(self):
        """Close all open positions"""
        self.logger.info("Closing all positions...")
        for coin in list(self.positions.keys()):
            self._execute_close(coin, {'reason': 'Bot shutdown'})
    
    def _update_account_state(self):
        """Update account state from exchange"""
        # In paper trading mode, this would calculate based on positions
        # In live mode, query actual account state
        pass
    
    def _log_current_state(self):
        """Log current trading state"""
        metrics = self.risk_manager.get_risk_metrics()
        
        self.logger.info(
            f"Capital: ${metrics['current_capital']:,.2f} | "
            f"Drawdown: {metrics['drawdown']:.2%} | "
            f"Positions: {metrics['num_positions']}"
        )
    
    def _print_statistics(self):
        """Print final statistics"""
        self.logger.info("=" * 60)
        self.logger.info("Final Statistics")
        self.logger.info("=" * 60)
        
        metrics = self.risk_manager.get_risk_metrics()
        
        self.logger.info(f"Initial Capital: ${metrics['initial_capital']:,.2f}")
        self.logger.info(f"Final Capital: ${metrics['current_capital']:,.2f}")
        self.logger.info(f"Total Return: {((metrics['current_capital'] / metrics['initial_capital']) - 1) * 100:.2f}%")
        self.logger.info(f"Max Drawdown: {metrics['drawdown']:.2%}")
        self.logger.info(f"Total Trades: {len(self.trade_history)}")
        
        if self.trade_history:
            # Calculate win rate
            # wins = sum(1 for t in self.trade_history if t.get('pnl', 0) > 0)
            # win_rate = wins / len(self.trade_history)
            # self.logger.info(f"Win Rate: {win_rate:.2%}")
            pass


def main():
    """Main entry point"""
    bot = TradingBot()
    bot.start()


if __name__ == "__main__":
    main()
