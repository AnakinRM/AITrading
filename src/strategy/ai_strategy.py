"""
AI-powered trading strategy
"""
from typing import Dict, Optional, Any
import pandas as pd

from ..utils.logger import get_logger
from ..data.market_data import MarketDataCollector
from ..data.indicators import TechnicalIndicators
from ..ai.deepseek_agent import DeepseekAgent
from ..risk.risk_manager import RiskManager


class AITradingStrategy:
    """AI-powered trading strategy using Deepseek"""
    
    def __init__(
        self,
        market_data: MarketDataCollector,
        indicators: TechnicalIndicators,
        ai_agent: DeepseekAgent,
        risk_manager: RiskManager,
        config: dict = None
    ):
        """
        Initialize AI trading strategy
        
        Args:
            market_data: Market data collector
            indicators: Technical indicators calculator
            ai_agent: Deepseek AI agent
            risk_manager: Risk manager
            config: Strategy configuration
        """
        self.logger = get_logger()
        self.market_data = market_data
        self.indicators = indicators
        self.ai_agent = ai_agent
        self.risk_manager = risk_manager
        self.config = config or {}
        
        self.logger.info("AITradingStrategy initialized")
    
    def analyze_and_decide(
        self,
        coin: str,
        current_position: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze market and make trading decision
        
        Args:
            coin: Coin symbol
            current_position: Current position if any
        
        Returns:
            Trading decision
        """
        try:
            # Get current market data
            mids = self.market_data.get_all_mids()
            current_price = mids.get(coin, 0)
            
            if current_price == 0:
                self.logger.warning(f"No price data for {coin}")
                return {'action': 'hold', 'reason': 'No price data'}
            
            # Get historical candles
            candles = self.market_data.get_candles(coin, interval='1h')
            
            if candles.empty:
                self.logger.warning(f"No candle data for {coin}")
                return {'action': 'hold', 'reason': 'No candle data'}
            
            # Calculate technical indicators
            candles_with_indicators = self.indicators.calculate_all_indicators(
                candles,
                config=self.config.get('indicators', {})
            )
            
            # Get market summary
            market_summary = self.indicators.get_market_summary(candles_with_indicators)
            
            # Get AI decision
            ai_decision = self.ai_agent.analyze_market(
                coin=coin,
                market_data={'price': current_price, 'volume': market_summary.get('volume', 0)},
                technical_indicators=market_summary,
                current_position=current_position
            )
            
            # Process decision
            decision = self._process_ai_decision(
                coin, current_price, ai_decision, current_position
            )
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error in analyze_and_decide for {coin}: {e}")
            return {'action': 'hold', 'reason': f'Error: {str(e)}'}
    
    def _process_ai_decision(
        self,
        coin: str,
        current_price: float,
        ai_decision: Dict[str, Any],
        current_position: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process AI decision and apply risk management
        
        Args:
            coin: Coin symbol
            current_price: Current price
            ai_decision: AI decision
            current_position: Current position
        
        Returns:
            Processed trading decision
        """
        action = ai_decision.get('action', 'hold')
        confidence = ai_decision.get('confidence', 0)
        leverage = ai_decision.get('leverage', 3)
        reasoning = ai_decision.get('reasoning', '')
        
        # Minimum confidence threshold
        min_confidence = 0.6
        if confidence < min_confidence and action != 'hold':
            self.logger.info(
                f"Confidence {confidence:.2f} below threshold {min_confidence:.2f}, "
                f"changing action to HOLD"
            )
            return {
                'action': 'hold',
                'reason': f'Low confidence ({confidence:.2f})',
                'ai_reasoning': reasoning
            }
        
        # If we have a position, check if we should close it
        if current_position:
            # Check stop loss / take profit
            risk_action = self.risk_manager.update_position(coin, current_price)
            if risk_action:
                return {
                    'action': 'close',
                    'reason': risk_action,
                    'ai_reasoning': reasoning
                }
            
            # If AI says opposite direction, close position
            is_long = current_position.get('is_long', True)
            if (is_long and action == 'sell') or (not is_long and action == 'buy'):
                return {
                    'action': 'close',
                    'reason': 'AI signal reversal',
                    'ai_reasoning': reasoning
                }
        
        # If action is buy or sell, calculate position size
        if action in ['buy', 'sell']:
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                coin=coin,
                entry_price=current_price,
                confidence=confidence,
                volatility=0.02  # TODO: Calculate actual volatility
            )
            
            # Validate trade
            is_valid, reason = self.risk_manager.validate_trade(
                coin=coin,
                size=position_size,
                price=current_price,
                leverage=leverage
            )
            
            if not is_valid:
                self.logger.warning(f"Trade validation failed: {reason}")
                return {
                    'action': 'hold',
                    'reason': f'Risk check failed: {reason}',
                    'ai_reasoning': reasoning
                }
            
            # Calculate stop loss and take profit
            is_long = (action == 'buy')
            stop_loss = self.risk_manager.calculate_stop_loss(current_price, is_long)
            take_profit = self.risk_manager.calculate_take_profit(current_price, is_long)
            
            return {
                'action': action,
                'coin': coin,
                'size': position_size,
                'entry_price': current_price,
                'leverage': leverage,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'reason': 'AI signal with risk validation',
                'ai_reasoning': reasoning
            }
        
        # Default to hold
        return {
            'action': 'hold',
            'reason': 'No clear signal',
            'ai_reasoning': reasoning
        }
    
    def backtest(
        self,
        coin: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 10000
    ) -> Dict[str, Any]:
        """
        Backtest strategy on historical data
        
        Args:
            coin: Coin symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            initial_capital: Initial capital
        
        Returns:
            Backtest results
        """
        self.logger.info(f"Starting backtest for {coin} from {start_date} to {end_date}")
        
        # TODO: Implement backtesting logic
        # 1. Load historical data
        # 2. Iterate through time periods
        # 3. Generate signals
        # 4. Simulate trades
        # 5. Calculate performance metrics
        
        return {
            'total_return': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'win_rate': 0,
            'num_trades': 0
        }
