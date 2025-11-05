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
from .ai.deepseek_trading_agent import DeepseekTradingAgent
from .news.news_analyzer import NewsAnalyzer
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
        
        # Initialize news analyzer if enabled
        news_config = self.config.get_section('news')
        self.news_analyzer = None
        if news_config.get('enabled', True):
            try:
                self.news_analyzer = NewsAnalyzer(
                    api_key=self.config.get('deepseek.api_key'),
                    storage_dir=news_config.get('news_data_dir', 'news_data')
                )
                self.logger.info("News integration enabled")
            except Exception as e:
                self.logger.warning(f"Failed to initialize news analyzer: {e}")
        
        # Use new DeepseekTradingAgent with news integration
        self.ai_agent = DeepseekTradingAgent(
            config=self.config.get_section('deepseek'),
            news_analyzer=self.news_analyzer
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
        
        # Fetch news from the past hour before starting
        self._fetch_startup_news()
        
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
        """Main trading loop iteration - Single AI call for all symbols"""
        try:
            self.logger.info("-" * 60)
            self.logger.info(f"Trading loop iteration at {datetime.now()}")
            self.logger.info("[ORCHESTRATOR MODE] Calling AI once for all symbols")
            
            # Update account state
            self._update_account_state()
            
            # Check risk limits
            if not self.risk_manager.trading_enabled:
                self.logger.warning("Trading disabled due to risk limits")
                return
            
            # Collect market data for all symbols
            all_market_data = self._collect_all_market_data()
            
            # Get trading plan for all symbols in one AI call
            trading_plan = self.ai_agent.generate_trading_plan(
                market_data=all_market_data['prices'],
                current_positions=self.positions,
                unavailable_symbols=all_market_data['unavailable'],
                news_summary="",
                orders=self._get_recent_orders()
            )
            
            # Execute trading plan
            self._execute_trading_plan(trading_plan)
            
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
    
    def _fetch_startup_news(self):
        """
        Fetch news from the past hour at startup
        """
        if not self.news_analyzer:
            self.logger.info("News analyzer not available, skipping startup news fetch")
            return
        
        try:
            from datetime import datetime, timedelta
            
            self.logger.info("=" * 60)
            self.logger.info("Fetching news from the past hour...")
            self.logger.info("=" * 60)
            
            # Calculate time range (past 1 hour)
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            self.logger.info(f"Time range: {start_time} to {end_time}")
            
            # Fetch hourly news
            news_items = self.news_analyzer.storage.get_hourly_news_range(start_time, end_time)
            
            if news_items:
                self.logger.info(f"✅ Found {len(news_items)} news items from the past hour")
                for item in news_items:
                    self.logger.info(f"  - [{item.get('timestamp')}] {item.get('summary', 'N/A')[:80]}...")
            else:
                self.logger.info("ℹ️  No news found in the past hour")
                self.logger.info("💡 Tip: Run news collection script to populate news data")
            
            # Also check daily summaries
            today = datetime.now().date()
            daily_summary = self.news_analyzer.storage.get_daily_summary(today)
            
            if daily_summary:
                self.logger.info(f"✅ Found today's daily summary")
                self.logger.info(f"  Key themes: {', '.join(daily_summary.get('key_themes', [])[:3])}")
            else:
                self.logger.info("ℹ️  No daily summary for today yet")
            
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"Error fetching startup news: {e}", exc_info=True)
    
    def _collect_all_market_data(self) -> Dict[str, Any]:
        """
        Collect market data for all trading pairs in one go
        
        Returns:
            Dictionary with 'prices' and 'unavailable' keys
        """
        all_prices = {}
        unavailable = []
        
        for coin in self.trading_pairs:
            try:
                # Get current price
                current_price = self.market_data.get_current_price(coin)
                
                if current_price and current_price > 0:
                    all_prices[coin] = {
                        'price': current_price,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.logger.debug(f"{coin}: ${current_price:,.2f}")
                else:
                    unavailable.append(coin)
                    self.logger.warning(f"{coin}: No valid price data")
                    
            except Exception as e:
                self.logger.error(f"Error getting price for {coin}: {e}")
                unavailable.append(coin)
        
        self.logger.info(f"Collected data for {len(all_prices)} symbols, {len(unavailable)} unavailable")
        
        return {
            'prices': all_prices,
            'unavailable': unavailable
        }
    
    def _get_recent_orders(self) -> List[Dict[str, Any]]:
        """
        Get recent orders for context
        
        Returns:
            List of recent order dictionaries
        """
        # Return last 10 trades from history
        return self.trade_history[-10:] if self.trade_history else []
    
    def _execute_trading_plan(self, trading_plan: Dict[str, Any]):
        """
        Execute the trading plan generated by AI
        
        Args:
            trading_plan: Trading plan dictionary from DeepseekTradingAgent
        """
        candidates = trading_plan.get('candidates', [])
        
        if not candidates:
            self.logger.info("No trading candidates in plan")
            return
        
        self.logger.info(f"Executing trading plan with {len(candidates)} candidates")
        
        for candidate in candidates:
            try:
                symbol = candidate.get('symbol')
                direction = candidate.get('direction')
                
                if symbol not in self.trading_pairs:
                    self.logger.warning(f"Skipping {symbol}: not in allowed symbols")
                    continue
                
                # Convert to action
                if direction == 'LONG':
                    action = 'buy'
                elif direction == 'SHORT':
                    action = 'sell'
                else:
                    self.logger.warning(f"Unknown direction {direction} for {symbol}")
                    continue
                
                # Build decision dict compatible with existing execution methods
                entry = candidate.get('entry', {})
                position_info = candidate.get('position', {})
                
                decision = {
                    'action': action,
                    'entry_price': entry.get('price', 0),
                    'stop_loss': candidate.get('stop_loss', 0),
                    'take_profit': candidate.get('take_profit', 0),
                    'size': position_info.get('size_pct', 0.1),
                    'leverage': position_info.get('leverage_hint', 3),
                    'reason': candidate.get('rationale', 'AI orchestrator decision'),
                    'confidence': 0.8  # Default confidence
                }
                
                self.logger.info(
                    f"{symbol}: Action={action.upper()}, "
                    f"Reason={decision.get('reason', 'N/A')[:50]}..."
                )
                
                # Execute using existing methods
                if action == 'buy':
                    self._execute_buy(symbol, decision)
                elif action == 'sell':
                    self._execute_sell(symbol, decision)
                    
            except Exception as e:
                self.logger.error(f"Error executing candidate for {symbol}: {e}")


def main():
    """Main entry point"""
    bot = TradingBot()
    bot.start()


if __name__ == "__main__":
    main()
