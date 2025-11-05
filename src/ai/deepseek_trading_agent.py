"""
DeepSeek Trading Agent with nof1.ai-style prompts
Supports structured JSON output for executable trading decisions
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from openai import OpenAI

from ..utils.logger import get_logger
from ..utils.config_loader import get_config
from ..utils.constants import ALLOWED_SYMBOLS, DIRECTION_LONG, DIRECTION_SHORT
from ..news.news_analyzer import NewsAnalyzer


class DeepseekTradingAgent:
    """
    AI trading agent powered by Deepseek with structured prompt system
    Inspired by nof1.ai Alpha Arena trading competition
    """
    
    def __init__(self, config: dict = None, news_analyzer: NewsAnalyzer = None):
        """
        Initialize Deepseek trading agent
        
        Args:
            config: Deepseek configuration dictionary
            news_analyzer: NewsAnalyzer instance for news integration
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
        
        # News analyzer for news integration
        self.news_analyzer = news_analyzer
        
        # Allowed trading symbols
        self.allowed_symbols = ALLOWED_SYMBOLS
        
        # Dialog log file for debugging
        project_root = Path(__file__).parent.parent.parent
        self.dialog_log_path = project_root / "logs" / "ai_dialogs.log"
        self.dialog_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"DeepseekTradingAgent initialized with model: {self.model}, temperature: {self.temperature}")
        self.logger.info(f"Allowed symbols: {ALLOWED_SYMBOLS}")
        if self.news_analyzer:
            self.logger.info("News integration enabled")
    
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
            
            # Log dialog for debugging
            self._log_dialog(context_prompt, decision_text)
            
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
        """Build context prompt for trading decision with news integration"""
        
        # Format current time
        current_time = datetime.now().isoformat()
        
        # Get formatted news if news_analyzer is available
        today_hourly_news = "No hourly news available for today."
        past_7_days_summaries = "No daily summaries available for past 7 days."
        
        if self.news_analyzer:
            try:
                today_hourly_news = self.news_analyzer.format_today_hourly_news_for_prompt()
                past_7_days_summaries = self.news_analyzer.format_past_n_days_summaries_for_prompt(7)
                self.logger.info("Successfully retrieved formatted news data")
            except Exception as e:
                self.logger.warning(f"Failed to retrieve news data: {e}")
        
        # Import EnhancedMarketDataCollector for formatting
        from ..data.enhanced_market_data import EnhancedMarketDataCollector
        
        # Format market data with detailed technical indicators
        market_data_sections = []
        for symbol in self.allowed_symbols:
            if symbol in market_data:
                formatted = EnhancedMarketDataCollector(None).format_market_data_for_prompt(market_data[symbol])
                market_data_sections.append(formatted)
        
        market_data_text = "\n".join(market_data_sections)
        
        # Format unavailable symbols
        unavailable_str = ", ".join(unavailable_symbols) if unavailable_symbols else "None"
        
        # Format positions and orders
        positions_text = str(current_positions) if current_positions else "No current positions"
        orders_text = str(orders) if orders else "No previous orders"
        
        # Build prompt in nof1.ai style with news integration
        prompt = f"""**CONTEXT UPDATE**:

**Current Time**: {current_time}

═══════════════════════════════════════════════════════════════
SECTION 1: NEWS CONTEXT
═══════════════════════════════════════════════════════════════

Before analyzing technical data, review the latest news developments that may be driving market movements.

───────────────────────────────────────────────────────────────
1A. TODAY'S HOURLY NEWS UPDATES
───────────────────────────────────────────────────────────────

{today_hourly_news}

───────────────────────────────────────────────────────────────
1B. PAST 7 DAYS DAILY NEWS SUMMARIES
───────────────────────────────────────────────────────────────

{past_7_days_summaries}

═══════════════════════════════════════════════════════════════
SECTION 2: MARKET DATA
═══════════════════════════════════════════════════════════════

CURRENT MARKET STATE FOR ALL COINS

{market_data_text}

**Unavailable Symbols** (skip these): {unavailable_str}

═══════════════════════════════════════════════════════════════
SECTION 3: ACCOUNT INFORMATION
═══════════════════════════════════════════════════════════════

HERE IS YOUR ACCOUNT INFORMATION & PERFORMANCE

{positions_text}

{orders_text}

═══════════════════════════════════════════════════════════════
SECTION 4: YOUR TRADING DECISION
═══════════════════════════════════════════════════════════════

Based on the comprehensive information above (NEWS + MARKET DATA + POSITIONS):

STEP 1: NEWS UPDATE CHECK
1. Has any new news emerged since your last decision?
2. Does any new news contradict your current positions?
3. Are there new catalysts that create opportunities?

STEP 2: POSITION REVIEW
4. How are your current positions performing relative to your thesis?
5. Is the market reacting to news as expected?
6. Should you hold, adjust stop-loss/take-profit, or close positions?

STEP 3: NEW OPPORTUNITIES
7. Are there new opportunities based on updated news or technicals?
8. Which coins have the clearest setup now?

STEP 4: RISK MANAGEMENT
9. What are the key risks (technical and news-based) to monitor?
10. Should position sizes be adjusted based on new information?

STEP 5: OUTPUT
Please provide your trading decisions in the required JSON format, ensuring:
- "market_view" section highlights any new developments from news
- "candidates" array includes actions for both existing and new positions
- "rationale" explains how news + market data support each decision

CRITICAL: Always check for news updates first, then analyze how the market is reacting.

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

    def analyze_market(
        self,
        coin: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, Any],
        current_position: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze market for a single coin (compatibility method for AITradingStrategy)
        
        This method provides backward compatibility with the old DeepseekAgent interface
        while using the new trading plan generation system with news integration.
        
        Args:
            coin: Symbol to analyze
            market_data: Market data for the coin
            technical_indicators: Technical indicators
            current_position: Current position if any
            
        Returns:
            Trading decision dictionary compatible with old interface
        """
        try:
            # Build market data dict for generate_trading_plan
            full_market_data = {
                coin: {
                    "price": market_data.get('price', 0),
                    "timestamp": datetime.now().isoformat(),
                    "volume": market_data.get('volume', 0),
                    **technical_indicators
                }
            }
            
            # Build current positions dict
            positions = {}
            if current_position:
                positions[coin] = current_position
            
            # Generate trading plan using new system
            trading_plan = self.generate_trading_plan(
                market_data=full_market_data,
                current_positions=positions,
                unavailable_symbols=[],
                news_summary="",
                orders=[]
            )
            
            # Extract decision for this coin from trading plan
            candidates = trading_plan.get('candidates', [])
            
            # Find candidate for this coin
            coin_candidate = None
            for candidate in candidates:
                if candidate.get('symbol') == coin:
                    coin_candidate = candidate
                    break
            
            # Convert to old format
            if coin_candidate:
                direction = coin_candidate.get('direction', 'LONG')
                entry = coin_candidate.get('entry', {})
                position_info = coin_candidate.get('position', {})
                
                return {
                    'action': 'buy' if direction == 'LONG' else 'sell',
                    'confidence': 0.8,  # Default confidence
                    'entry_price': entry.get('price', market_data.get('price', 0)),
                    'stop_loss': coin_candidate.get('stop_loss', 0),
                    'take_profit': coin_candidate.get('take_profit', 0),
                    'size': position_info.get('size_pct', 0.1),
                    'leverage': position_info.get('leverage_hint', 3),
                    'reason': coin_candidate.get('rationale', 'AI analysis'),
                    'risk_notes': coin_candidate.get('risk_notes', [])
                }
            else:
                # No candidate for this coin, return hold
                market_view = trading_plan.get('market_view', {})
                return {
                    'action': 'hold',
                    'confidence': 0.5,
                    'reason': market_view.get('summary', 'No clear trading opportunity identified'),
                    'risk_notes': []
                }
                
        except Exception as e:
            self.logger.error(f"Error in analyze_market for {coin}: {e}", exc_info=True)
            return {
                'action': 'hold',
                'confidence': 0.0,
                'reason': f'Error: {str(e)}',
                'risk_notes': []
            }

    def _log_dialog(self, prompt: str, response_text: str) -> None:
        """
        Persist Deepseek prompt/response to the shared log file for debugging
        
        Args:
            prompt: The context prompt sent to AI
            response_text: The AI's response
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "prompt": prompt,
            "response": response_text,
        }
        try:
            with open(self.dialog_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self.logger.debug(f"Dialog logged to {self.dialog_log_path}")
        except Exception as exc:
            self.logger.error(f"Failed to persist AI dialog: {exc}")
