"""
Deepseek AI Agent for trading decisions
"""
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI

from ..utils.logger import get_logger
from ..utils.config_loader import get_config


class DeepseekAgent:
    """AI agent powered by Deepseek for trading analysis and decisions"""
    
    def __init__(self, config: dict = None):
        """
        Initialize Deepseek agent
        
        Args:
            config: Deepseek configuration dictionary
        """
        self.logger = get_logger()
        
        if config is None:
            config_loader = get_config()
            config = config_loader.get_section('deepseek')
        
        self.api_key = config.get('api_key')
        self.api_url = config.get('api_url', 'https://api.deepseek.com')
        self.model = config.get('model', 'deepseek-chat')
        self.max_tokens = config.get('max_tokens', 2000)
        self.temperature = config.get('temperature', 0.7)
        
        # Initialize OpenAI client (Deepseek is OpenAI-compatible)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url
        )
        
        self.logger.info(f"DeepseekAgent initialized with model: {self.model}")
    
    def analyze_market(
        self,
        coin: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, Any],
        current_position: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze market and generate trading decision
        
        Args:
            coin: Coin symbol
            market_data: Market data including price, volume, etc.
            technical_indicators: Technical indicators (RSI, MACD, etc.)
            current_position: Current position if any
        
        Returns:
            Trading decision with action, confidence, and reasoning
        """
        try:
            # Prepare prompt
            prompt = self._build_analysis_prompt(
                coin, market_data, technical_indicators, current_position
            )
            
            # Call Deepseek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse response
            decision_text = response.choices[0].message.content
            decision = self._parse_decision(decision_text)
            
            self.logger.info(
                f"AI decision for {coin}: {decision.get('action', 'HOLD')} "
                f"(confidence: {decision.get('confidence', 0):.2f})"
            )
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {e}")
            return {
                'action': 'hold',
                'confidence': 0,
                'reasoning': f'Error: {str(e)}'
            }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the AI agent"""
        return """You are an expert cryptocurrency trading analyst and advisor. Your role is to analyze market data, technical indicators, and provide clear trading recommendations.

Your analysis should consider:
1. Technical indicators (RSI, MACD, Moving Averages, Bollinger Bands)
2. Price trends and momentum
3. Volume analysis
4. Market sentiment
5. Risk management principles

Provide your recommendation in the following JSON format:
{
    "action": "buy" | "sell" | "hold",
    "confidence": 0.0 to 1.0,
    "leverage": 1 to 5,
    "entry_price": number,
    "stop_loss": number,
    "take_profit": number,
    "reasoning": "detailed explanation of your decision"
}

Be conservative and prioritize capital preservation. Only recommend trades with high confidence when the setup is clear."""
    
    def _build_analysis_prompt(
        self,
        coin: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, Any],
        current_position: Optional[Dict[str, Any]]
    ) -> str:
        """Build analysis prompt from market data"""
        
        prompt = f"""Analyze the following market data for {coin} and provide a trading recommendation:

## Current Market Data
- Current Price: ${market_data.get('price', 0):.2f}
- 24h Volume: {market_data.get('volume', 0):.2f}

## Technical Indicators
- SMA (20): ${technical_indicators.get('sma', 0):.2f}
- EMA (12): ${technical_indicators.get('ema', 0):.2f}
- RSI (14): {technical_indicators.get('rsi', 0):.2f} ({technical_indicators.get('rsi_signal', 'neutral')})
- MACD: {technical_indicators.get('macd', 0):.4f}
- MACD Signal: {technical_indicators.get('macd_signal', 0):.4f}
- MACD Trend: {technical_indicators.get('macd_signal', 'neutral')}
- Bollinger Upper: ${technical_indicators.get('bb_upper', 0):.2f}
- Bollinger Lower: ${technical_indicators.get('bb_lower', 0):.2f}
- ATR: ${technical_indicators.get('atr', 0):.2f}
- Overall Trend: {technical_indicators.get('trend', 'neutral')}
"""
        
        if current_position:
            prompt += f"""
## Current Position
- Side: {'LONG' if current_position.get('is_long') else 'SHORT'}
- Size: {current_position.get('size', 0):.4f}
- Entry Price: ${current_position.get('entry_price', 0):.2f}
- Leverage: {current_position.get('leverage', 1)}x
- Unrealized PnL: {self._calculate_pnl(current_position, market_data.get('price', 0)):.2f}%
"""
        else:
            prompt += "\n## Current Position\n- No open position\n"
        
        prompt += """
Based on this data, should I BUY, SELL, or HOLD? Provide your recommendation in the specified JSON format with detailed reasoning."""
        
        return prompt
    
    def _calculate_pnl(self, position: Dict[str, Any], current_price: float) -> float:
        """Calculate PnL percentage"""
        entry_price = position.get('entry_price', 0)
        is_long = position.get('is_long', True)
        
        if entry_price == 0:
            return 0
        
        if is_long:
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
        else:
            pnl_pct = ((entry_price - current_price) / entry_price) * 100
        
        return pnl_pct
    
    def _parse_decision(self, decision_text: str) -> Dict[str, Any]:
        """Parse AI decision from text response"""
        try:
            # Try to extract JSON from the response
            # Look for JSON block
            start_idx = decision_text.find('{')
            end_idx = decision_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = decision_text[start_idx:end_idx]
                decision = json.loads(json_str)
                
                # Validate and normalize
                decision['action'] = decision.get('action', 'hold').lower()
                decision['confidence'] = float(decision.get('confidence', 0.5))
                decision['leverage'] = int(decision.get('leverage', 3))
                
                # Ensure confidence is in valid range
                decision['confidence'] = max(0.0, min(1.0, decision['confidence']))
                
                return decision
            else:
                # Fallback: parse from text
                return self._parse_text_decision(decision_text)
                
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON decision: {e}")
            return self._parse_text_decision(decision_text)
        except Exception as e:
            self.logger.error(f"Error parsing decision: {e}")
            return {
                'action': 'hold',
                'confidence': 0,
                'reasoning': 'Failed to parse decision'
            }
    
    def _parse_text_decision(self, text: str) -> Dict[str, Any]:
        """Parse decision from plain text response"""
        text_lower = text.lower()
        
        # Determine action
        if 'buy' in text_lower or 'long' in text_lower:
            action = 'buy'
        elif 'sell' in text_lower or 'short' in text_lower:
            action = 'sell'
        else:
            action = 'hold'
        
        # Try to extract confidence
        confidence = 0.5
        if 'high confidence' in text_lower or 'strong' in text_lower:
            confidence = 0.8
        elif 'low confidence' in text_lower or 'weak' in text_lower:
            confidence = 0.3
        
        return {
            'action': action,
            'confidence': confidence,
            'leverage': 3,
            'reasoning': text
        }
    
    def optimize_strategy_parameters(
        self,
        historical_performance: List[Dict[str, Any]],
        current_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to optimize strategy parameters based on historical performance
        
        Args:
            historical_performance: List of past trades and their outcomes
            current_parameters: Current strategy parameters
        
        Returns:
            Optimized parameters
        """
        try:
            prompt = f"""Analyze the following trading performance and suggest optimized parameters:

## Current Parameters
{json.dumps(current_parameters, indent=2)}

## Recent Performance (last {len(historical_performance)} trades)
Win Rate: {self._calculate_win_rate(historical_performance):.2%}
Average Profit: {self._calculate_avg_profit(historical_performance):.2f}%
Max Drawdown: {self._calculate_max_drawdown(historical_performance):.2f}%

Based on this performance, suggest optimized parameters to improve results while managing risk.
Provide your response in JSON format with the same parameter structure."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in quantitative trading strategy optimization."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            optimized_text = response.choices[0].message.content
            
            # Parse optimized parameters
            start_idx = optimized_text.find('{')
            end_idx = optimized_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = optimized_text[start_idx:end_idx]
                optimized_params = json.loads(json_str)
                
                self.logger.info("Strategy parameters optimized by AI")
                return optimized_params
            else:
                return current_parameters
                
        except Exception as e:
            self.logger.error(f"Error optimizing parameters: {e}")
            return current_parameters
    
    def _calculate_win_rate(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate win rate from trades"""
        if not trades:
            return 0
        wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
        return wins / len(trades)
    
    def _calculate_avg_profit(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate average profit from trades"""
        if not trades:
            return 0
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        return total_pnl / len(trades)
    
    def _calculate_max_drawdown(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate maximum drawdown from trades"""
        if not trades:
            return 0
        
        cumulative = 0
        peak = 0
        max_dd = 0
        
        for trade in trades:
            cumulative += trade.get('pnl', 0)
            if cumulative > peak:
                peak = cumulative
            dd = (peak - cumulative) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
        
        return max_dd * 100
