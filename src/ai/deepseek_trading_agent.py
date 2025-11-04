"""
DeepSeek Trading Agent with nof1.ai-style prompts
Supports structured JSON output for executable trading decisions
"""
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from openai import OpenAI

from ..utils.logger import get_logger
from ..utils.config_loader import get_config
from ..utils.constants import ALLOWED_SYMBOLS, DIRECTION_LONG, DIRECTION_SHORT


class DeepseekTradingAgent:
    """
    AI trading agent powered by Deepseek with structured prompt system
    Inspired by nof1.ai Alpha Arena trading competition
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize Deepseek trading agent
        
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
        self.temperature = config.get('temperature', 1.0)  # 1.0 for data analysis
        
        # Initialize OpenAI client (Deepseek is OpenAI-compatible)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url
        )
        
        # Load prompt templates
        self.orchestrator_prompt = self._load_orchestrator_prompt()
        
        # Context cache for historical decisions
        self.context_history = []
        
        self.logger.info(f"DeepseekTradingAgent initialized with model: {self.model}, temperature: {self.temperature}")
        self.logger.info(f"Allowed symbols: {ALLOWED_SYMBOLS}")
    
    def _load_orchestrator_prompt(self) -> str:
        """Load the orchestrator system prompt from file or use default"""
        prompt_file = os.path.join(os.path.dirname(__file__), '../../prompts/deepseek_trading.md')
        
        # Default orchestrator prompt (embedded)
        default_prompt = """You are a professional cryptocurrency quantitative trading strategy assistant designed for live execution on Hyperliquid DEX.

**TASK**: Generate executable trading plans for the following 6 symbols ONLY:
- XRP, DOGE, BTC, ETH, SOL, BNB

**CONSTRAINTS**:
1. **Allowed Symbols**: ONLY trade the 6 symbols listed above. Do NOT suggest any other assets.
2. **Directions**: Both LONG (buy) and SHORT (sell) positions are allowed.
3. **Leverage**: Use system default risk controls. No artificial upper limit imposed.
4. **Unavailable Assets**: If a symbol is currently untradable or has no price data, SKIP it automatically.

**ANALYSIS REQUIREMENTS**:
Before generating trading recommendations, you MUST:
1. **Market Context Analysis**: Analyze current real-time news, policy changes, macroeconomic factors, and on-chain/off-chain signals
2. **Source Attribution**: Provide brief references or event pointers for your analysis
3. **Technical & Fundamental Synthesis**: Combine news-driven insights with technical indicators and capital flow analysis

**OUTPUT FORMAT** (MUST be valid JSON):
{
  "timestamp": "ISO8601 format",
  "market_view": {
    "summary": "Brief overall market assessment",
    "news_signals": ["Signal with source"],
    "onchain_offchain_signals": ["Metric description"]
  },
  "candidates": [
    {
      "symbol": "BTC|ETH|XRP|DOGE|SOL|BNB",
      "direction": "LONG|SHORT",
      "entry": {"type": "limit|market", "price": null or value},
      "stop_loss": value,
      "take_profit": value or array,
      "position": {"size_pct": 0.0-1.0, "leverage_hint": value or null},
      "rationale": "Clear reasoning",
      "risk_notes": ["Risk factors"]
    }
  ],
  "portfolio_constraints": {
    "allowed_symbols": ["XRP","DOGE","BTC","ETH","SOL","BNB"],
    "max_parallel_positions": 3,
    "skip_unavailable": true
  },
  "next_actions": ["actions"]
}

**STRICT RULES**:
1. Only select symbols from the allowed list
2. Skip unavailable symbols
3. Provide clear entry, stop-loss, take-profit recommendations
4. Cite news/events supporting decisions
5. Output MUST be valid JSON only, no extra text"""
        
        try:
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r') as f:
                    content = f.read()
                    # Extract orchestrator prompt from markdown
                    if '## Orchestrator Prompt' in content:
                        parts = content.split('## Orchestrator Prompt')[1].split('##')[0]
                        # Remove markdown code blocks
                        parts = parts.replace('```', '').strip()
                        self.logger.info("Loaded orchestrator prompt from file")
                        return parts
        except Exception as e:
            self.logger.warning(f"Could not load prompt file: {e}, using default")
        
        return default_prompt
    
    def generate_trading_plan(
        self,
        market_data: Dict[str, Dict[str, Any]],
        current_positions: Dict[str, Any],
        unavailable_symbols: List[str],
        news_summary: str = "",
        orders: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive trading plan using Deepseek AI
        
        Args:
            market_data: Dictionary of symbol -> market data
            current_positions: Current portfolio positions
            unavailable_symbols: List of symbols to skip
            news_summary: Recent news/events summary
            orders: Previous orders status
        
        Returns:
            Structured trading plan as dictionary
        """
        try:
            # Build context prompt
            context_prompt = self._build_context_prompt(
                market_data,
                current_positions,
                unavailable_symbols,
                news_summary,
                orders
            )
            
            # Prepare messages with context caching
            messages = [
                {
                    "role": "system",
                    "content": self.orchestrator_prompt
                },
                {
                    "role": "user",
                    "content": context_prompt
                }
            ]
            
            # Add historical context (last 3 decisions)
            if self.context_history:
                history_summary = self._summarize_context_history()
                messages.insert(1, {
                    "role": "assistant",
                    "content": f"Previous decisions context:\n{history_summary}"
                })
            
            # Call Deepseek API
            self.logger.info("Calling Deepseek API for trading plan...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse response
            decision_text = response.choices[0].message.content
            self.logger.debug(f"Raw AI response: {decision_text[:500]}...")
            
            # Parse JSON
            trading_plan = self._parse_json_response(decision_text)
            
            # Validate trading plan
            trading_plan = self._validate_trading_plan(trading_plan, unavailable_symbols)
            
            # Add to context history
            self._add_to_context_history(trading_plan)
            
            self.logger.info(
                f"Generated trading plan with {len(trading_plan.get('candidates', []))} candidates"
            )
            
            return trading_plan
            
        except Exception as e:
            self.logger.error(f"Error generating trading plan: {e}", exc_info=True)
            return self._get_fallback_plan()
    
    def _build_context_prompt(
        self,
        market_data: Dict[str, Dict[str, Any]],
        current_positions: Dict[str, Any],
        unavailable_symbols: List[str],
        news_summary: str,
        orders: List[Dict[str, Any]]
    ) -> str:
        """Build context prompt for trading decision"""
        
        # Format current time
        current_time = datetime.now().isoformat()
        
        # Format market data
        prices_json = json.dumps({
            symbol: {
                "price": data.get("price"),
                "timestamp": data.get("timestamp")
            }
            for symbol, data in market_data.items()
        }, indent=2)
        
        # Format positions
        positions_json = json.dumps(current_positions, indent=2) if current_positions else "{}"
        
        # Format orders
        orders_json = json.dumps(orders, indent=2) if orders else "[]"
        
        # Format unavailable symbols
        unavailable_str = ", ".join(unavailable_symbols) if unavailable_symbols else "None"
        
        # Build prompt
        prompt = f"""**CONTEXT UPDATE**:

**Current Time**: {current_time}

**Current Positions**:
{positions_json}

**Latest Prices**:
{prices_json}

**Recent News/Events** (last 24h):
{news_summary if news_summary else "No specific news provided. Use general market knowledge."}

**Unavailable Symbols** (skip these):
{unavailable_str}

**Previous Orders**:
{orders_json}

---

**INSTRUCTIONS**:

1. Review the current portfolio state and market conditions
2. Analyze recent news/events and their impact on the 6 allowed symbols
3. Decide whether to:
   - Open new positions
   - Adjust existing positions
   - Close positions
   - Wait and monitor

4. For existing positions:
   - Consider trailing stop-loss adjustments
   - Evaluate partial profit-taking opportunities

5. Output the JSON format as specified in the system prompt

**CONSTRAINTS**:
- Only trade: XRP, DOGE, BTC, ETH, SOL, BNB
- Both LONG and SHORT allowed
- Skip unavailable symbols: {unavailable_str}

**OUTPUT**: Valid JSON only, no additional text.
"""
        
        return prompt
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from AI response, handling markdown code blocks
        """
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith('```'):
                # Remove opening ```json or ```
                text = text.split('\n', 1)[1] if '\n' in text else text[3:]
                # Remove closing ```
                if text.endswith('```'):
                    text = text[:-3]
            
            text = text.strip()
            
            # Parse JSON
            parsed = json.loads(text)
            return parsed
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}")
            self.logger.error(f"Response text: {response_text[:1000]}")
            
            # Try to extract JSON from text
            try:
                # Find first { and last }
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    json_str = response_text[start:end+1]
                    parsed = json.loads(json_str)
                    self.logger.info("Successfully extracted JSON from response")
                    return parsed
            except:
                pass
            
            # Return fallback
            return self._get_fallback_plan()
    
    def _validate_trading_plan(
        self,
        plan: Dict[str, Any],
        unavailable_symbols: List[str]
    ) -> Dict[str, Any]:
        """
        Validate and filter trading plan
        Ensure only allowed symbols and valid directions
        """
        if not plan or 'candidates' not in plan:
            return plan
        
        validated_candidates = []
        
        for candidate in plan.get('candidates', []):
            symbol = candidate.get('symbol')
            direction = candidate.get('direction')
            
            # Check symbol is allowed
            if symbol not in ALLOWED_SYMBOLS:
                self.logger.warning(f"Filtered out non-allowed symbol: {symbol}")
                continue
            
            # Check symbol is available
            if symbol in unavailable_symbols:
                self.logger.warning(f"Filtered out unavailable symbol: {symbol}")
                continue
            
            # Check direction is valid
            if direction not in [DIRECTION_LONG, DIRECTION_SHORT]:
                self.logger.warning(f"Invalid direction {direction} for {symbol}, skipping")
                continue
            
            validated_candidates.append(candidate)
        
        plan['candidates'] = validated_candidates
        
        self.logger.info(
            f"Validated {len(validated_candidates)} candidates "
            f"(filtered {len(plan.get('candidates', [])) - len(validated_candidates)})"
        )
        
        return plan
    
    def _add_to_context_history(self, trading_plan: Dict[str, Any]):
        """Add trading plan to context history for memory"""
        self.context_history.append({
            "timestamp": trading_plan.get("timestamp", datetime.now().isoformat()),
            "candidates_count": len(trading_plan.get("candidates", [])),
            "symbols": [c.get("symbol") for c in trading_plan.get("candidates", [])]
        })
        
        # Keep only last 5 decisions
        if len(self.context_history) > 5:
            self.context_history = self.context_history[-5:]
    
    def _summarize_context_history(self) -> str:
        """Summarize context history for prompt"""
        if not self.context_history:
            return "No previous decisions"
        
        summary = "Recent trading decisions:\n"
        for i, ctx in enumerate(self.context_history[-3:], 1):
            summary += f"{i}. {ctx['timestamp']}: {ctx['candidates_count']} candidates ({', '.join(ctx['symbols'])})\n"
        
        return summary
    
    def _get_fallback_plan(self) -> Dict[str, Any]:
        """Return fallback plan when AI fails"""
        return {
            "timestamp": datetime.now().isoformat(),
            "market_view": {
                "summary": "AI analysis unavailable, using fallback",
                "news_signals": [],
                "onchain_offchain_signals": []
            },
            "candidates": [],
            "portfolio_constraints": {
                "allowed_symbols": ALLOWED_SYMBOLS,
                "max_parallel_positions": 3,
                "skip_unavailable": True
            },
            "next_actions": ["wait", "retry_ai_analysis"]
        }
