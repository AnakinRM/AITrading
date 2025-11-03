#!/usr/bin/env python3
"""
Alpha Arena Style Trading with Deepseek Reasoner
Uses deepseek-reasoner (thinking mode) for better decision making
Target: +76% return like Alpha Arena Deepseek V3.1
"""
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "hyperliquid_trading_bot"))

from src.data.market_data import MarketDataCollector
from src.risk.risk_manager import RiskManager
from src.trading.executor import TradeExecutor
from src.utils.logger import get_logger

from openai import OpenAI


class ReasonerTrader:
    """Trading system using Deepseek Reasoner (thinking mode)"""
    
    def __init__(self, start_date, initial_capital=10000):
        """Initialize trader"""
        self.logger = get_logger()
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        self.initial_capital = initial_capital
        
        # Market data
        self.market_data = MarketDataCollector({
            'api_url': 'https://api.hyperliquid-testnet.xyz'
        })
        
        # Risk manager - Alpha Arena style (aggressive)
        self.risk_manager = RiskManager({
            'max_position_per_coin': 0.40,  # 40% per coin
            'max_total_position': 1.0,      # 100% total
            'default_leverage': 5,
            'max_leverage': 10,
            'stop_loss_pct': 0.10,
            'take_profit_pct': 0.20,
            'max_drawdown': 0.35,
            'max_daily_loss': 0.20
        })
        
        # Executor
        self.executor = TradeExecutor(paper_trading=True)
        
        # Deepseek Reasoner client
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
        
        # Results
        self.equity_curve = []
        self.day = 0
    
    def run(self, num_days=12):
        """Run trading simulation"""
        self.logger.info("=" * 80)
        self.logger.info("🧠 Deepseek Reasoner Trading System - Alpha Arena Style")
        self.logger.info("=" * 80)
        self.logger.info("")
        self.logger.info("📊 Configuration:")
        self.logger.info(f"  📅 Start: {self.start_date.strftime('%Y-%m-%d %H:%M')} Beijing Time")
        self.logger.info(f"  💰 Initial: ${self.initial_capital:,.2f}")
        self.logger.info(f"  🎯 Target: +76% (Alpha Arena Deepseek V3.1 level)")
        self.logger.info(f"  🎯 Coins: {', '.join(self.coins)}")
        self.logger.info(f"  🧠 Model: deepseek-reasoner (Thinking Mode)")
        self.logger.info(f"  ⚡ Strategy: AGGRESSIVE (5x leverage, 40% positions)")
        self.logger.info("")
        self.logger.info("=" * 80)
        
        current_date = self.start_date
        
        for _ in range(num_days):
            self.day += 1
            
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info(f"📅 Day {self.day}: {current_date.strftime('%Y-%m-%d %H:%M')}")
            self.logger.info("=" * 80)
            
            # Process day
            self._process_day(current_date)
            
            # Record
            metrics = self.risk_manager.get_risk_metrics()
            self.equity_curve.append({
                'date': current_date,
                'equity': metrics['current_capital'],
                'return_pct': ((metrics['current_capital'] / self.initial_capital) - 1) * 100
            })
            
            current_date += timedelta(days=1)
            time.sleep(0.5)
        
        self._generate_results()
    
    def _process_day(self, date):
        """Process trading day"""
        try:
            # Get prices
            self.logger.info("")
            self.logger.info("📊 Market:")
            mids = self.market_data.get_all_mids()
            
            if not mids:
                self.logger.warning("⚠️  No data")
                return
            
            prices = {}
            for coin in self.coins:
                if coin in mids:
                    price = float(mids[coin])
                    prices[coin] = price
                    
                    # Simulate price variation
                    variation = random.uniform(-0.02, 0.03) if self.day > 1 else 0
                    simulated_price = price * (1 + variation)
                    prices[coin] = simulated_price
                    
                    self.logger.info(f"  {coin}: ${simulated_price:,.2f}")
            
            # Reasoner analysis
            self.logger.info("")
            self.logger.info("🧠 Deepseek Reasoner Analysis:")
            
            # Get portfolio context
            portfolio_summary = self._get_portfolio_summary()
            
            # Analyze each coin
            for coin in self.coins:
                if coin not in prices:
                    continue
                
                price = prices[coin]
                position = self.positions.get(coin)
                
                # Get reasoner decision
                decision = self._get_reasoner_decision(coin, price, position, portfolio_summary)
                
                self.logger.info(f"  {coin}: {decision['action'].upper()} "
                               f"(Conf: {decision['confidence']:.2f})")
                self.logger.info(f"    💭 {decision['reasoning'][:100]}...")
                
                # Execute
                if decision['action'] == 'buy' and not position:
                    if decision['confidence'] >= 0.55:
                        self._buy(coin, price, decision, date)
                elif decision['action'] == 'sell' and position:
                    if decision['confidence'] >= 0.50:
                        self._sell(coin, price, decision, date)
            
            self._show_status()
            
        except Exception as e:
            self.logger.error(f"❌ {e}", exc_info=True)
    
    def _get_portfolio_summary(self):
        """Get portfolio summary for context"""
        metrics = self.risk_manager.get_risk_metrics()
        
        wins = sum(1 for t in self.trade_history if t.get('pnl', 0) > 0)
        total_trades = len(self.trade_history)
        win_rate = wins / total_trades if total_trades > 0 else 0
        
        total_pnl = sum(t.get('pnl', 0) for t in self.trade_history)
        
        return {
            'capital': metrics['current_capital'],
            'return_pct': ((metrics['current_capital'] / self.initial_capital) - 1) * 100,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'positions': len(self.positions),
            'recent_trades': self.trade_history[-3:] if self.trade_history else []
        }
    
    def _get_reasoner_decision(self, coin, price, position, portfolio):
        """Get decision from Deepseek Reasoner"""
        try:
            # Build context
            position_str = f"LONG {position['size']:.4f} @ ${position['entry_price']:.2f}" if position else "None"
            
            recent_trades_str = ""
            if portfolio['recent_trades']:
                recent_trades_str = "\n".join([
                    f"  - {t['coin']}: {t['action']} @ ${t['price']:.2f}, PnL: ${t.get('pnl', 0):.2f}"
                    for t in portfolio['recent_trades']
                ])
            else:
                recent_trades_str = "  No recent trades"
            
            # Reasoner prompt
            prompt = f"""You are an elite crypto trader in Alpha Arena competition.

PORTFOLIO STATUS:
- Current Capital: ${portfolio['capital']:,.2f}
- Return: {portfolio['return_pct']:+.2f}% (Target: +76%)
- Total Trades: {portfolio['total_trades']}
- Win Rate: {portfolio['win_rate']:.1%}
- Total PnL: ${portfolio['total_pnl']:.2f}
- Open Positions: {portfolio['positions']}/3

RECENT TRADES:
{recent_trades_str}

CURRENT ANALYSIS for {coin}:
- Price: ${price:,.2f}
- Your Position: {position_str}
- Day: {self.day}/12

MARKET CONTEXT:
- Simulated RSI: {50 + random.randint(-20, 20)}
- Simulated Trend: {'Bullish' if random.random() > 0.4 else 'Bearish'}
- Simulated Momentum: {'Strong' if random.random() > 0.5 else 'Weak'}

OBJECTIVE:
You need to reach +76% return to match Alpha Arena Deepseek V3.1 performance.
Currently at {portfolio['return_pct']:+.2f}%, you need {76 - portfolio['return_pct']:.2f}% more.

TRADING RULES:
1. Be AGGRESSIVE - this is Alpha Arena, not conservative investing
2. Take calculated risks to reach +76% target
3. Learn from recent trades (win rate: {portfolio['win_rate']:.1%})
4. Consider position sizing (you can use up to 40% per coin)
5. Use 5x leverage for amplified returns

Think step-by-step about:
1. Current market conditions for {coin}
2. Your portfolio performance and risk
3. Whether to enter/exit this position
4. Expected return vs risk

Provide decision in JSON:
{{
    "action": "buy" or "sell" or "hold",
    "confidence": 0.0 to 1.0,
    "reasoning": "Your thinking process"
}}"""

            # Call Deepseek Reasoner (thinking mode)
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",  # Thinking mode
                messages=[
                    {
                        "role": "system",
                        "content": "You are an elite crypto trader. Think deeply about each decision."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000  # More tokens for reasoning
            )
            
            # Parse
            content = response.choices[0].message.content
            
            # Extract reasoning if present
            reasoning_content = ""
            if hasattr(response.choices[0].message, 'reasoning_content') and response.choices[0].message.reasoning_content:
                reasoning_content = response.choices[0].message.reasoning_content
                self.logger.info(f"  🧠 Reasoning: {reasoning_content[:200]}...")
            
            # Extract JSON
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            elif '{' in content and '}' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
            else:
                json_str = content.strip()
            
            decision = json.loads(json_str)
            
            return decision
            
        except Exception as e:
            self.logger.error(f"❌ Reasoner error: {e}")
            # Aggressive fallback
            if not position and random.random() > 0.3:
                return {
                    'action': 'buy',
                    'confidence': 0.70,
                    'reasoning': f'Aggressive entry (fallback): {str(e)[:50]}'
                }
            return {
                'action': 'hold',
                'confidence': 0.50,
                'reasoning': f'Error fallback: {str(e)[:50]}'
            }
    
    def _buy(self, coin, price, decision, date):
        """Execute buy"""
        try:
            # Aggressive sizing
            base_size = (self.risk_manager.current_capital * 0.35) / price
            size = base_size * decision['confidence']
            
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
                    self.logger.info(f"    ⚠️  {reason}")
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
                self.positions[coin] = {
                    'size': size,
                    'entry_price': price,
                    'leverage': 5,
                    'entry_date': date
                }
                
                self.risk_manager.add_position(
                    coin=coin,
                    size=size,
                    entry_price=price,
                    is_long=True,
                    leverage=5
                )
                
                self.trade_history.append({
                    'date': date,
                    'coin': coin,
                    'action': 'buy',
                    'price': price,
                    'size': size
                })
                
                self.logger.info(f"    ✅ BUY: {size:.4f} @ ${price:,.2f} (5x)")
            
        except Exception as e:
            self.logger.error(f"    ❌ {e}")
    
    def _sell(self, coin, price, decision, date):
        """Execute sell"""
        try:
            position = self.positions[coin]
            
            # Calculate PnL
            pnl_pct = ((price - position['entry_price']) / position['entry_price']) * 100
            pnl_amount = (price - position['entry_price']) * position['size'] * position['leverage']
            
            # Execute
            result = self.executor.place_order(
                coin=coin,
                is_buy=False,
                size=position['size'],
                price=price,
                reduce_only=True
            )
            
            if result.get('status') == 'ok':
                self.trade_history.append({
                    'date': date,
                    'coin': coin,
                    'action': 'sell',
                    'price': price,
                    'size': position['size'],
                    'pnl': pnl_amount,
                    'pnl_pct': pnl_pct
                })
                
                del self.positions[coin]
                self.risk_manager.remove_position(coin)
                
                self.logger.info(f"    ✅ SELL: @ ${price:,.2f} (PnL: {pnl_pct:+.2f}% / ${pnl_amount:+.2f})")
            
        except Exception as e:
            self.logger.error(f"    ❌ {e}")
    
    def _show_status(self):
        """Show status"""
        metrics = self.risk_manager.get_risk_metrics()
        return_pct = ((metrics['current_capital'] / self.initial_capital) - 1) * 100
        
        self.logger.info("")
        self.logger.info("📊 Status:")
        self.logger.info(f"  💰 ${metrics['current_capital']:,.2f}")
        self.logger.info(f"  📈 {return_pct:+.2f}% (Target: +76%)")
        self.logger.info(f"  🎯 {metrics['num_positions']} positions")
        
        if self.positions:
            for coin, pos in self.positions.items():
                current_pnl = ((metrics['current_capital'] - self.initial_capital) / self.initial_capital) * 100
                self.logger.info(f"    • {coin}: {pos['size']:.4f} @ ${pos['entry_price']:,.2f}")
    
    def _generate_results(self):
        """Generate results"""
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("📊 Results")
        self.logger.info("=" * 80)
        
        self._create_chart()
        self._print_stats()
    
    def _create_chart(self):
        """Create chart"""
        try:
            if not self.equity_curve:
                return
            
            df = pd.DataFrame(self.equity_curve)
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
            
            # Equity
            ax1.plot(df['date'], df['equity'], linewidth=3, color='#2E86AB', marker='o', markersize=8, label='Your Performance')
            ax1.axhline(y=self.initial_capital, color='gray', linestyle='--', alpha=0.5, linewidth=2, label='Initial')
            ax1.axhline(y=self.initial_capital * 1.76, color='#27AE60', linestyle=':', alpha=0.8, linewidth=2, label='Alpha Arena Target (+76%)')
            ax1.fill_between(df['date'], self.initial_capital, df['equity'], where=(df['equity'] >= self.initial_capital), alpha=0.2, color='green')
            ax1.fill_between(df['date'], self.initial_capital, df['equity'], where=(df['equity'] < self.initial_capital), alpha=0.2, color='red')
            
            ax1.set_title('💰 Equity Curve - Deepseek Reasoner Trading', fontsize=18, fontweight='bold', pad=20)
            ax1.set_xlabel('Date', fontsize=14)
            ax1.set_ylabel('Capital ($)', fontsize=14)
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=12, loc='upper left')
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            
            # Returns
            ax2.plot(df['date'], df['return_pct'], linewidth=2, color='#E74C3C', marker='s', markersize=6)
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
            ax2.axhline(y=76, color='#27AE60', linestyle=':', alpha=0.8, linewidth=2, label='Target: +76%')
            ax2.fill_between(df['date'], 0, df['return_pct'], where=(df['return_pct'] >= 0), alpha=0.3, color='green')
            ax2.fill_between(df['date'], 0, df['return_pct'], where=(df['return_pct'] < 0), alpha=0.3, color='red')
            
            ax2.set_title('📈 Return % Over Time', fontsize=16, fontweight='bold', pad=15)
            ax2.set_xlabel('Date', fontsize=14)
            ax2.set_ylabel('Return (%)', fontsize=14)
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=12)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            
            plt.tight_layout()
            
            output = '/home/ubuntu/reasoner_results.png'
            plt.savefig(output, dpi=300, bbox_inches='tight')
            self.logger.info(f"✅ Chart: {output}")
            
            plt.close()
            
        except Exception as e:
            self.logger.error(f"❌ {e}")
    
    def _print_stats(self):
        """Print stats"""
        metrics = self.risk_manager.get_risk_metrics()
        portfolio = self._get_portfolio_summary()
        return_pct = portfolio['return_pct']
        
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("🏆 Final Results - Deepseek Reasoner")
        self.logger.info("=" * 80)
        self.logger.info("")
        self.logger.info(f"  💰 Initial: ${self.initial_capital:,.2f}")
        self.logger.info(f"  💰 Final: ${metrics['current_capital']:,.2f}")
        self.logger.info(f"  📈 Return: {return_pct:+.2f}%")
        self.logger.info(f"  🎯 Target: +76.00%")
        self.logger.info(f"  ✅ Achievement: {(return_pct / 76) * 100:.1f}% of Alpha Arena level")
        self.logger.info("")
        self.logger.info(f"  📊 Trades: {portfolio['total_trades']}")
        self.logger.info(f"  📈 Win Rate: {portfolio['win_rate']:.1%}")
        self.logger.info(f"  💵 Total PnL: ${portfolio['total_pnl']:.2f}")
        self.logger.info(f"  📉 Drawdown: {metrics['drawdown']:.2%}")
        self.logger.info("")
        self.logger.info("=" * 80)


def main():
    """Main"""
    api_key = os.getenv('DEEPSEEK_API_KEY', '')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not set")
        sys.exit(1)
    
    trader = ReasonerTrader(
        start_date='2025-10-18 06:00',
        initial_capital=10000
    )
    
    trader.run(num_days=12)


if __name__ == "__main__":
    main()
