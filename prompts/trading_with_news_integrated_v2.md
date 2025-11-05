# Trading Prompt with News Integration (Final Version)

## 完整的交易Prompt格式

---

## USER PROMPT (发送给Deepseek的完整内容)

```
It has been {runtime_minutes} minutes since you started trading. The current time is {current_time} and you've been invoked {invocation_count} times. Below, we are providing you with a variety of state data, price data, and predictive signals so you can discover alpha. Below that is your current account information, value, performance, positions, etc.

ALL OF THE PRICE OR SIGNAL DATA BELOW IS ORDERED: OLDEST → NEWEST

Timeframes note: Unless stated otherwise in a section title, intraday series are provided at 3‑minute intervals. If a coin uses a different interval, it is explicitly stated in that coin's section.

═══════════════════════════════════════════════════════════════
SECTION 1: NEWS CONTEXT
═══════════════════════════════════════════════════════════════

Before analyzing technical data, review the latest news developments that may be driving market movements.

───────────────────────────────────────────────────────────────
1A. TODAY'S HOURLY NEWS UPDATES
───────────────────────────────────────────────────────────────

{today_hourly_news_all}

───────────────────────────────────────────────────────────────
1B. PAST 7 DAYS DAILY NEWS SUMMARIES
───────────────────────────────────────────────────────────────

{past_7_days_daily_summaries}

═══════════════════════════════════════════════════════════════
SECTION 2: MARKET DATA
═══════════════════════════════════════════════════════════════

{market_data_section}

═══════════════════════════════════════════════════════════════
SECTION 3: ACCOUNT INFORMATION
═══════════════════════════════════════════════════════════════

Current Total Return (percent): {total_return_pct}%

Available Cash: ${available_cash}

Current Account Value: ${account_value}

Sharpe Ratio: {sharpe_ratio}

Current live positions & performance:

{positions_dict}

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
- "news_analysis" section highlights any new developments
- "technical_analysis" section covers current market regime
- "decisions" array includes actions for both existing and new positions
- "rationale" explains how news + technicals support each decision
- "news_catalyst" identifies specific news driving each decision

CRITICAL: Always check for news updates first, then analyze how the market is reacting.

Required JSON output format:
{
  "news_analysis": {
    "key_news_impact": "string",
    "market_narrative": "string",
    "sentiment": "bullish|bearish|mixed|neutral",
    "news_driven_opportunities": ["string", ...]
  },
  "technical_analysis": {
    "market_regime": "trending|ranging|volatile",
    "key_observations": ["string", ...],
    "risk_assessment": "low|medium|high"
  },
  "decisions": [
    {
      "symbol": "BTC|ETH|SOL|BNB|XRP|DOGE",
      "action": "OPEN_LONG|OPEN_SHORT|HOLD|ADJUST|CLOSE",
      "rationale": "string (explain news + technical support)",
      "news_catalyst": "string (specific news driving this decision)",
      "confidence": 0.0-1.0,
      "position_size_pct": 0.0-1.0 (null if HOLD/ADJUST/CLOSE),
      "leverage": 1-20 (null if HOLD/ADJUST/CLOSE),
      "entry_price": float (null if HOLD/ADJUST/CLOSE),
      "stop_loss": float,
      "take_profit": float,
      "invalidation_condition": "string"
    }
  ]
}
```

---

## 变量说明

### 元信息变量

```python
runtime_minutes = 19026  # 运行时长(分钟)
current_time = "2025-11-04 18:17:07.996112"  # 当前时间
invocation_count = 11819  # 被调用次数
```

### 新闻变量

#### today_hourly_news_all

格式:
```
Hour 1: 2025-11-04 09:00:00
Total News: 5
Market Sentiment: Mixed
Key Themes: Fed policy, ETF flows

News Items:
1. [Macro] Fed Holds Rates Steady - Impact: Bearish | Urgency: High
   Summary: Federal Reserve maintains interest rates at 5.25-5.50%, signaling continued hawkish stance. 
   This could pressure risk assets including crypto in the short term.
   Affected Coins: BTC, ETH, SOL

2. [Bitcoin] BlackRock Bitcoin ETF Sees $200M Inflow - Impact: Bullish | Urgency: Medium
   Summary: Institutional demand remains strong despite macro headwinds. This is the 5th consecutive 
   day of net inflows, suggesting sustained institutional interest.
   Affected Coins: BTC

3. [Web3] Solana Network Upgrade Scheduled - Impact: Bullish | Urgency: Low
   Summary: Solana announces major network upgrade to improve transaction speeds and reduce fees. 
   Expected to roll out in 48 hours.
   Affected Coins: SOL

4. [International] EU Approves New Crypto Regulation Framework - Impact: Neutral | Urgency: Medium
   Summary: European Union finalizes MiCA regulations, providing regulatory clarity but adding 
   compliance requirements for exchanges.
   Affected Coins: BTC, ETH, BNB

5. [Financial] Major Bank Announces Crypto Custody Services - Impact: Bullish | Urgency: Medium
   Summary: JPMorgan expands crypto services, offering institutional custody for BTC and ETH. 
   Signals growing mainstream acceptance.
   Affected Coins: BTC, ETH

Trading Implications: Watch BTC support at $100K. Fed hawkishness may create short-term pressure, 
but strong ETF inflows provide support. SOL upgrade could drive momentum.

---

Hour 2: 2025-11-04 10:00:00
Total News: 3
Market Sentiment: Bullish
Key Themes: Institutional adoption, DeFi growth

News Items:
1. [Ethereum] Ethereum Gas Fees Drop 40% - Impact: Bullish | Urgency: High
   Summary: Network congestion eases significantly, making DeFi more accessible. Could drive 
   increased activity and ETH demand.
   Affected Coins: ETH

2. [DeFi] Major Protocol Launches on BNB Chain - Impact: Bullish | Urgency: Medium
   Summary: Leading DeFi protocol expands to BNB Chain, potentially increasing network activity 
   and BNB utility.
   Affected Coins: BNB

3. [Ripple] XRP Wins Partial Victory in SEC Case - Impact: Bullish | Urgency: High
   Summary: Court rules in favor of Ripple on key points, reducing regulatory uncertainty. 
   Could trigger short-term rally.
   Affected Coins: XRP

Trading Implications: Strong bullish catalysts for ETH, BNB, and XRP. Consider long positions 
with tight stops in case of profit-taking.

---

(继续显示当天其他小时的新闻...)
```

#### past_7_days_daily_summaries

格式:
```
Day 1: 2025-11-03
Total News Analyzed: 87

Daily Overview:
Market was dominated by conflicting signals - strong institutional demand through ETF inflows 
contrasted with macro headwinds from persistent Fed hawkishness. Bitcoin held the $100K level 
despite selling pressure, while altcoins showed mixed performance. Ethereum benefited from 
network upgrade anticipation, while meme coins like DOGE faced profit-taking.

Market Narrative:
Institutional demand vs. macro headwinds. The crypto market is caught between two powerful forces: 
growing institutional adoption (evidenced by record ETF inflows and major banks entering the space) 
and macro pressure from central bank policies. This creates a range-bound environment with high 
volatility.

Top 5 Important News:
1. [Bitcoin] Record $500M Single-Day ETF Inflow - Impact: Bullish
   Why Important: Largest single-day inflow since ETF launch, showing unprecedented institutional 
   demand. This provides strong support for BTC price and validates the institutional adoption thesis.

2. [Macro] Fed Chair Powell Signals No Rate Cuts Until 2025 - Impact: Bearish
   Why Important: Removes hope for near-term monetary easing, which typically supports risk assets. 
   This could cap upside for crypto in the short term and increase volatility.

3. [Ethereum] Vitalik Buterin Proposes Major Protocol Change - Impact: Neutral/Bullish
   Why Important: Shows continued innovation and development of Ethereum ecosystem. Could drive 
   long-term value but may create short-term uncertainty during implementation.

4. [Regulation] US Senator Proposes Pro-Crypto Bill - Impact: Bullish
   Why Important: Signals potential for favorable regulatory framework in the US, reducing a major 
   source of uncertainty for the industry.

5. [DeFi] $100M Exploit on Major Protocol - Impact: Bearish
   Why Important: Highlights ongoing security risks in DeFi space. Could trigger risk-off sentiment 
   and capital rotation away from smaller altcoins.

Key Themes:
- Fed hawkishness: Central bank maintaining restrictive policy, creating headwinds for risk assets
- Institutional adoption: Record ETF inflows and traditional finance entering crypto space
- DeFi security: Ongoing exploits raising concerns about smart contract risks

Strategic Implications:
- Next 24h Focus: CPI data release, ETF flow data, Bitcoin support at $100K
- Key Risks: Fed hawkish surprise, major exchange outage, regulatory crackdown
- Key Opportunities: Dip buying on strong support levels, ETH ahead of upgrade, XRP on legal clarity

Sentiment Evolution:
Started bearish on Fed comments, shifted to cautiously bullish as ETF inflows absorbed selling 
pressure. Ended the day neutral with market participants waiting for CPI data.

---

Day 2: 2025-11-02
Total News Analyzed: 72

Daily Overview:
Consolidation day with low volatility as market digested previous week's gains. Bitcoin traded 
in tight range around $101K while altcoins showed relative strength. News flow was lighter than 
usual, with focus on technical levels and on-chain metrics.

Market Narrative:
Healthy consolidation after rally. Market taking a breather after strong gains, with participants 
watching for the next catalyst. On-chain metrics remain bullish, suggesting underlying strength 
despite sideways price action.

Top 5 Important News:
1. [Bitcoin] On-Chain Data Shows Accumulation by Long-Term Holders - Impact: Bullish
   Why Important: Indicates strong hands are buying the dip, reducing available supply and 
   supporting higher prices longer-term.

2. [Solana] Network Achieves Record Transaction Speed - Impact: Bullish
   Why Important: Demonstrates technical superiority and scalability, potentially attracting 
   more developers and users to the ecosystem.

3. [Binance] Exchange Announces New Listing Standards - Impact: Neutral
   Why Important: Could affect which tokens get listed, impacting altcoin market dynamics. 
   Generally positive for quality projects.

4. [Dogecoin] Elon Musk Tweet Mentions DOGE - Impact: Bullish (Short-term)
   Why Important: Historically drives short-term volatility and trading volume in DOGE. 
   Typically fades quickly but can create trading opportunities.

5. [Market Structure] Options Open Interest Hits All-Time High - Impact: Bullish
   Why Important: Shows growing institutional participation and market maturity. High open 
   interest can amplify moves in either direction.

Key Themes:
- Market maturity: Growing options market and institutional infrastructure
- Technical strength: Strong on-chain metrics despite sideways price action
- Altcoin rotation: Capital flowing from Bitcoin to select altcoins

Strategic Implications:
- Next 24h Focus: Breakout or breakdown from consolidation range, altcoin momentum
- Key Risks: Failed breakout leading to correction, sudden negative news
- Key Opportunities: Range trading, altcoin momentum plays, options strategies

Sentiment Evolution:
Neutral throughout the day with slight bullish bias into close. Market participants positioning 
for potential breakout while respecting key support levels.

---

(继续显示Day 3-7的汇总...)
```

### 市场数据变量

#### market_data_section

包含两个子部分:

**2A. 过去24小时K线数据 (仅首次调用时包含)**

```
───────────────────────────────────────────────────────────────
2A. PAST 24 HOURS - 10 MINUTE CANDLES (FOR INITIAL CONTEXT)
───────────────────────────────────────────────────────────────

This is your FIRST invocation. Below are the past 24 hours of 10-minute candle data for each coin 
to help you understand recent price action before making your first trading decision.

BTC 10-min candles (144 candles, oldest → newest):
Format: [timestamp, open, high, low, close, volume]

[2025-11-03 10:00, 101234.5, 101456.0, 101123.0, 101345.0, 1234.5]
[2025-11-03 10:10, 101345.0, 101567.0, 101234.0, 101456.0, 1456.7]
[2025-11-03 10:20, 101456.0, 101678.0, 101345.0, 101567.0, 1567.8]
...
[2025-11-04 09:50, 100456.0, 100567.0, 100345.0, 100456.0, 1234.5]

ETH 10-min candles (144 candles, oldest → newest):
[2025-11-03 10:00, 3456.78, 3478.90, 3445.67, 3467.89, 567.8]
[2025-11-03 10:10, 3467.89, 3489.01, 3456.78, 3478.90, 678.9]
...

SOL 10-min candles (144 candles, oldest → newest):
[2025-11-03 10:00, 192.34, 193.45, 191.23, 192.56, 234.5]
...

BNB 10-min candles (144 candles, oldest → newest):
[2025-11-03 10:00, 567.89, 569.01, 566.78, 568.12, 123.4]
...

XRP 10-min candles (144 candles, oldest → newest):
[2025-11-03 10:00, 0.6234, 0.6256, 0.6212, 0.6245, 12345.6]
...

DOGE 10-min candles (144 candles, oldest → newest):
[2025-11-03 10:00, 0.1234, 0.1245, 0.1223, 0.1236, 123456.7]
...

Now, based on this 24-hour context and the news above, what is your initial trading strategy?
```

**2B. 当前市场状态 (每次调用都包含)**

```
───────────────────────────────────────────────────────────────
2B. CURRENT MARKET STATE FOR ALL COINS
───────────────────────────────────────────────────────────────

ALL BTC DATA
current_price = {btc_price}, current_ema20 = {btc_ema20}, current_macd = {btc_macd}, current_rsi (7 period) = {btc_rsi7}

In addition, here is the latest BTC open interest and funding rate for perps:

Open Interest: Latest: {btc_oi_latest}B Average: {btc_oi_avg}B

Funding Rate: {btc_funding_rate}% ({btc_funding_direction})

Intraday series (3-minute intervals, oldest → latest):

Mid prices: {btc_mid_prices}

EMA indicators (20-period): {btc_ema20_series}

MACD indicators: {btc_macd_series}

RSI indicators (7-Period): {btc_rsi7_series}

RSI indicators (14-Period): {btc_rsi14_series}

Longer-term context (4-hour timeframe):

20-Period EMA: {btc_4h_ema20} vs. 50-Period EMA: {btc_4h_ema50}

3-Period ATR: {btc_4h_atr3} vs. 14-Period ATR: {btc_4h_atr14}

Current Volume: {btc_4h_volume_current}B vs. Average Volume: {btc_4h_volume_avg}B

MACD indicators: {btc_4h_macd_series}

RSI indicators (14-Period): {btc_4h_rsi14_series}

---

ALL ETH DATA
current_price = {eth_price}, current_ema20 = {eth_ema20}, current_macd = {eth_macd}, current_rsi (7 period) = {eth_rsi7}

In addition, here is the latest ETH open interest and funding rate for perps:

Open Interest: Latest: {eth_oi_latest}B Average: {eth_oi_avg}B

Funding Rate: {eth_funding_rate}% ({eth_funding_direction})

Intraday series (3-minute intervals, oldest → latest):

Mid prices: {eth_mid_prices}

EMA indicators (20-period): {eth_ema20_series}

MACD indicators: {eth_macd_series}

RSI indicators (7-Period): {eth_rsi7_series}

RSI indicators (14-Period): {eth_rsi14_series}

Longer-term context (4-hour timeframe):

20-Period EMA: {eth_4h_ema20} vs. 50-Period EMA: {eth_4h_ema50}

3-Period ATR: {eth_4h_atr3} vs. 14-Period ATR: {eth_4h_atr14}

Current Volume: {eth_4h_volume_current}B vs. Average Volume: {eth_4h_volume_avg}B

MACD indicators: {eth_4h_macd_series}

RSI indicators (14-Period): {eth_4h_rsi14_series}

---

(同样格式显示 SOL, BNB, XRP, DOGE 的完整数据)
```

### 账户信息变量

```python
total_return_pct = -3.24
available_cash = 7234.56
account_value = 9676.00
sharpe_ratio = -0.45

positions_dict = {
    'BTC': {
        'symbol': 'BTC',
        'quantity': 0.38,
        'entry_price': 101456.0,
        'current_price': 100601.5,
        'liquidation_price': 97630.22,
        'unrealized_pnl': -324.71,
        'unrealized_pnl_pct': -3.2,
        'leverage': 20,
        'position_value': 38228.57,
        'exit_plan': {
            'profit_target': 104300.0,
            'stop_loss': 99200.0,
            'invalidation': 'Break below 99000 or negative funding persists >24h'
        },
        'confidence': 0.75,
        'risk_usd': 860.0,
        'entry_order_id': 'btc_entry_20251104_090123',
        'tp_order_id': 'btc_tp_20251104_090124',
        'sl_order_id': 'btc_sl_20251104_090125',
        'wait_for_fill': False,
        'notional_size': 38228.57
    },
    'ETH': {
        'symbol': 'ETH',
        'quantity': 2.5,
        'entry_price': 3467.89,
        'current_price': 3456.78,
        'liquidation_price': 3234.56,
        'unrealized_pnl': -27.78,
        'unrealized_pnl_pct': -0.32,
        'leverage': 10,
        'position_value': 8641.95,
        'exit_plan': {
            'profit_target': 3567.00,
            'stop_loss': 3400.00,
            'invalidation': 'Break below 3380 or gas fees spike >100 gwei'
        },
        'confidence': 0.82,
        'risk_usd': 169.47,
        'entry_order_id': 'eth_entry_20251104_091234',
        'tp_order_id': 'eth_tp_20251104_091235',
        'sl_order_id': 'eth_sl_20251104_091236',
        'wait_for_fill': False,
        'notional_size': 8641.95
    }
}
```

---

## Python实现示例

```python
from datetime import datetime, timedelta
import json

def build_trading_prompt(
    runtime_minutes: int,
    invocation_count: int,
    is_first_call: bool,
    today_hourly_news: list,
    past_7_days_summaries: list,
    market_data: dict,
    account_info: dict,
    positions: dict
) -> str:
    """
    构建完整的交易prompt
    
    Args:
        runtime_minutes: 运行时长(分钟)
        invocation_count: 被调用次数
        is_first_call: 是否首次调用
        today_hourly_news: 今天的每小时新闻列表
        past_7_days_summaries: 过去7天的每日汇总列表
        market_data: 市场数据字典
        account_info: 账户信息字典
        positions: 持仓信息字典
    
    Returns:
        完整的prompt字符串
    """
    
    current_time = datetime.now().isoformat()
    
    # 1. 格式化今天的hourly news
    today_news_text = format_today_hourly_news(today_hourly_news)
    
    # 2. 格式化过去7天的daily summaries
    past_7_days_text = format_past_7_days_summaries(past_7_days_summaries)
    
    # 3. 格式化市场数据
    market_data_text = format_market_data(market_data, is_first_call)
    
    # 4. 格式化账户信息
    account_text = format_account_info(account_info)
    
    # 5. 格式化持仓信息
    positions_text = json.dumps(positions, indent=4)
    
    # 6. 构建完整prompt
    prompt = f"""It has been {runtime_minutes} minutes since you started trading. The current time is {current_time} and you've been invoked {invocation_count} times. Below, we are providing you with a variety of state data, price data, and predictive signals so you can discover alpha. Below that is your current account information, value, performance, positions, etc.

ALL OF THE PRICE OR SIGNAL DATA BELOW IS ORDERED: OLDEST → NEWEST

Timeframes note: Unless stated otherwise in a section title, intraday series are provided at 3‑minute intervals. If a coin uses a different interval, it is explicitly stated in that coin's section.

═══════════════════════════════════════════════════════════════
SECTION 1: NEWS CONTEXT
═══════════════════════════════════════════════════════════════

Before analyzing technical data, review the latest news developments that may be driving market movements.

───────────────────────────────────────────────────────────────
1A. TODAY'S HOURLY NEWS UPDATES
───────────────────────────────────────────────────────────────

{today_news_text}

───────────────────────────────────────────────────────────────
1B. PAST 7 DAYS DAILY NEWS SUMMARIES
───────────────────────────────────────────────────────────────

{past_7_days_text}

═══════════════════════════════════════════════════════════════
SECTION 2: MARKET DATA
═══════════════════════════════════════════════════════════════

{market_data_text}

═══════════════════════════════════════════════════════════════
SECTION 3: ACCOUNT INFORMATION
═══════════════════════════════════════════════════════════════

{account_text}

Current live positions & performance:

{positions_text}

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
- "news_analysis" section highlights any new developments
- "technical_analysis" section covers current market regime
- "decisions" array includes actions for both existing and new positions
- "rationale" explains how news + technicals support each decision
- "news_catalyst" identifies specific news driving each decision

CRITICAL: Always check for news updates first, then analyze how the market is reacting.

Required JSON output format:
{{
  "news_analysis": {{
    "key_news_impact": "string",
    "market_narrative": "string",
    "sentiment": "bullish|bearish|mixed|neutral",
    "news_driven_opportunities": ["string", ...]
  }},
  "technical_analysis": {{
    "market_regime": "trending|ranging|volatile",
    "key_observations": ["string", ...],
    "risk_assessment": "low|medium|high"
  }},
  "decisions": [
    {{
      "symbol": "BTC|ETH|SOL|BNB|XRP|DOGE",
      "action": "OPEN_LONG|OPEN_SHORT|HOLD|ADJUST|CLOSE",
      "rationale": "string (explain news + technical support)",
      "news_catalyst": "string (specific news driving this decision)",
      "confidence": 0.0-1.0,
      "position_size_pct": 0.0-1.0 (null if HOLD/ADJUST/CLOSE),
      "leverage": 1-20 (null if HOLD/ADJUST/CLOSE),
      "entry_price": float (null if HOLD/ADJUST/CLOSE),
      "stop_loss": float,
      "take_profit": float,
      "invalidation_condition": "string"
    }}
  ]
}}
"""
    
    return prompt


def format_today_hourly_news(hourly_news: list) -> str:
    """格式化今天的每小时新闻"""
    result = []
    
    for hour_data in hourly_news:
        hour_text = f"""Hour {hour_data['hour']}: {hour_data['timestamp']}
Total News: {hour_data['total_news']}
Market Sentiment: {hour_data['sentiment']}
Key Themes: {', '.join(hour_data['themes'])}

News Items:"""
        
        for i, news in enumerate(hour_data['news_items'], 1):
            news_text = f"""
{i}. [{news['category']}] {news['title']} - Impact: {news['impact']} | Urgency: {news['urgency']}
   Summary: {news['summary']}
   Affected Coins: {', '.join(news['affected_coins'])}"""
            hour_text += news_text
        
        hour_text += f"\n\nTrading Implications: {hour_data['trading_implications']}\n"
        result.append(hour_text)
    
    return "\n---\n\n".join(result)


def format_past_7_days_summaries(summaries: list) -> str:
    """格式化过去7天的每日汇总"""
    result = []
    
    for day_data in summaries:
        day_text = f"""Day {day_data['day']}: {day_data['date']}
Total News Analyzed: {day_data['total_news']}

Daily Overview:
{day_data['overview']}

Market Narrative:
{day_data['narrative']}

Top 5 Important News:"""
        
        for i, news in enumerate(day_data['top_news'], 1):
            news_text = f"""
{i}. [{news['category']}] {news['title']} - Impact: {news['impact']}
   Why Important: {news['why_important']}"""
            day_text += news_text
        
        day_text += f"""

Key Themes:
{chr(10).join(f"- {theme['name']}: {theme['description']}" for theme in day_data['themes'])}

Strategic Implications:
- Next 24h Focus: {day_data['strategic']['next_24h_focus']}
- Key Risks: {day_data['strategic']['key_risks']}
- Key Opportunities: {day_data['strategic']['key_opportunities']}

Sentiment Evolution:
{day_data['sentiment_evolution']}
"""
        result.append(day_text)
    
    return "\n---\n\n".join(result)


def format_market_data(market_data: dict, is_first_call: bool) -> str:
    """格式化市场数据"""
    result = []
    
    # 如果是首次调用,添加24小时K线数据
    if is_first_call:
        result.append("""───────────────────────────────────────────────────────────────
2A. PAST 24 HOURS - 10 MINUTE CANDLES (FOR INITIAL CONTEXT)
───────────────────────────────────────────────────────────────

This is your FIRST invocation. Below are the past 24 hours of 10-minute candle data for each coin 
to help you understand recent price action before making your first trading decision.
""")
        
        for symbol in ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']:
            candles = market_data['24h_candles'][symbol]
            result.append(f"\n{symbol} 10-min candles (144 candles, oldest → newest):")
            result.append("Format: [timestamp, open, high, low, close, volume]\n")
            for candle in candles:
                result.append(str(candle))
        
        result.append("\nNow, based on this 24-hour context and the news above, what is your initial trading strategy?\n")
    
    # 添加当前市场状态
    result.append("""───────────────────────────────────────────────────────────────
2B. CURRENT MARKET STATE FOR ALL COINS
───────────────────────────────────────────────────────────────
""")
    
    for symbol in ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']:
        coin_data = market_data['current'][symbol]
        
        coin_text = f"""
ALL {symbol} DATA
current_price = {coin_data['price']}, current_ema20 = {coin_data['ema20']}, current_macd = {coin_data['macd']}, current_rsi (7 period) = {coin_data['rsi7']}

In addition, here is the latest {symbol} open interest and funding rate for perps:

Open Interest: Latest: {coin_data['oi_latest']}B Average: {coin_data['oi_avg']}B

Funding Rate: {coin_data['funding_rate']}% ({coin_data['funding_direction']})

Intraday series (3-minute intervals, oldest → latest):

Mid prices: {coin_data['mid_prices']}

EMA indicators (20-period): {coin_data['ema20_series']}

MACD indicators: {coin_data['macd_series']}

RSI indicators (7-Period): {coin_data['rsi7_series']}

RSI indicators (14-Period): {coin_data['rsi14_series']}

Longer-term context (4-hour timeframe):

20-Period EMA: {coin_data['4h_ema20']} vs. 50-Period EMA: {coin_data['4h_ema50']}

3-Period ATR: {coin_data['4h_atr3']} vs. 14-Period ATR: {coin_data['4h_atr14']}

Current Volume: {coin_data['4h_volume_current']}B vs. Average Volume: {coin_data['4h_volume_avg']}B

MACD indicators: {coin_data['4h_macd_series']}

RSI indicators (14-Period): {coin_data['4h_rsi14_series']}

---
"""
        result.append(coin_text)
    
    return "\n".join(result)


def format_account_info(account_info: dict) -> str:
    """格式化账户信息"""
    return f"""Current Total Return (percent): {account_info['total_return_pct']}%

Available Cash: ${account_info['available_cash']}

Current Account Value: ${account_info['account_value']}

Sharpe Ratio: {account_info['sharpe_ratio']}"""


# 使用示例
if __name__ == "__main__":
    # 示例数据
    runtime_minutes = 19026
    invocation_count = 11819
    is_first_call = False
    
    # 今天的hourly news (从news_storage获取)
    today_hourly_news = [
        {
            'hour': 1,
            'timestamp': '2025-11-04 09:00:00',
            'total_news': 5,
            'sentiment': 'Mixed',
            'themes': ['Fed policy', 'ETF flows'],
            'news_items': [
                {
                    'category': 'Macro',
                    'title': 'Fed Holds Rates Steady',
                    'impact': 'Bearish',
                    'urgency': 'High',
                    'summary': 'Federal Reserve maintains interest rates at 5.25-5.50%...',
                    'affected_coins': ['BTC', 'ETH', 'SOL']
                },
                # ... 更多新闻
            ],
            'trading_implications': 'Watch BTC support at $100K...'
        },
        # ... 更多小时
    ]
    
    # 过去7天的summaries (从news_storage获取)
    past_7_days_summaries = [
        {
            'day': 1,
            'date': '2025-11-03',
            'total_news': 87,
            'overview': 'Market was dominated by conflicting signals...',
            'narrative': 'Institutional demand vs. macro headwinds...',
            'top_news': [
                {
                    'category': 'Bitcoin',
                    'title': 'Record $500M Single-Day ETF Inflow',
                    'impact': 'Bullish',
                    'why_important': 'Largest single-day inflow since ETF launch...'
                },
                # ... 更多top news
            ],
            'themes': [
                {'name': 'Fed hawkishness', 'description': 'Central bank maintaining restrictive policy...'},
                # ... 更多主题
            ],
            'strategic': {
                'next_24h_focus': 'CPI data release, ETF flow data...',
                'key_risks': 'Fed hawkish surprise, major exchange outage...',
                'key_opportunities': 'Dip buying on strong support levels...'
            },
            'sentiment_evolution': 'Started bearish on Fed comments...'
        },
        # ... 更多天
    ]
    
    # 市场数据
    market_data = {
        '24h_candles': {
            'BTC': [[...], [...], ...],  # 144个10分钟K线
            # ... 其他币种
        },
        'current': {
            'BTC': {
                'price': 100601.5,
                'ema20': 101234.0,
                'macd': -45.6,
                'rsi7': 42.3,
                'oi_latest': 15.2,
                'oi_avg': 14.8,
                'funding_rate': 0.0085,
                'funding_direction': 'positive, longs paying shorts',
                'mid_prices': [100234.0, 100345.0, ...],
                'ema20_series': [101456.0, 101445.0, ...],
                'macd_series': [-23.4, -28.9, ...],
                'rsi7_series': [48.5, 46.7, ...],
                'rsi14_series': [52.3, 51.2, ...],
                '4h_ema20': 102345.0,
                '4h_ema50': 103456.0,
                '4h_atr3': 1234.5,
                '4h_atr14': 1567.8,
                '4h_volume_current': 2.5,
                '4h_volume_avg': 2.2,
                '4h_macd_series': [-56.7, -62.3, ...],
                '4h_rsi14_series': [54.3, 53.2, ...]
            },
            # ... 其他币种
        }
    }
    
    # 账户信息
    account_info = {
        'total_return_pct': -3.24,
        'available_cash': 7234.56,
        'account_value': 9676.00,
        'sharpe_ratio': -0.45
    }
    
    # 持仓信息
    positions = {
        'BTC': {
            'symbol': 'BTC',
            'quantity': 0.38,
            'entry_price': 101456.0,
            'current_price': 100601.5,
            'liquidation_price': 97630.22,
            'unrealized_pnl': -324.71,
            'unrealized_pnl_pct': -3.2,
            'leverage': 20,
            'position_value': 38228.57,
            'exit_plan': {
                'profit_target': 104300.0,
                'stop_loss': 99200.0,
                'invalidation': 'Break below 99000 or negative funding persists >24h'
            },
            'confidence': 0.75,
            'risk_usd': 860.0,
            'entry_order_id': 'btc_entry_20251104_090123',
            'tp_order_id': 'btc_tp_20251104_090124',
            'sl_order_id': 'btc_sl_20251104_090125',
            'wait_for_fill': False,
            'notional_size': 38228.57
        },
        # ... 其他持仓
    }
    
    # 构建prompt
    prompt = build_trading_prompt(
        runtime_minutes=runtime_minutes,
        invocation_count=invocation_count,
        is_first_call=is_first_call,
        today_hourly_news=today_hourly_news,
        past_7_days_summaries=past_7_days_summaries,
        market_data=market_data,
        account_info=account_info,
        positions=positions
    )
    
    print(prompt)
```

---

## 总结

这个prompt完整保留了nof1.ai的原始开场白:

```
It has been {runtime_minutes} minutes since you started trading. 
The current time is {current_time} and you've been invoked {invocation_count} times. 
Below, we are providing you with a variety of state data, price data, and predictive signals 
so you can discover alpha. Below that is your current account information, value, performance, positions, etc.

ALL OF THE PRICE OR SIGNAL DATA BELOW IS ORDERED: OLDEST → NEWEST

Timeframes note: Unless stated otherwise in a section title, intraday series are provided at 
3‑minute intervals. If a coin uses a different interval, it is explicitly stated in that coin's section.
```

然后在这个开场白之后,按顺序添加:
1. 新闻上下文 (今天hourly + 过去7天daily)
2. 市场数据 (24h K线 + 当前状态)
3. 账户信息
4. 交易决策要求

完全符合您的要求! ✅
