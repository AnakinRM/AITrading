"""
Main trading bot orchestrator
"""
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .utils.logger import get_logger
from .utils.config_loader import get_config
from .data.market_data import MarketDataCollector, MarketDataCache
from .data.indicators import TechnicalIndicators
from .data.enhanced_market_data import EnhancedMarketDataCollector
from .trading.executor import TradeExecutor
from .risk.risk_manager import RiskManager
from .ai.deepseek_agent import DeepseekAgent
from .ai.deepseek_trading_agent import DeepseekTradingAgent
from .news.news_analyzer import NewsAnalyzer
from .strategy.ai_strategy import AITradingStrategy

EQUITY_LOG_HEADER = "timestamp,capital,unrealized_pnl,realized_pnl,drawdown,num_positions,total_position_value\n"
JOURNAL_LOG_HEADER = "timestamp,capital,unrealized_pnl,realized_pnl,num_positions,positions,details\n"


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
        self.enhanced_market_data = EnhancedMarketDataCollector(self.market_data)
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
        # Logging paths
        self.log_dir = Path("logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.ai_dialog_path = self.log_dir / "ai_dialogs.log"
        self.equity_log_path = self.log_dir / "equity_history.csv"
        self.journal_path = self.log_dir / "trading_journal.csv"
        
        # Clean historical artifacts (logs/news) on startup
        self._cleanup_historical_data()
        
        # Trading state
        self.trading_pairs = self.config.get('trading.trading_pairs', [])
        self.trading_interval = max(self.config.get('trading.trading_interval', 300), 300)
        self.is_running = False
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.trade_history: List[Dict[str, Any]] = []
        self.realized_pnl = 0.0
        self.last_prices: Dict[str, float] = {}
        if not self.equity_log_path.exists():
            self.equity_log_path.write_text(EQUITY_LOG_HEADER, encoding="utf-8")
        if not self.journal_path.exists():
            self.journal_path.write_text(JOURNAL_LOG_HEADER, encoding="utf-8")
        
        # Initialize capital
        initial_capital = self.config.get('trading.initial_capital', 10000)
        self.initial_capital_value = initial_capital
        self.risk_manager.initialize_capital(initial_capital)
        
        self.logger.info("Trading Bot initialized successfully")
        self.logger.info(f"Trading pairs: {', '.join(self.trading_pairs)}")
        self.logger.info(f"Trading mode: {self.config.get('trading.mode')}")
        self.logger.info(f"Initial capital: ${initial_capital:,.2f}")

    def _cleanup_historical_data(self) -> None:
        """Remove stale log/news data on startup."""
        try:
            self.ai_dialog_path.write_text("", encoding="utf-8")
            self.logger.info(f"Cleared historical data: {self.ai_dialog_path}")
        except Exception as exc:
            self.logger.warning(f"Failed to reset {self.ai_dialog_path}: {exc}")

        try:
            self.equity_log_path.write_text(EQUITY_LOG_HEADER, encoding="utf-8")
            self.logger.info(f"Reset equity log: {self.equity_log_path}")
        except Exception as exc:
            self.logger.warning(f"Failed to reset equity log {self.equity_log_path}: {exc}")

        try:
            self.journal_path.write_text(JOURNAL_LOG_HEADER, encoding="utf-8")
            self.logger.info(f"Reset trading journal: {self.journal_path}")
        except Exception as exc:
            self.logger.warning(f"Failed to reset trading journal {self.journal_path}: {exc}")

    @staticmethod
    def _extract_price(value: Any, default: float = 0.0) -> float:
        """Convert price-like values (possibly lists) into float."""
        if isinstance(value, (list, tuple)):
            for item in value:
                try:
                    return float(item)
                except (TypeError, ValueError):
                    continue
            return float(default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    def _calculate_portfolio_value(self, prices: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """Compute current equity, splitting realized/unrealized components."""
        prices = prices or self.last_prices
        unrealized = 0.0
        total_position_value = 0.0

        for coin, position in self.positions.items():
            current_price = self._extract_price(prices.get(coin, position['entry_price']), position['entry_price'])
            entry_price = position['entry_price']
            size = position['size']
            leverage = position.get('leverage', 1)
            total_position_value += size * current_price

            price_diff = current_price - entry_price
            if not position.get('is_long', True):
                price_diff = entry_price - current_price
            unrealized += price_diff * size * leverage

        capital = self.initial_capital_value + self.realized_pnl + unrealized
        return {
            "capital": capital,
            "unrealized": unrealized,
            "total_position_value": total_position_value,
        }

    def _append_equity_log(self, metrics: Dict[str, Any]) -> None:
        """Write a row to the equity CSV."""
        try:
            with open(self.equity_log_path, "a", encoding="utf-8") as fp:
                fp.write(
                    f"{datetime.now().isoformat()},"
                    f"{metrics['capital']},"
                    f"{metrics['unrealized']},"
                    f"{self.realized_pnl},"
                    f"{self.risk_manager.calculate_drawdown()},"
                    f"{len(self.positions)},"
                    f"{metrics['total_position_value']}\n"
                )
        except Exception as exc:
            self.logger.error(f"Failed to append equity log: {exc}")

    def _update_equity_metrics(self, prices: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """Refresh risk metrics and persist equity snapshot."""
        metrics = self._calculate_portfolio_value(prices)
        self.risk_manager.update_capital(metrics['capital'])
        self._append_equity_log(metrics)
        return metrics

    def _positions_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Return a simplified snapshot of current positions."""
        return {
            coin: {
                "size": pos.get('size', 0),
                "entry_price": pos.get('entry_price', 0),
                "is_long": pos.get('is_long', True),
                "leverage": pos.get('leverage', 1),
                "stop_loss": pos.get('stop_loss'),
                "take_profit": pos.get('take_profit'),
            }
            for coin, pos in self.positions.items()
        }

    def _log_journal(self, event_type: str, details: Dict[str, Any], metrics: Optional[Dict[str, float]] = None) -> None:
        """Append a structured entry to the trading journal."""
        if metrics is None:
            metrics = self._calculate_portfolio_value(self.last_prices)
        try:
            with open(self.journal_path, "a", encoding="utf-8") as fp:
                fp.write(
                    f"{datetime.now().isoformat()},"
                    f"{metrics['capital']},"
                    f"{metrics['unrealized']},"
                    f"{self.realized_pnl},"
                    f"{len(self.positions)},"
                    f"\"{json.dumps(self._positions_snapshot(), ensure_ascii=False)}\","
                    f"\"{json.dumps(details, ensure_ascii=False)}\"\n"
                )
        except Exception as exc:
            self.logger.warning(f"Failed to log journal entry: {exc}")

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
            if self.risk_manager.enforce_limits and not self.risk_manager.trading_enabled:
                self.logger.warning("Trading disabled due to risk limits")
                return
            
            # Collect market data for all symbols
            all_market_data = self._collect_all_market_data()
            self.last_prices = {
                coin: data.get('current_price')
                for coin, data in all_market_data['market_data'].items()
                if data.get('current_price') is not None
            }
            
            # Get trading plan for all symbols in one AI call
            trading_plan = self.ai_agent.generate_trading_plan(
                market_data=all_market_data['market_data'],
                current_positions=self.positions,
                unavailable_symbols=all_market_data['unavailable'],
                news_summary="",
                orders=self._get_recent_orders()
            )
            
            # Execute trading plan
            self._execute_trading_plan(trading_plan)
            metrics = self._update_equity_metrics(self.last_prices)
            self._log_journal("ai_plan", trading_plan, metrics)
            
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
            price = self._extract_price(decision.get('entry_price', 0))
            leverage = decision.get('leverage') or self.risk_manager.default_leverage or 1
            if not isinstance(leverage, (int, float)) or leverage <= 0:
                leverage = self.risk_manager.default_leverage or 1
            stop_loss = self._extract_price(decision.get('stop_loss', 0))
            take_profit_raw = decision.get('take_profit', 0)
            take_profit = self._extract_price(take_profit_raw)
            take_profit_targets = (
                list(take_profit_raw)
                if isinstance(take_profit_raw, (list, tuple))
                else [take_profit]
            )
            market_price = self.last_prices.get(coin)
            if price <= 0 and market_price:
                self.logger.warning(
                    f"{coin}: Replacing invalid buy entry price with market price {market_price}"
                )
                price = market_price
            if price <= 0:
                self.logger.error(
                    f"{coin}: Cannot execute buy order due to missing price information"
                )
                self._log_journal(
                    "order_error",
                    {
                        "coin": coin,
                        "action": "buy",
                        "error": "Missing entry price",
                        "decision": decision,
                    }
                )
                return
            
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
                    'take_profit_targets': take_profit_targets,
                    'entry_time': datetime.now()
                }
                
                self.logger.info(
                    f"BUY order executed: {coin} {size} @ ${price:.2f} "
                    f"(leverage: {leverage}x, SL: ${stop_loss:.2f}, TP: ${take_profit:.2f})"
                )
                self._log_journal(
                    "order_fill",
                    {
                        "coin": coin,
                        "action": "buy",
                        "size": size,
                        "entry_price": price,
                        "leverage": leverage,
                        "stop_loss": stop_loss,
                        "take_profit_targets": take_profit_targets,
                        "reason": decision.get('reason'),
                    }
                )
            else:
                self.logger.error(f"BUY order failed: {result.get('error', 'Unknown error')}")
                self._log_journal(
                    "order_error",
                    {
                        "coin": coin,
                        "action": "buy",
                        "error": result.get('error', 'Unknown error'),
                        "decision": decision,
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Error executing buy order: {e}")
    
    def _execute_sell(self, coin: str, decision: Dict[str, Any]):
        """Execute sell order"""
        try:
            size = decision.get('size', 0)
            price = self._extract_price(decision.get('entry_price', 0))
            leverage = decision.get('leverage') or self.risk_manager.default_leverage or 1
            if not isinstance(leverage, (int, float)) or leverage <= 0:
                leverage = self.risk_manager.default_leverage or 1
            stop_loss = self._extract_price(decision.get('stop_loss', 0))
            take_profit_raw = decision.get('take_profit', 0)
            take_profit = self._extract_price(take_profit_raw)
            take_profit_targets = (
                list(take_profit_raw)
                if isinstance(take_profit_raw, (list, tuple))
                else [take_profit]
            )
            market_price = self.last_prices.get(coin)
            if price <= 0 and market_price:
                self.logger.warning(
                    f"{coin}: Replacing invalid sell entry price with market price {market_price}"
                )
                price = market_price
            if price <= 0:
                self.logger.error(
                    f"{coin}: Cannot execute sell order due to missing price information"
                )
                self._log_journal(
                    "order_error",
                    {
                        "coin": coin,
                        "action": "sell",
                        "error": "Missing entry price",
                        "decision": decision,
                    }
                )
                return
            
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
                    'take_profit_targets': take_profit_targets,
                    'entry_time': datetime.now()
                }
                
                self.logger.info(
                    f"SELL order executed: {coin} {size} @ ${price:.2f} "
                    f"(leverage: {leverage}x, SL: ${stop_loss:.2f}, TP: ${take_profit:.2f})"
                )
                self._log_journal(
                    "order_fill",
                    {
                        "coin": coin,
                        "action": "sell",
                        "size": size,
                        "entry_price": price,
                        "leverage": leverage,
                        "stop_loss": stop_loss,
                        "take_profit_targets": take_profit_targets,
                        "reason": decision.get('reason'),
                    }
                )
            else:
                self.logger.error(f"SELL order failed: {result.get('error', 'Unknown error')}")
                self._log_journal(
                    "order_error",
                    {
                        "coin": coin,
                        "action": "sell",
                        "error": result.get('error', 'Unknown error'),
                        "decision": decision,
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Error executing sell order: {e}")
    
    def _execute_close(self, coin: str, decision: Dict[str, Any]):
        """Execute close position"""
        try:
            if coin not in self.positions:
                return
            
            position = self.positions[coin]
            exit_price = self._extract_price(self.last_prices.get(coin, position['entry_price']), position['entry_price'])
            
            # Place opposite order to close
            result = self.executor.place_order(
                coin=coin,
                is_buy=not position['is_long'],
                size=position['size'],
                price=None,  # Market order
                reduce_only=True
            )
            
            if result.get('status') == 'ok':
                # Calculate PnL
                entry_price = position['entry_price']
                size = position['size']
                leverage = position.get('leverage', 1)
                price_diff = exit_price - entry_price
                if not position['is_long']:
                    price_diff = entry_price - exit_price
                pnl = price_diff * size * leverage
                self.realized_pnl += pnl

                # Remove from tracking
                self.risk_manager.remove_position(coin)
                del self.positions[coin]
                
                # Record trade
                self.trade_history.append({
                    'coin': coin,
                    'entry_time': position['entry_time'],
                    'exit_time': datetime.now(),
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'size': position['size'],
                    'is_long': position['is_long'],
                    'pnl': pnl,
                    'reason': decision.get('reason', 'N/A')
                })
                
                self.logger.info(f"Position closed: {coin} - {decision.get('reason', 'N/A')}")
                self._log_journal(
                    "order_close",
                    {
                        "coin": coin,
                        "exit_price": exit_price,
                        "pnl": pnl,
                        "reason": decision.get('reason'),
                    }
                )
            else:
                self.logger.error(f"Close order failed: {result.get('error', 'Unknown error')}")
                self._log_journal(
                    "order_error",
                    {
                        "coin": coin,
                        "action": "close",
                        "error": result.get('error', 'Unknown error'),
                        "decision": decision,
                    }
                )
                
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
        Collect comprehensive market data for all trading pairs
        including technical indicators, OI, funding rates
        
        Returns:
            Dictionary with 'market_data' and 'unavailable' keys
        """
        all_market_data = {}
        unavailable = []
        
        for coin in self.trading_pairs:
            try:
                # Get comprehensive market data with technical indicators
                coin_data = self.enhanced_market_data.get_comprehensive_market_data(coin)
                
                if coin_data.get('available'):
                    all_market_data[coin] = coin_data
                    self.logger.debug(f"{coin}: ${coin_data.get('current_price', 0):,.2f}")
                else:
                    unavailable.append(coin)
                    self.logger.warning(f"{coin}: {coin_data.get('error', 'Data not available')}")
                    
            except Exception as e:
                self.logger.error(f"Error getting data for {coin}: {e}")
                unavailable.append(coin)
        
        self.logger.info(f"Collected data for {len(all_market_data)} symbols, {len(unavailable)} unavailable")
        
        return {
            'market_data': all_market_data,
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
                direction_upper = str(direction).upper()
                if direction_upper == 'LONG':
                    action = 'buy'
                elif direction_upper == 'SHORT':
                    action = 'sell'
                elif direction_upper.startswith('HOLD'):
                    self.logger.info(f"{symbol}: HOLD signal ({direction_upper}), skipping trade execution")
                    self._log_journal(
                        "hold_signal",
                        {
                            "coin": symbol,
                            "direction": direction_upper,
                            "reason": candidate.get('rationale')
                        }
                    )
                    continue
                else:
                    self.logger.warning(f"Unknown direction {direction} for {symbol}, treating as HOLD")
                    self._log_journal(
                        "hold_signal",
                        {
                            "coin": symbol,
                            "direction": direction_upper,
                            "reason": candidate.get('rationale')
                        }
                    )
                    continue
                
                # Build decision dict compatible with existing execution methods
                entry = candidate.get('entry', {})
                position_info = candidate.get('position', {})
                market_price = self.last_prices.get(symbol)
                entry_price = self._extract_price(
                    entry.get('price'),
                    default=market_price or 0.0,
                )
                if entry.get('price') in (None, "", 0) and entry_price:
                    self.logger.debug(
                        f"{symbol}: Using market price {entry_price} as fallback entry"
                    )
                elif entry_price <= 0:
                    self.logger.warning(
                        f"{symbol}: No valid entry price available; skipping candidate"
                    )
                    self._log_journal(
                        "hold_signal",
                        {
                            "coin": symbol,
                            "direction": direction_upper,
                            "reason": "No valid entry price available",
                        }
                    )
                    continue
                
                size_pct = position_info.get('size_pct', 0.1)
                if not isinstance(size_pct, (int, float)) or size_pct <= 0:
                    size_pct = 0.1
                leverage_hint = position_info.get(
                    'leverage_hint',
                    self.risk_manager.default_leverage or 1,
                )
                if not isinstance(leverage_hint, (int, float)) or leverage_hint <= 0:
                    leverage_hint = self.risk_manager.default_leverage or 1

                decision = {
                    'action': action,
                    'entry_price': entry_price,
                    'stop_loss': candidate.get('stop_loss', 0),
                    'take_profit': candidate.get('take_profit', 0),
                    'size': size_pct,
                    'leverage': leverage_hint,
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
