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
from typing import Dict, Any, Optional, List
from openai import OpenAI

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "hyperliquid_trading_bot"))

from src.data.market_data import MarketDataCollector
from src.risk.risk_manager import RiskManager
from src.trading.executor import TradeExecutor
from src.utils.logger import get_logger
from src.utils.config_loader import get_config


class LiveTradingSystem:
    """7-day continuous live trading system"""
    
    def __init__(self, initial_capital=10000):
        """Initialize live trading system"""
        self.logger = get_logger()
        self.config = get_config()
        self.initial_capital = initial_capital
        self.start_time = datetime.now()
        self.invocation_count = 0
        self.ai_memory: List[Dict[str, Any]] = []
        
        # Market data
        hyper_config = self.config.get_section('hyperliquid')
        self.market_data = MarketDataCollector(hyper_config)
        
        # Risk manager - Aggressive settings
        risk_config = dict(self.config.get_section('risk') or {})
        risk_config.setdefault('max_position_per_coin', 0.40)
        risk_config.setdefault('max_total_position', 1.0)
        risk_config.setdefault('default_leverage', 5)
        risk_config.setdefault('stop_loss_pct', 0.10)
        risk_config.setdefault('take_profit_pct', 0.20)
        risk_config.setdefault('max_drawdown', 0.35)
        risk_config.setdefault('max_daily_loss', 0.20)
        # Unlimited leverage
        risk_config['max_leverage'] = 0
        self.risk_manager = RiskManager(risk_config)
        
        # Executor
        self.executor = TradeExecutor(config=hyper_config, paper_trading=True)
        
        # Deepseek Reasoner
        api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # AI dialog log file
        self.ai_dialog_log_path = Path(__file__).parent / "logs" / "ai_dialogs.log"
        self.ai_dialog_log_path.parent.mkdir(parents=True, exist_ok=True)
        # Equity history log file
        self.equity_log_path = Path(__file__).parent / "logs" / "equity_history.csv"
        if not self.equity_log_path.exists():
            header = "timestamp,capital,drawdown,num_positions,total_position_value\n"
            self.equity_log_path.write_text(header, encoding="utf-8")
        
        # Initialize capital
        self.risk_manager.initialize_capital(initial_capital)
        
        # Trading state
        trading_pairs = self.config.get('trading.trading_pairs', [])
        default_pairs = [
            "BTC", "ETH", "SOL", "DOGE", "XRP",
            "ADA", "AVAX", "LINK", "MATIC", "DOT"
        ]
        self.coins = trading_pairs or default_pairs
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
        self.logger.info(f"  Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"  End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"  💰 Initial Capital: ${self.initial_capital:,.2f}")
        self.logger.info(f"  🎯 Trading Pairs: {', '.join(self.coins)}")
        self.logger.info(f"  🧠 Model: deepseek-chat")
        self.logger.info(f"  ⚡ Strategy: AGGRESSIVE (no leverage cap, 40% positions)")
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
        """Execute one trading cycle."""
        try:
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info(f"TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info("=" * 80)

            # Fetch latest prices
            self.logger.info("")
            self.logger.info("Market Prices:")
            mids = self.market_data.get_all_mids()
            if not mids:
                self.logger.warning("No market data available")
                return

            prices: Dict[str, float] = {}
            for coin in self.coins:
                if coin in mids:
                    price = float(mids[coin])
                    prices[coin] = price
                    self.logger.info(f"  {coin}: ${price:,.2f}")

            # Run AI decision loop
            self.logger.info("")
            self.logger.info("AI Analysis & Trading Decisions:")

            decisions = self._get_ai_decisions(prices)

            for coin in self.coins:
                price = prices.get(coin)
                if price is None:
                    continue

                position = self.positions.get(coin)
                decision = decisions.get(coin.upper(), {
                    "action": "hold",
                    "confidence": 0.0,
                    "leverage": 1,
                    "reasoning": "No decision returned"
                })

                action = str(decision.get('action', '')).lower()
                try:
                    confidence = float(decision.get('confidence', 0) or 0.0)
                except (TypeError, ValueError):
                    confidence = 0.0
                self.logger.info(f"  {coin}: {action.upper()} (confidence {confidence:.2f})")

                if action == 'buy':
                    if position:
                        if not position.get('is_long', True):
                            if confidence >= 0.50:
                                self._close_short(coin, price, decision)
                            else:
                                self.logger.info(f"    Hold short {coin} (confidence below threshold)")
                        else:
                            self.logger.info(f"    Already long {coin}, skipping additional buy")
                    else:
                        if confidence >= 0.55:
                            self._execute_buy(coin, price, decision)
                        else:
                            self.logger.info(f"    Skip opening long {coin} (confidence below threshold)")
                elif action == 'sell':
                    if position:
                        if position.get('is_long', True):
                            if confidence >= 0.50:
                                self._execute_sell(coin, price, decision)
                            else:
                                self.logger.info(f"    Hold long {coin} (confidence below threshold)")
                        else:
                            self.logger.info(f"    Already short {coin}, skipping additional sell")
                    else:
                        if confidence >= 0.55:
                            self._execute_short(coin, price, decision)
                        else:
                            self.logger.info(f"    Skip opening short {coin} (confidence below threshold)")
                else:
                    self.logger.info(f"    HOLD {coin}")

            self.logger.info("")
            self.logger.info("=" * 80)

        except Exception as exc:
            self.logger.error(f"Trading cycle error: {exc}", exc_info=True)

    def _format_positions_summary(self, prices: Dict[str, float]) -> str:
        """Create a concise portfolio status string for AI prompts."""
        if not self.positions:
            return "No open positions. All capital is available."

        lines = []
        for coin, pos in self.positions.items():
            is_long = pos.get('is_long', True)
            direction = "LONG" if is_long else "SHORT"
            size = pos.get('size', 0.0)
            entry_price = pos.get('entry_price', 0.0)
            leverage = pos.get('leverage', 1)
            current_price = prices.get(coin)

            if current_price and entry_price:
                if is_long:
                    change_pct = ((current_price - entry_price) / entry_price) * 100
                else:
                    change_pct = ((entry_price - current_price) / entry_price) * 100
                lines.append(
                    f"{coin}: {direction} {size:.4f} @ ${entry_price:,.2f} | "
                    f"current ${current_price:,.2f} | PnL {change_pct:+.2f}% | {leverage}x"
                )
            else:
                lines.append(
                    f"{coin}: {direction} {size:.4f} @ ${entry_price:,.2f} | current price unavailable | {leverage}x"
                )

        return "\n".join(lines)

    def _format_market_overview(self, prices: Dict[str, float]) -> str:
        """Create top-level market state summary."""
        if not prices:
            return "No market data available."
        lines = ["Symbol | Price"]
        for coin in sorted(prices.keys()):
            lines.append(f"{coin}: ${prices[coin]:,.4f}")
        return "\n".join(lines)

    def _format_position_details(self, prices: Dict[str, float]) -> str:
        """Expand on each position for the template."""
        if not self.positions:
            return "No open positions."

        details = []
        for coin, pos in self.positions.items():
            current_price = prices.get(coin, pos.get('entry_price', 0.0))
            entry_price = pos.get('entry_price', 0.0)
            size = pos.get('size', 0.0)
            leverage = pos.get('leverage', 1)
            is_long = pos.get('is_long', True)
            direction = "LONG" if is_long else "SHORT"

            if is_long:
                pnl = (current_price - entry_price) * size * leverage
                pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price else 0
            else:
                pnl = (entry_price - current_price) * size * leverage
                pnl_pct = ((entry_price - current_price) / entry_price * 100) if entry_price else 0

            details.append(
                f"{coin}: {direction} size={size:.6f}, entry=${entry_price:,.4f}, "
                f"current=${current_price:,.4f}, leverage={leverage}x, "
                f"unrealized_pnl=${pnl:+,.2f} ({pnl_pct:+.2f}%)"
            )
        return "\n".join(details)

    def _format_ai_memory(self, max_entries: int = 5) -> str:
        """Return a short summary of previous AI responses."""
        if not self.ai_memory:
            return "No prior AI responses recorded."

        recent = self.ai_memory[-max_entries:]
        lines = []
        for entry in recent:
            timestamp = entry.get("timestamp", "unknown")
            if "decisions" in entry:
                decisions = entry.get("decisions", {})
                if decisions:
                    for coin, decision in decisions.items():
                        action = decision.get("action", "n/a")
                        confidence = decision.get("confidence", 0)
                        reasoning = decision.get("reasoning", "")
                        lines.append(
                            f"{timestamp} | {coin} -> action={action} confidence={float(confidence):.2f} | notes={reasoning[:80]}"
                        )
                else:
                    lines.append(f"{timestamp} | No decisions returned")
            else:
                decision = entry.get("decision", {})
                coin = entry.get("coin", "UNKNOWN")
                lines.append(
                    f"{timestamp} | {coin} -> action={decision.get('action', 'n/a')} "
                    f"confidence={float(decision.get('confidence', 0)):.2f} | notes={decision.get('reasoning', '')[:80]}"
                )
        return "\n".join(lines)

    def _get_recent_candles(self, coin, minutes=5):
        """Fetch last N minutes of 1m candles for the given coin"""
        try:
            end_time_ms = int(time.time() * 1000)
            start_time_ms = end_time_ms - minutes * 60 * 1000
            df = self.market_data.get_candles(
                coin=coin,
                interval="1m",
                start_time=start_time_ms,
                end_time=end_time_ms
            )
            if df.empty:
                return []
            
            recent = df.tail(minutes).reset_index()
            records = []
            for _, row in recent.iterrows():
                timestamp = row['timestamp']
                records.append({
                    "time": timestamp.strftime("%Y-%m-%d %H:%M"),
                    "open": round(float(row['open']), 6),
                    "high": round(float(row['high']), 6),
                    "low": round(float(row['low']), 6),
                    "close": round(float(row['close']), 6),
                    "volume": round(float(row['volume']), 2),
                })
            return records
        except Exception as exc:
            self.logger.error(f"Failed to fetch recent candles for {coin}: {exc}")
            return []

    def _log_ai_dialog(self, coin: str, prompt: str, response_text: str) -> None:
        """Persist each AI prompt/response pair to a dedicated log file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "coin": coin,
            "prompt": prompt,
            "response": response_text,
        }
        try:
            entry_str = json.dumps(entry, ensure_ascii=False)
            with open(self.ai_dialog_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(entry_str + "\n")

            # Mirror summary into main trading log for quick visibility
            self.logger.info(
                "AI Dialog Logged | %s | action prompt length=%d, response length=%d",
                coin,
                len(prompt),
                len(response_text),
            )
            self.logger.debug("AI Prompt: %s", prompt)
            self.logger.debug("AI Response: %s", response_text)
        except Exception as exc:
            self.logger.error(f"Failed to write AI dialog log: {exc}")

    def _record_equity_snapshot(self, metrics: Dict[str, Any]) -> None:
        """Append a capital snapshot to CSV for charting."""
        try:
            with open(self.equity_log_path, "a", encoding="utf-8") as fp:
                fp.write(
                    f"{datetime.now().isoformat()},"
                    f"{metrics.get('current_capital', 0)},"
                    f"{metrics.get('drawdown', 0)},"
                    f"{metrics.get('num_positions', 0)},"
                    f"{metrics.get('total_position_value', 0)}\n"
                )
        except Exception as exc:
            self.logger.error(f"Failed to persist equity snapshot: {exc}")


    def _get_ai_decisions(self, prices: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Get AI trading decisions for all tracked coins via a single DeepSeek prompt."""
        try:
            self.invocation_count += 1
            now = datetime.now()
            runtime_minutes = int((now - self.start_time).total_seconds() // 60)

            metrics = self.risk_manager.get_risk_metrics()
            return_pct = ((metrics['current_capital'] / self.initial_capital) - 1) * 100
            total_markets = len(self.coins)
            available_cash = metrics['current_capital'] - metrics.get('total_position_value', 0)

            market_overview = self._format_market_overview(prices)
            position_details = self._format_position_details(prices)
            prior_ai_context = self._format_ai_memory()

            coin_sections = []
            for coin in self.coins:
                price = prices.get(coin)
                if price is None:
                    continue

                position = self.positions.get(coin)
                if position:
                    is_long = position.get('is_long', True)
                    direction = "LONG" if is_long else "SHORT"
                    position_str = (
                        f"{direction} {position['size']:.4f} @ ${position['entry_price']:.2f} "
                        f"(leverage {position.get('leverage', 1)}x)"
                    )
                else:
                    position_str = "No position"

                recent_candles = self._get_recent_candles(coin, minutes=5)
                candles_text = json.dumps(recent_candles, indent=2) if recent_candles else "No recent candle data available in the last 5 minutes."

                coin_sections.append(
                    (
                        f"{coin} DATA:\n"
                        f"- current_price = {price}\n"
                        f"- current_position = {position_str}\n"
                        f"- recent_candles (1m, oldest → newest):\n{candles_text}"
                    )
                )

            if not coin_sections:
                return {}

            coin_details_text = "\n\n".join(coin_sections)

            prompt = (
                f"It has been {runtime_minutes} minutes since you started trading. "
                f"The current time is {now.strftime('%Y-%m-%d %H:%M:%S')} and you've been invoked {self.invocation_count} times. "
                "Below is a consolidated snapshot of market state, signals, and portfolio context.\n\n"
                "CURRENT MARKET STATE FOR ALL COINS\n"
                f"{market_overview}\n\n"
                "ALL COIN DETAILS\n"
                f"{coin_details_text}\n\n"
                "CURRENT ACCOUNT INFORMATION & PERFORMANCE\n"
                f"Current Total Return (percent): {return_pct:+.2f}%\n"
                f"Available Cash: {available_cash:,.2f}\n"
                f"Current Account Value: {metrics['current_capital']:,.2f}\n"
                f"Active Positions ({metrics['num_positions']} of {total_markets} tracked):\n"
                f"{position_details}\n\n"
                "PREVIOUS AI RESPONSES\n"
                f"{prior_ai_context}\n\n"
                "TASK\n"
                "Considering all information above, recommend an action for each coin. "
                "You may open or close long/short exposure with any leverage (no upper limit). "
                "Only recommend trades when confidence is sufficient; otherwise respond with hold.\n\n"
                "Respond strictly in JSON with coin symbols as keys, for example:\n"
                "{\n"
                '  \"BTC\": {\"action\": \"...\", \"confidence\": 0.0-1.0, \"leverage\": integer>=1, \"reasoning\": \"...\", \"notes\": \"...\"},\n'
                '  \"ETH\": {...}\n'
                "}\n"
            )
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an elite crypto trader with awareness of prior guidance."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=1.0
            )

            content = response.choices[0].message.content
            self._log_ai_dialog("ALL", prompt, content)

            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '{' in content and '}' in content:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                json_str = content[start_idx:end_idx]
            else:
                json_str = content.strip()

            parsed = json.loads(json_str)
            decisions: Dict[str, Dict[str, Any]] = {}
            if isinstance(parsed, dict):
                for coin, decision in parsed.items():
                    if isinstance(decision, dict):
                        decision.setdefault('leverage', 1)
                        decisions[coin.upper()] = decision

            self.ai_memory.append({
                "timestamp": now.strftime('%Y-%m-%d %H:%M:%S'),
                "decisions": decisions,
                "raw_response": content
            })
            if len(self.ai_memory) > 20:
                self.ai_memory = self.ai_memory[-20:]

            return decisions

        except Exception as e:
            self.logger.error(f"AI decision error: {e}")
            return {}
    def _execute_buy(self, coin, price, decision):
        """Execute buy order with detailed reporting"""
        try:
            # Calculate position size
            metrics = self.risk_manager.get_risk_metrics()
            available_capital = metrics['current_capital']
            
            # Aggressive sizing
            target_value = available_capital * 0.35 * decision['confidence']
            size = target_value / price

            # Determine leverage (no upper cap)
            leverage_value = decision.get('leverage') or self.risk_manager.default_leverage or 1
            try:
                leverage_value = int(float(leverage_value))
            except (ValueError, TypeError):
                leverage_value = int(self.risk_manager.default_leverage or 1)
            leverage_value = max(leverage_value, 1)
            
            # Validate
            is_valid, reason = self.risk_manager.validate_trade(
                coin=coin,
                size=size,
                price=price,
                leverage=leverage_value
            )
            
            if not is_valid:
                # Try smaller size
                size = size * 0.7
                is_valid, reason = self.risk_manager.validate_trade(
                    coin=coin,
                    size=size,
                    price=price,
                    leverage=leverage_value
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
                leverage=leverage_value
            )
            
            if result.get('status') == 'ok':
                # Calculate position value
                position_value = size * price
                leveraged_value = position_value * leverage_value
                
                # Update positions
                self.positions[coin] = {
                    'size': size,
                    'entry_price': price,
                    'leverage': leverage_value,
                    'entry_time': datetime.now(),
                    'entry_value': position_value,
                    'is_long': True
                }
                
                self.risk_manager.add_position(
                    coin=coin,
                    size=size,
                    entry_price=price,
                    is_long=True,
                    leverage=leverage_value
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
                self.logger.info(f"  ⚡ Leverage: {leverage_value}x")
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

    def _execute_short(self, coin, price, decision):
        """Open a short position."""
        try:
            metrics = self.risk_manager.get_risk_metrics()
            available_capital = metrics['current_capital']

            target_value = available_capital * 0.35 * decision.get('confidence', 0)
            size = target_value / price if price else 0

            leverage_value = decision.get('leverage') or self.risk_manager.default_leverage or 1
            try:
                leverage_value = int(float(leverage_value))
            except (ValueError, TypeError):
                leverage_value = int(self.risk_manager.default_leverage or 1)
            leverage_value = max(leverage_value, 1)

            is_valid, reason = self.risk_manager.validate_trade(
                coin=coin,
                size=size,
                price=price,
                leverage=leverage_value
            )

            if not is_valid:
                size *= 0.7
                is_valid, reason = self.risk_manager.validate_trade(
                    coin=coin,
                    size=size,
                    price=price,
                    leverage=leverage_value
                )
                if not is_valid:
                    self.logger.warning(f"    Cannot short {coin}: {reason}")
                    return

            result = self.executor.place_order(
                coin=coin,
                is_buy=False,
                size=size,
                price=price,
                leverage=leverage_value
            )

            if result.get('status') == 'ok':
                position_value = size * price
                leveraged_value = position_value * leverage_value

                self.positions[coin] = {
                    'size': size,
                    'entry_price': price,
                    'leverage': leverage_value,
                    'entry_time': datetime.now(),
                    'entry_value': position_value,
                    'is_long': False
                }

                self.risk_manager.add_position(
                    coin=coin,
                    size=size,
                    entry_price=price,
                    is_long=False,
                    leverage=leverage_value
                )

                self.trade_history.append({
                    'time': datetime.now(),
                    'coin': coin,
                    'action': 'short',
                    'price': price,
                    'size': size,
                    'value': position_value
                })

                self.logger.info("")
                self.logger.info("  " + "=" * 76)
                self.logger.info(f"  SHORT POSITION OPENED - {coin}")
                self.logger.info("  " + "=" * 76)
                self.logger.info(f"  Coin: {coin}")
                self.logger.info(f"  Entry Price: ${price:,.2f}")
                self.logger.info(f"  Size: {size:.6f} {coin}")
                self.logger.info(f"  Position Notional: ${position_value:,.2f}")
                self.logger.info(f"  Leverage: {leverage_value}x")
                self.logger.info(f"  Leveraged Exposure: ${leveraged_value:,.2f}")
                self.logger.info(f"  Confidence: {decision.get('confidence', 0):.2%}")
                self.logger.info(f"  Reasoning: {decision.get('reasoning', '')[:60]}...")
                self.logger.info(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as exc:
            self.logger.error(f"    Short execution error: {exc}", exc_info=True)
    
    def _execute_sell(self, coin, price, decision):
        """Execute sell order with detailed reporting"""
        try:
            if coin not in self.positions:
                return
            
            position = self.positions[coin]
            if not position.get('is_long', True):
                self.logger.info(f"    Existing position on {coin} is short; sell ignored.")
                return
            
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
                reduce_only=True,
                leverage=leverage
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

    def _close_short(self, coin, price, decision):
        """Close an open short position."""
        try:
            position = self.positions.get(coin)
            if not position or position.get('is_long', True):
                return

            entry_price = position['entry_price']
            size = position['size']
            leverage = position['leverage']

            price_change = entry_price - price
            price_change_pct = (price_change / entry_price) * 100 if entry_price else 0
            pnl_amount = price_change * size * leverage
            pnl_pct = price_change_pct * leverage

            result = self.executor.place_order(
                coin=coin,
                is_buy=True,
                size=size,
                price=price,
                reduce_only=True,
                leverage=leverage
            )

            if result.get('status') == 'ok':
                self.trade_history.append({
                    'time': datetime.now(),
                    'coin': coin,
                    'action': 'cover',
                    'price': price,
                    'size': size,
                    'pnl': pnl_amount,
                    'pnl_pct': pnl_pct
                })

                self.logger.info("")
                self.logger.info("  " + "=" * 76)
                label = "SHORT COVERED - PROFIT" if pnl_amount >= 0 else "SHORT COVERED - LOSS"
                self.logger.info(f"  {label} - {coin}")
                self.logger.info("  " + "=" * 76)
                self.logger.info(f"  Coin: {coin}")
                self.logger.info(f"  Entry Price: ${entry_price:,.2f}")
                self.logger.info(f"  Exit Price: ${price:,.2f}")
                self.logger.info(f"  Size: {size:.6f} {coin}")
                self.logger.info(f"  Leverage: {leverage}x")
                self.logger.info(f"  P&L Amount: ${pnl_amount:+,.2f}")
                self.logger.info(f"  P&L Percentage: {pnl_pct:+.2f}%")
                self.logger.info(f"  Holding Time: {datetime.now() - position['entry_time']}")
                self.logger.info(f"  Reasoning: {decision.get('reasoning', '')[:60]}...")
                self.logger.info(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                del self.positions[coin]
                self.risk_manager.remove_position(coin)

                new_metrics = self.risk_manager.get_risk_metrics()
                new_return = ((new_metrics['current_capital'] / self.initial_capital) - 1) * 100
                self.logger.info("")
                self.logger.info(f"  Capital After Trade: ${new_metrics['current_capital']:,.2f}")
                self.logger.info(f"  Total Return: {new_return:+.2f}%")
                self.logger.info(f"  Remaining Positions: {new_metrics['num_positions']}")
                self.logger.info("  " + "=" * 76)
                self.logger.info("")

        except Exception as exc:
            self.logger.error(f"    Short cover error: {exc}", exc_info=True)
    
    def _hourly_report(self):
        """Generate hourly status report"""
        try:
            metrics = self.risk_manager.get_risk_metrics()
            # Persist metrics for visualization before formatting output
            self._record_equity_snapshot(metrics)
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
                    is_long = pos.get('is_long', True)
                    if is_long:
                        unrealized_pnl = (current_price - pos['entry_price']) * pos['size'] * pos['leverage']
                        unrealized_pnl_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100 * pos['leverage']
                    else:
                        unrealized_pnl = (pos['entry_price'] - current_price) * pos['size'] * pos['leverage']
                        unrealized_pnl_pct = ((pos['entry_price'] - current_price) / pos['entry_price']) * 100 * pos['leverage']
                    
                    total_position_value += position_value
                    
                    pnl_emoji = "📈" if unrealized_pnl >= 0 else "📉"
                    
                    self.logger.info(f"║  {pnl_emoji} {coin}" + " " * 71 + "║")
                    direction = "LONG" if is_long else "SHORT"
                    self.logger.info(f"║    {direction} Size: {pos['size']:.6f} {coin}" + " " * (57 - len(direction) - len(coin)) + "║")
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
            completed_trades = [
                t for t in self.trade_history
                if t.get('action') in ('sell', 'cover')
            ]
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
            for coin, pos in list(self.positions.items()):
                price = float(mids.get(coin, pos['entry_price']))
                decision = {'confidence': 1.0, 'reasoning': 'Final position close'}
                if pos.get('is_long', True):
                    self._execute_sell(coin, price, decision)
                else:
                    self._close_short(coin, price, decision)
        
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
