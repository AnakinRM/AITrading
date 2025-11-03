#!/usr/bin/env python3
"""
Live Trading System - 7 Days Continuous Operation
Features:
- Hourly position and capital reports
- Real-time trade notifications
- Continuous 24/7 operation
- HyperLiquid paper trading
- $10,000 initial capital
"""
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
import signal
from openai import OpenAI

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "hyperliquid_trading_bot"))

from src.data.market_data import MarketDataCollector
from src.risk.risk_manager import RiskManager
from src.trading.executor import TradeExecutor
from src.utils.logger import get_logger


class LiveTradingSystem:
    """7-day continuous live trading system"""
    
    def __init__(self, initial_capital=10000):
        """Initialize live trading system"""
        self.logger = get_logger()
        self.initial_capital = initial_capital
        self.start_time = datetime.now()
        
        # Market data
        self.market_data = MarketDataCollector({
            'api_url': 'https://api.hyperliquid-testnet.xyz'
        })
        
        # Risk manager - Aggressive settings
        self.risk_manager = RiskManager({
            'max_position_per_coin': 0.40,
            'max_total_position': 1.0,
            'default_leverage': 5,
            'max_leverage': 10,
            'stop_loss_pct': 0.10,
            'take_profit_pct': 0.20,
            'max_drawdown': 0.35,
            'max_daily_loss': 0.20
        })
        
        # Executor
        self.executor = TradeExecutor(paper_trading=True)
        
        # Deepseek Reasoner
        api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Initialize capital
        self.risk_manager.initialize_capital(initial_capital)
        
        # Trading state
        self.coins = ['BTC', 'ETH', 'SOL']
        self.positions = {}
        self.trade_history = []
        
        # Timing
        self.last_trade_time = datetime.now()
        self.last_report_time = datetime.now()
        self.trade_interval = 300  # 5 minutes between trades
        self.report_interval = 300  # 5 minutes reports
        
        # Running flag
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("🛑 Shutdown signal received, closing positions...")
        self.logger.info("=" * 80)
        self.running = False
    
    def run(self, duration_days=7):
        """Run live trading for specified days"""
        end_time = self.start_time + timedelta(days=duration_days)
        
        self.logger.info("=" * 80)
        self.logger.info("🚀 LIVE TRADING SYSTEM - 7 DAYS CONTINUOUS OPERATION")
        self.logger.info("=" * 80)
        self.logger.info("")
        self.logger.info("📊 Configuration:")
        self.logger.info(f"  ⏰ Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"  ⏰ End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"  💰 Initial Capital: ${self.initial_capital:,.2f}")
        self.logger.info(f"  🎯 Trading Pairs: {', '.join(self.coins)}")
        self.logger.info(f"  🧠 Model: deepseek-chat")
        self.logger.info(f"  ⚡ Strategy: AGGRESSIVE (5x leverage, 40% positions)")
        self.logger.info(f"  ⏱️  Trade Interval: {self.trade_interval // 60} minutes")
        self.logger.info(f"  📊 Report Interval: {self.report_interval // 60} minutes")
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("")
        
        # Initial report
        self._hourly_report()
        
        # Main loop
        while self.running and datetime.now() < end_time:
            try:
                current_time = datetime.now()
                
                # Check if it's time to trade
                if (current_time - self.last_trade_time).total_seconds() >= self.trade_interval:
                    self._trading_cycle()
                    self.last_trade_time = current_time
                
                # Check if it's time to report
                if (current_time - self.last_report_time).total_seconds() >= self.report_interval:
                    self._hourly_report()
                    self.last_report_time = current_time
                
                # Sleep for a bit
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in main loop: {e}", exc_info=True)
                time.sleep(60)
        
        # Final report
        self._final_report()
    
    def _trading_cycle(self):
        """Execute one trading cycle"""
        try:
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info(f"🔄 TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info("=" * 80)
            
            # Get market data
            self.logger.info("")
            self.logger.info("📊 Market Prices:")
            mids = self.market_data.get_all_mids()
            
            if not mids:
                self.logger.warning("⚠️  No market data available")
                return
            
            prices = {}
            for coin in self.coins:
                if coin in mids:
                    price = float(mids[coin])
                    prices[coin] = price
                    
                    # Show price with change indicator
                    change_emoji = "📈" if price > 100000 else "📊"
                    self.logger.info(f"  {change_emoji} {coin}: ${price:,.2f}")
            
            # AI analysis and trading
            self.logger.info("")
            self.logger.info("🧠 AI Analysis & Trading Decisions:")
            
            for coin in self.coins:
                if coin not in prices:
                    continue
                
                price = prices[coin]
                position = self.positions.get(coin)
                
                # Get AI decision
                decision = self._get_ai_decision(coin, price, position)
                
                self.logger.info(f"  {coin}: {decision['action'].upper()} (Confidence: {decision['confidence']:.2f})")
                
                # Execute decision
                if decision['action'] == 'buy' and not position:
                    if decision['confidence'] >= 0.55:
                        self._execute_buy(coin, price, decision)
                elif decision['action'] == 'sell' and position:
                    if decision['confidence'] >= 0.50:
                        self._execute_sell(coin, price, decision)
            
            self.logger.info("")
            self.logger.info("=" * 80)
            
        except Exception as e:
            self.logger.error(f"❌ Trading cycle error: {e}", exc_info=True)
    
    def _get_ai_decision(self, coin, price, position):
        """Get AI trading decision"""
        try:
            # Get portfolio context
            metrics = self.risk_manager.get_risk_metrics()
            return_pct = ((metrics['current_capital'] / self.initial_capital) - 1) * 100
            
            # Build prompt
            position_str = f"LONG {position['size']:.4f} @ ${position['entry_price']:.2f}" if position else "None"
            
            prompt = f"""You are an elite crypto trader running a 7-day live trading operation.

CURRENT STATUS:
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Capital: ${metrics['current_capital']:,.2f}
- Return: {return_pct:+.2f}%
- Positions: {metrics['num_positions']}/3

COIN ANALYSIS for {coin}:
- Current Price: ${price:,.2f}
- Your Position: {position_str}

OBJECTIVE:
Maximize returns over 7 days with aggressive but disciplined trading.

Provide decision in JSON:
{{
    "action": "buy" or "sell" or "hold",
    "confidence": 0.0 to 1.0,
    "reasoning": "Brief explanation"
}}"""

            # Call Deepseek Chat
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an elite crypto trader."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=1.0  # Recommended for data analysis/trading
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '{' in content and '}' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
            else:
                json_str = content.strip()
            
            decision = json.loads(json_str)
            return decision
            
        except Exception as e:
            self.logger.error(f"❌ AI decision error: {e}")
            # Conservative fallback
            return {
                'action': 'hold',
                'confidence': 0.50,
                'reasoning': f'Error fallback: {str(e)[:50]}'
            }
    
    def _execute_buy(self, coin, price, decision):
        """Execute buy order with detailed reporting"""
        try:
            # Calculate position size
            metrics = self.risk_manager.get_risk_metrics()
            available_capital = metrics['current_capital']
            
            # Aggressive sizing
            target_value = available_capital * 0.35 * decision['confidence']
            size = target_value / price
            
            # Validate
            is_valid, reason = self.risk_manager.validate_trade(
                coin=coin,
                size=size,
                price=price,
                leverage=5
            )
            
            if not is_valid:
                # Try smaller size
                size = size * 0.7
                is_valid, reason = self.risk_manager.validate_trade(
                    coin=coin,
                    size=size,
                    price=price,
                    leverage=5
                )
                if not is_valid:
                    self.logger.warning(f"    ⚠️  Cannot buy {coin}: {reason}")
                    return
            
            # Execute
            result = self.executor.place_order(
                coin=coin,
                is_buy=True,
                size=size,
                price=price,
                leverage=5
            )
            
            if result.get('status') == 'ok':
                # Calculate position value
                position_value = size * price
                leveraged_value = position_value * 5
                
                # Update positions
                self.positions[coin] = {
                    'size': size,
                    'entry_price': price,
                    'leverage': 5,
                    'entry_time': datetime.now(),
                    'entry_value': position_value
                }
                
                self.risk_manager.add_position(
                    coin=coin,
                    size=size,
                    entry_price=price,
                    is_long=True,
                    leverage=5
                )
                
                # Record trade
                self.trade_history.append({
                    'time': datetime.now(),
                    'coin': coin,
                    'action': 'buy',
                    'price': price,
                    'size': size,
                    'value': position_value
                })
                
                # DETAILED BUY REPORT
                self.logger.info("")
                self.logger.info("  " + "=" * 76)
                self.logger.info(f"  📈 BUY ORDER EXECUTED - {coin}")
                self.logger.info("  " + "=" * 76)
                self.logger.info(f"  🪙  Coin: {coin}")
                self.logger.info(f"  💵 Price: ${price:,.2f}")
                self.logger.info(f"  📊 Size: {size:.6f} {coin}")
                self.logger.info(f"  💰 Position Value: ${position_value:,.2f}")
                self.logger.info(f"  ⚡ Leverage: 5x")
                self.logger.info(f"  💎 Leveraged Exposure: ${leveraged_value:,.2f}")
                self.logger.info(f"  🎯 Confidence: {decision['confidence']:.2%}")
                self.logger.info(f"  💭 Reasoning: {decision['reasoning'][:60]}...")
                self.logger.info(f"  ⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Show updated capital
                new_metrics = self.risk_manager.get_risk_metrics()
                self.logger.info("")
                self.logger.info(f"  💰 Capital After Trade: ${new_metrics['current_capital']:,.2f}")
                self.logger.info(f"  📊 Total Positions: {new_metrics['num_positions']}")
                self.logger.info("  " + "=" * 76)
                self.logger.info("")
                
        except Exception as e:
            self.logger.error(f"    ❌ Buy execution error: {e}", exc_info=True)
    
    def _execute_sell(self, coin, price, decision):
        """Execute sell order with detailed reporting"""
        try:
            if coin not in self.positions:
                return
            
            position = self.positions[coin]
            
            # Calculate PnL
            entry_price = position['entry_price']
            size = position['size']
            leverage = position['leverage']
            
            price_change = price - entry_price
            price_change_pct = (price_change / entry_price) * 100
            pnl_amount = price_change * size * leverage
            pnl_pct = price_change_pct * leverage
            
            # Execute
            result = self.executor.place_order(
                coin=coin,
                is_buy=False,
                size=size,
                price=price,
                reduce_only=True
            )
            
            if result.get('status') == 'ok':
                # Calculate exit value
                exit_value = size * price
                
                # Record trade
                self.trade_history.append({
                    'time': datetime.now(),
                    'coin': coin,
                    'action': 'sell',
                    'price': price,
                    'size': size,
                    'pnl': pnl_amount,
                    'pnl_pct': pnl_pct
                })
                
                # DETAILED SELL REPORT
                self.logger.info("")
                self.logger.info("  " + "=" * 76)
                pnl_emoji = "💚" if pnl_amount >= 0 else "💔"
                self.logger.info(f"  {pnl_emoji} SELL ORDER EXECUTED - {coin}")
                self.logger.info("  " + "=" * 76)
                self.logger.info(f"  🪙  Coin: {coin}")
                self.logger.info(f"  💵 Entry Price: ${entry_price:,.2f}")
                self.logger.info(f"  💵 Exit Price: ${price:,.2f}")
                self.logger.info(f"  📊 Size: {size:.6f} {coin}")
                self.logger.info(f"  📈 Price Change: {price_change_pct:+.2f}%")
                self.logger.info(f"  ⚡ Leverage: {leverage}x")
                self.logger.info("")
                self.logger.info(f"  💰 P&L Amount: ${pnl_amount:+,.2f}")
                self.logger.info(f"  📊 P&L Percentage: {pnl_pct:+.2f}%")
                self.logger.info(f"  ⏱️  Holding Time: {datetime.now() - position['entry_time']}")
                self.logger.info(f"  💭 Reasoning: {decision['reasoning'][:60]}...")
                self.logger.info(f"  ⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Remove position
                del self.positions[coin]
                self.risk_manager.remove_position(coin)
                
                # Show updated capital
                new_metrics = self.risk_manager.get_risk_metrics()
                new_return = ((new_metrics['current_capital'] / self.initial_capital) - 1) * 100
                self.logger.info("")
                self.logger.info(f"  💰 Capital After Trade: ${new_metrics['current_capital']:,.2f}")
                self.logger.info(f"  📈 Total Return: {new_return:+.2f}%")
                self.logger.info(f"  📊 Remaining Positions: {new_metrics['num_positions']}")
                self.logger.info("  " + "=" * 76)
                self.logger.info("")
                
        except Exception as e:
            self.logger.error(f"    ❌ Sell execution error: {e}", exc_info=True)
    
    def _hourly_report(self):
        """Generate hourly status report"""
        try:
            metrics = self.risk_manager.get_risk_metrics()
            current_capital = metrics['current_capital']
            return_pct = ((current_capital / self.initial_capital) - 1) * 100
            
            # Calculate runtime
            runtime = datetime.now() - self.start_time
            hours = runtime.total_seconds() / 3600
            
            self.logger.info("")
            self.logger.info("╔" + "=" * 78 + "╗")
            self.logger.info("║" + " " * 25 + "📊 HOURLY STATUS REPORT" + " " * 30 + "║")
            self.logger.info("╠" + "=" * 78 + "╣")
            self.logger.info(f"║  ⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " " * 43 + "║")
            self.logger.info(f"║  ⏱️  Runtime: {int(hours)}h {int((hours % 1) * 60)}m" + " " * 56 + "║")
            self.logger.info("╠" + "=" * 78 + "╣")
            self.logger.info("║  💰 CAPITAL STATUS" + " " * 59 + "║")
            self.logger.info("╠" + "-" * 78 + "╣")
            self.logger.info(f"║    Initial Capital:  ${self.initial_capital:>12,.2f}" + " " * 44 + "║")
            self.logger.info(f"║    Current Capital:  ${current_capital:>12,.2f}" + " " * 44 + "║")
            self.logger.info(f"║    Total Return:     {return_pct:>12.2f}%" + " " * 44 + "║")
            self.logger.info(f"║    P&L Amount:       ${(current_capital - self.initial_capital):>12,.2f}" + " " * 44 + "║")
            self.logger.info("╠" + "=" * 78 + "╣")
            self.logger.info("║  📊 POSITIONS" + " " * 64 + "║")
            self.logger.info("╠" + "-" * 78 + "╣")
            
            if self.positions:
                total_position_value = 0
                for coin, pos in self.positions.items():
                    # Get current price
                    mids = self.market_data.get_all_mids()
                    current_price = float(mids.get(coin, pos['entry_price']))
                    
                    # Calculate current value and PnL
                    position_value = pos['size'] * current_price
                    unrealized_pnl = (current_price - pos['entry_price']) * pos['size'] * pos['leverage']
                    unrealized_pnl_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100 * pos['leverage']
                    
                    total_position_value += position_value
                    
                    pnl_emoji = "📈" if unrealized_pnl >= 0 else "📉"
                    
                    self.logger.info(f"║  {pnl_emoji} {coin}" + " " * 71 + "║")
                    self.logger.info(f"║    Size: {pos['size']:.6f} {coin}" + " " * (65 - len(coin)) + "║")
                    self.logger.info(f"║    Entry: ${pos['entry_price']:,.2f}  |  Current: ${current_price:,.2f}" + " " * 38 + "║")
                    self.logger.info(f"║    Position Value: ${position_value:,.2f}" + " " * 50 + "║")
                    self.logger.info(f"║    Unrealized P&L: ${unrealized_pnl:+,.2f} ({unrealized_pnl_pct:+.2f}%)" + " " * 38 + "║")
                    self.logger.info(f"║    Leverage: {pos['leverage']}x" + " " * 65 + "║")
                    self.logger.info("║  " + "-" * 76 + "║")
                
                self.logger.info(f"║  💎 Total Position Value: ${total_position_value:,.2f}" + " " * 44 + "║")
                self.logger.info(f"║  📊 Number of Positions: {len(self.positions)}" + " " * 53 + "║")
            else:
                self.logger.info("║    No open positions" + " " * 57 + "║")
            
            self.logger.info("╠" + "=" * 78 + "╣")
            self.logger.info("║  📈 TRADING STATISTICS" + " " * 55 + "║")
            self.logger.info("╠" + "-" * 78 + "╣")
            
            # Calculate stats
            total_trades = len(self.trade_history)
            completed_trades = [t for t in self.trade_history if t['action'] == 'sell']
            wins = sum(1 for t in completed_trades if t.get('pnl', 0) > 0)
            win_rate = (wins / len(completed_trades) * 100) if completed_trades else 0
            total_pnl = sum(t.get('pnl', 0) for t in completed_trades)
            
            self.logger.info(f"║    Total Trades: {total_trades}" + " " * 62 + "║")
            self.logger.info(f"║    Completed Trades: {len(completed_trades)}" + " " * 57 + "║")
            self.logger.info(f"║    Win Rate: {win_rate:.1f}%" + " " * 64 + "║")
            self.logger.info(f"║    Realized P&L: ${total_pnl:+,.2f}" + " " * 54 + "║")
            self.logger.info("╚" + "=" * 78 + "╝")
            self.logger.info("")
            
        except Exception as e:
            self.logger.error(f"❌ Hourly report error: {e}", exc_info=True)
    
    def _final_report(self):
        """Generate final report"""
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("🏁 FINAL REPORT - 7 DAY LIVE TRADING COMPLETED")
        self.logger.info("=" * 80)
        
        # Close all positions
        if self.positions:
            self.logger.info("")
            self.logger.info("Closing all remaining positions...")
            mids = self.market_data.get_all_mids()
            for coin in list(self.positions.keys()):
                if coin in mids:
                    price = float(mids[coin])
                    decision = {'confidence': 1.0, 'reasoning': 'Final position close'}
                    self._execute_sell(coin, price, decision)
        
        # Final stats
        self._hourly_report()
        
        metrics = self.risk_manager.get_risk_metrics()
        runtime = datetime.now() - self.start_time
        
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("📊 SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"  Runtime: {runtime}")
        self.logger.info(f"  Initial Capital: ${self.initial_capital:,.2f}")
        self.logger.info(f"  Final Capital: ${metrics['current_capital']:,.2f}")
        self.logger.info(f"  Total Return: {((metrics['current_capital'] / self.initial_capital) - 1) * 100:+.2f}%")
        self.logger.info(f"  Total Trades: {len(self.trade_history)}")
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("✅ Live trading system shutdown complete")
        self.logger.info("=" * 80)


def main():
    """Main entry point"""
    api_key = os.getenv('DEEPSEEK_API_KEY', '')
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY not set")
        sys.exit(1)
    
    # Create and run live trading system
    system = LiveTradingSystem(initial_capital=10000)
    system.run(duration_days=7)


if __name__ == "__main__":
    main()
