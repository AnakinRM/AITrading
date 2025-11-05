# 每24小时新闻汇总与重点提取 Prompt

## 系统说明

此 prompt 用于每24小时一次的新闻汇总,整合过去24小时收集的所有新闻,提取关键主题和最重要的新闻,为交易决策提供宏观视角。

---

## SYSTEM PROMPT

```
You are a senior cryptocurrency market analyst specializing in synthesizing large amounts of news data into actionable insights. Your task is to review all news collected over the past 24 hours, identify key themes, and highlight the most important developments that could impact cryptocurrency markets.

YOUR ROLE:
- Review and synthesize 24 hours of news data
- Identify overarching themes and narratives
- Highlight the most market-moving news items
- Provide strategic insights for traders
- Connect dots between seemingly unrelated events

ANALYSIS APPROACH:
- Look for patterns and recurring themes
- Identify cause-and-effect relationships
- Assess cumulative impact of multiple news items
- Consider both immediate and longer-term implications
- Distinguish between noise and signal

OUTPUT REQUIREMENTS:
- Comprehensive daily summary (1-2 paragraphs)
- Top 5-10 most important news items
- Key themes and narratives
- Market sentiment analysis
- Strategic trading implications
- Output in structured JSON format

CRITICAL REMINDERS:
- Focus on IMPACT, not just volume of news
- Consider interconnections between events
- Provide forward-looking insights
- Be objective and balanced in assessment
```

---

## USER PROMPT TEMPLATE

```
Current Time: {current_time}
Analysis Period: Past 24 Hours ({start_time} to {end_time})

Below is ALL the news collected over the past 24 hours through hourly searches. Each entry represents one hour's worth of news analysis.

TOTAL NEWS ITEMS: {total_news_count}
HOURLY REPORTS: {hourly_report_count}

===== 24-HOUR NEWS DATA =====

{all_hourly_news_data}

===== YOUR TASK =====

Please analyze ALL the news above and provide a comprehensive 24-hour summary with the following:

1. **Daily Summary**
   - Write a 1-2 paragraph overview of the past 24 hours
   - Highlight the most significant developments
   - Describe the overall market narrative

2. **Top Important News**
   - Select the 5-10 MOST IMPORTANT news items from the entire 24-hour period
   - Rank them by impact on cryptocurrency markets
   - For each, explain WHY it's important

3. **Key Themes**
   - Identify 3-5 major themes or narratives that emerged
   - Examples: "Fed hawkishness", "Institutional adoption", "Regulatory clarity"
   - Explain how these themes developed throughout the day

4. **Market Sentiment Evolution**
   - Describe how market sentiment changed over 24 hours
   - Identify any sentiment shifts and their catalysts
   - Assess current sentiment: Bullish / Bearish / Neutral / Mixed

5. **Interconnections**
   - Identify connections between different news items
   - Explain cause-and-effect relationships
   - Highlight compounding effects

6. **Strategic Implications**
   - What should traders focus on in the next 24 hours?
   - Which coins are likely to be most affected?
   - What are the key risks and opportunities?

OUTPUT FORMAT:

Please provide your analysis in the following JSON format:

{
  "analysis_time": "{current_time}",
  "period_start": "{start_time}",
  "period_end": "{end_time}",
  "total_news_analyzed": 0,
  
  "daily_summary": {
    "overview": "1-2 paragraph comprehensive summary",
    "market_narrative": "The dominant story of the day",
    "sentiment_evolution": "How sentiment changed over 24 hours"
  },
  
  "top_important_news": [
    {
      "rank": 1,
      "title": "News headline",
      "category": "Web3|Financial|International|Macro|Bitcoin",
      "summary": "Brief summary",
      "source": "Source name",
      "timestamp": "2025-11-04 14:30:00",
      "importance_reasoning": "Why this is in top 10",
      "market_impact": "Bullish|Bearish|Neutral",
      "affected_coins": ["BTC", "ETH"],
      "impact_timeframe": "Immediate|Short-term|Medium-term|Long-term"
    }
  ],
  
  "key_themes": [
    {
      "theme": "Theme name",
      "description": "What this theme is about",
      "related_news_count": 0,
      "impact_assessment": "How this theme affects markets",
      "outlook": "Where this theme is heading"
    }
  ],
  
  "market_sentiment": {
    "overall": "Bullish|Bearish|Neutral|Mixed",
    "confidence": "High|Medium|Low",
    "sentiment_by_category": {
      "Web3": "Bullish|Bearish|Neutral",
      "Financial": "Bullish|Bearish|Neutral",
      "International": "Bullish|Bearish|Neutral",
      "Macro": "Bullish|Bearish|Neutral",
      "Bitcoin": "Bullish|Bearish|Neutral"
    },
    "sentiment_drivers": ["Driver 1", "Driver 2", "Driver 3"]
  },
  
  "interconnections": [
    {
      "connection": "Description of connection",
      "news_items": ["News 1", "News 2"],
      "impact": "Combined impact explanation"
    }
  ],
  
  "strategic_implications": {
    "next_24h_focus": ["Focus area 1", "Focus area 2"],
    "coins_to_watch": [
      {
        "coin": "BTC",
        "reasoning": "Why to watch",
        "bias": "Bullish|Bearish|Neutral"
      }
    ],
    "key_risks": ["Risk 1", "Risk 2"],
    "key_opportunities": ["Opportunity 1", "Opportunity 2"],
    "recommended_actions": ["Action 1", "Action 2"]
  },
  
  "statistics": {
    "total_news_items": 0,
    "by_category": {
      "Web3": 0,
      "Financial": 0,
      "International": 0,
      "Macro": 0,
      "Bitcoin": 0
    },
    "by_impact": {
      "Bullish": 0,
      "Bearish": 0,
      "Neutral": 0
    },
    "by_urgency": {
      "High": 0,
      "Medium": 0,
      "Low": 0
    }
  }
}

IMPORTANT:
- Be comprehensive but concise
- Focus on ACTIONABLE insights
- Connect the dots between events
- Provide forward-looking analysis
- Be objective and balanced
```

---

## 示例输出

```json
{
  "analysis_time": "2025-11-05 00:00:00",
  "period_start": "2025-11-04 00:00:00",
  "period_end": "2025-11-05 00:00:00",
  "total_news_analyzed": 87,
  
  "daily_summary": {
    "overview": "The past 24 hours were dominated by the Federal Reserve's decision to hold interest rates steady at 5.25-5.50%, with Chair Powell signaling a higher-for-longer stance that initially pressured risk assets including crypto. However, this bearish macro backdrop was offset by extremely bullish Bitcoin-specific news, particularly BlackRock's record $500M single-day ETF inflow and continued institutional accumulation. The day also saw strong on-chain activity across major Layer-1 blockchains, with Solana processing a record 65M transactions. By day's end, Bitcoin managed to hold key support levels despite macro headwinds, suggesting strong underlying demand. The crypto market demonstrated resilience in the face of traditional finance uncertainty.",
    
    "market_narrative": "Institutional Bitcoin demand vs. Macro headwinds - The battle between growing institutional adoption (ETF inflows, corporate treasuries) and restrictive monetary policy (higher-for-longer rates) defined the day. Bitcoin's ability to maintain support despite Fed hawkishness signals a potential decoupling from traditional risk assets.",
    
    "sentiment_evolution": "Started neutral-to-bearish on Fed rate decision (14:00), shifted bullish on BlackRock ETF news (14:30), consolidated mixed through afternoon as traders digested conflicting signals, ended cautiously bullish as Bitcoin held support and on-chain metrics remained strong."
  },
  
  "top_important_news": [
    {
      "rank": 1,
      "title": "Federal Reserve Holds Interest Rates Steady, Signals Higher-for-Longer",
      "category": "Macro",
      "summary": "Fed maintained rates at 5.25-5.50% and Chair Powell indicated rates may stay elevated longer than expected, citing persistent inflation concerns.",
      "source": "Reuters",
      "timestamp": "2025-11-04 14:30:00",
      "importance_reasoning": "Central bank policy is the single most important macro driver for all risk assets. Higher-for-longer rates reduce liquidity and increase opportunity cost of holding non-yielding assets like Bitcoin. This sets the macro backdrop for all crypto trading.",
      "market_impact": "Bearish",
      "affected_coins": ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE"],
      "impact_timeframe": "Medium-term"
    },
    {
      "rank": 2,
      "title": "BlackRock's Bitcoin ETF Records $500M Single-Day Inflow",
      "category": "Bitcoin",
      "summary": "IBIT saw its largest single-day inflow since launch, bringing AUM to over $25B. Institutional demand continues accelerating.",
      "source": "Bloomberg",
      "timestamp": "2025-11-04 14:15:00",
      "importance_reasoning": "Massive institutional inflows directly reduce Bitcoin supply available on exchanges and demonstrate strong demand despite macro headwinds. This is the strongest bullish signal for Bitcoin specifically and suggests price support at current levels.",
      "market_impact": "Bullish",
      "affected_coins": ["BTC"],
      "impact_timeframe": "Immediate"
    },
    {
      "rank": 3,
      "title": "Solana Processes Record 65M Transactions in 24 Hours",
      "category": "Web3",
      "summary": "SOL blockchain hit all-time high transaction volume, surpassing all other L1s, driven by DeFi and meme coin activity.",
      "source": "The Block",
      "timestamp": "2025-11-04 13:30:00",
      "importance_reasoning": "Record usage demonstrates real adoption and utility, not just speculation. Solana is capturing market share from Ethereum and showing it can handle high throughput. This supports SOL's value proposition and price.",
      "market_impact": "Bullish",
      "affected_coins": ["SOL"],
      "impact_timeframe": "Short-term"
    },
    {
      "rank": 4,
      "title": "SEC Delays Decision on Ethereum ETF Applications",
      "category": "Bitcoin",
      "summary": "SEC pushed back decision deadline on multiple Ethereum ETF applications to Q1 2026, citing need for more review time.",
      "source": "CoinDesk",
      "timestamp": "2025-11-04 16:45:00",
      "importance_reasoning": "Delays regulatory clarity for Ethereum and dampens near-term institutional demand expectations. However, delay is not rejection, so long-term outlook remains intact. Creates short-term uncertainty for ETH.",
      "market_impact": "Bearish",
      "affected_coins": ["ETH"],
      "impact_timeframe": "Short-term"
    },
    {
      "rank": 5,
      "title": "China's Manufacturing PMI Beats Expectations at 51.2",
      "category": "Macro",
      "summary": "Chinese manufacturing expanded more than expected, suggesting stimulus measures are working and economy is stabilizing.",
      "source": "Bloomberg",
      "timestamp": "2025-11-04 13:45:00",
      "importance_reasoning": "China is a major crypto market and improved economic conditions typically increase retail and institutional participation. Positive China data supports global risk appetite and can drive crypto inflows.",
      "market_impact": "Bullish",
      "affected_coins": ["BTC", "ETH"],
      "impact_timeframe": "Medium-term"
    }
  ],
  
  "key_themes": [
    {
      "theme": "Institutional Bitcoin Accumulation",
      "description": "Continued strong demand from institutional investors via ETFs, corporate treasuries, and traditional finance firms entering crypto",
      "related_news_count": 12,
      "impact_assessment": "Extremely bullish for Bitcoin specifically. Creates price floor and reduces supply. Legitimizes Bitcoin as institutional asset class.",
      "outlook": "Trend likely to continue and accelerate. More traditional finance firms expected to enter. Potential supply squeeze if demand continues at current pace."
    },
    {
      "theme": "Fed Higher-for-Longer Stance",
      "description": "Federal Reserve maintaining restrictive monetary policy longer than markets hoped, keeping rates elevated to combat inflation",
      "related_news_count": 8,
      "impact_assessment": "Bearish for all risk assets including crypto. Reduces liquidity, increases opportunity cost, pressures valuations.",
      "outlook": "Likely to persist through Q1 2026 unless inflation drops significantly or recession emerges. Crypto may need to prove it can perform in high-rate environment."
    },
    {
      "theme": "Layer-1 Blockchain Competition",
      "description": "Intense competition among L1 blockchains (Solana, Ethereum, BNB Chain) for users, developers, and transaction volume",
      "related_news_count": 15,
      "impact_assessment": "Creates winners and losers among L1 tokens. Solana gaining ground on Ethereum. Performance and adoption metrics matter more than narratives.",
      "outlook": "Competition will intensify. Expect continued innovation in scalability and user experience. Market share shifts likely to continue."
    },
    {
      "theme": "Regulatory Uncertainty",
      "description": "Ongoing lack of clarity on crypto regulation, especially around ETFs, DeFi, and stablecoins",
      "related_news_count": 7,
      "impact_assessment": "Creates volatility and limits institutional participation in some areas. However, Bitcoin ETFs have achieved clarity, which is bullish.",
      "outlook": "Gradual improvement expected but will remain bumpy. ETH ETF approval likely in 2026. DeFi and stablecoin regulation still unclear."
    },
    {
      "theme": "China Economic Stabilization",
      "description": "Chinese economy showing signs of stabilization after stimulus measures, with improving manufacturing and consumption data",
      "related_news_count": 5,
      "impact_assessment": "Positive for global risk appetite and crypto. China is major crypto market. Improved conditions could drive retail and institutional flows.",
      "outlook": "Cautiously optimistic. Stimulus measures appear to be working. Watch for continued data improvement and any policy changes."
    }
  ],
  
  "market_sentiment": {
    "overall": "Mixed",
    "confidence": "Medium",
    "sentiment_by_category": {
      "Web3": "Bullish",
      "Financial": "Neutral",
      "International": "Neutral",
      "Macro": "Bearish",
      "Bitcoin": "Bullish"
    },
    "sentiment_drivers": [
      "Institutional Bitcoin demand (Bullish)",
      "Fed higher-for-longer (Bearish)",
      "Strong on-chain activity (Bullish)",
      "Regulatory delays (Bearish)",
      "China stabilization (Bullish)"
    ]
  },
  
  "interconnections": [
    {
      "connection": "Fed policy vs. Bitcoin ETF demand",
      "news_items": [
        "Fed holds rates steady",
        "BlackRock ETF $500M inflow"
      ],
      "impact": "Despite bearish macro (high rates), Bitcoin-specific demand remains extremely strong. This suggests Bitcoin may be decoupling from traditional risk assets and behaving more like a store-of-value. If this continues, Bitcoin could outperform other crypto and traditional assets in high-rate environment."
    },
    {
      "connection": "China PMI + Risk appetite",
      "news_items": [
        "China manufacturing PMI beats",
        "Increased DeFi activity",
        "Solana record transactions"
      ],
      "impact": "Improving China data supports global risk appetite, which flows into crypto markets. The surge in on-chain activity (Solana, DeFi) may be partly driven by increased Asian participation as China economy stabilizes."
    },
    {
      "connection": "ETH ETF delay + SOL outperformance",
      "news_items": [
        "SEC delays ETH ETF decision",
        "Solana processes record transactions"
      ],
      "impact": "ETH regulatory uncertainty creates opportunity for competitors like Solana. As ETH faces institutional headwinds, SOL is capturing market share through superior performance and user adoption. This could lead to continued SOL outperformance vs. ETH in short term."
    }
  ],
  
  "strategic_implications": {
    "next_24h_focus": [
      "Bitcoin support levels around $100,000 - key psychological level",
      "Continued ETF flow data - watch for sustained institutional demand",
      "Any Fed speaker commentary - could add volatility",
      "Solana vs. Ethereum performance - L1 competition heating up",
      "China economic data - next data points for stabilization confirmation"
    ],
    
    "coins_to_watch": [
      {
        "coin": "BTC",
        "reasoning": "Battle between institutional demand and macro headwinds. Holding $100k support would be very bullish. ETF flows suggest strong hands accumulating.",
        "bias": "Bullish"
      },
      {
        "coin": "SOL",
        "reasoning": "Record transaction volume shows real adoption. Gaining market share from ETH. Technical breakout possible if momentum continues.",
        "bias": "Bullish"
      },
      {
        "coin": "ETH",
        "reasoning": "ETF delay creates near-term uncertainty. Losing market share to SOL. However, long-term fundamentals intact. May underperform in short term.",
        "bias": "Neutral"
      }
    ],
    
    "key_risks": [
      "Fed turns even more hawkish - could pressure all risk assets",
      "Bitcoin breaks below $100k support - would trigger stop losses",
      "Unexpected negative regulatory news - always a risk in crypto",
      "China data disappoints - would hurt risk appetite",
      "Major exchange or protocol hack - could cause market-wide selloff"
    ],
    
    "key_opportunities": [
      "Bitcoin dip to $98k-100k - strong institutional bid should provide support",
      "Solana momentum trade - record usage could drive continued outperformance",
      "ETH accumulation if it dips on ETF delay - long-term still bullish",
      "China-related tokens if economic data continues improving",
      "Volatility trading around Fed speakers and data releases"
    ],
    
    "recommended_actions": [
      "Maintain long Bitcoin exposure - institutional demand too strong to fade",
      "Consider adding Solana on any dips - momentum and fundamentals aligned",
      "Reduce Ethereum exposure or hedge - near-term headwinds from ETF delay",
      "Set tight stop-losses - macro environment remains uncertain",
      "Monitor $100k Bitcoin level closely - key support/resistance",
      "Stay nimble - sentiment can shift quickly on Fed commentary",
      "Focus on coins with strong on-chain metrics - fundamentals matter in uncertain macro"
    ]
  },
  
  "statistics": {
    "total_news_items": 87,
    "by_category": {
      "Web3": 28,
      "Financial": 15,
      "International": 8,
      "Macro": 18,
      "Bitcoin": 18
    },
    "by_impact": {
      "Bullish": 42,
      "Bearish": 23,
      "Neutral": 22
    },
    "by_urgency": {
      "High": 12,
      "Medium": 38,
      "Low": 37
    }
  }
}
```

---

## 使用说明

### 1. 调用频率

- **每24小时一次** (建议在每天00:00执行)
- 例如: 2025-11-05 00:00:00

### 2. 数据输入

收集过去24小时的所有hourly news文件:

```python
# 读取过去24小时的所有新闻
hourly_files = sorted(Path("news_data/hourly").glob("news_2025-11-04_*.json"))
all_news = []
for file in hourly_files:
    with open(file) as f:
        all_news.append(json.load(f))
```

### 3. 数据存储

将每日汇总存储到:

```
news_data/daily/daily_summary_2025-11-04.json
```

### 4. 与交易系统集成

将每日汇总添加到交易决策prompt中:

```
===== 24-HOUR NEWS SUMMARY =====

{daily_news_summary}
```

---

## 实现示例

```python
import json
from datetime import datetime, timedelta
from pathlib import Path

class DailyNewsAnalyzer:
    def __init__(self, deepseek_client):
        self.client = deepseek_client
        self.hourly_dir = Path("news_data/hourly")
        self.daily_dir = Path("news_data/daily")
        self.daily_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_daily_news(self):
        """每24小时汇总分析新闻"""
        current_time = datetime.now()
        start_time = current_time - timedelta(hours=24)
        end_time = current_time
        
        # 收集过去24小时的所有新闻
        all_hourly_news = self._collect_hourly_news(start_time, end_time)
        
        if not all_hourly_news:
            print("No news data found for past 24 hours")
            return None
        
        # 构建prompt
        prompt = self._build_prompt(
            current_time, 
            start_time, 
            end_time, 
            all_hourly_news
        )
        
        # 调用Deepseek
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0,
            max_tokens=8000
        )
        
        # 解析JSON
        daily_summary = json.loads(response.choices[0].message.content)
        
        # 存储到文件
        self._save_daily_summary(daily_summary, current_time)
        
        return daily_summary
    
    def _collect_hourly_news(self, start_time, end_time):
        """收集指定时间范围内的所有hourly news"""
        all_news = []
        
        # 查找所有符合时间范围的文件
        for hour in range(24):
            timestamp = start_time + timedelta(hours=hour)
            pattern = f"news_{timestamp.strftime('%Y-%m-%d_%H')}-*.json"
            files = list(self.hourly_dir.glob(pattern))
            
            for file in files:
                with open(file, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
                    all_news.append(news_data)
        
        return all_news
    
    def _save_daily_summary(self, summary, timestamp):
        """存储每日汇总"""
        filename = f"daily_summary_{timestamp.strftime('%Y-%m-%d')}.json"
        filepath = self.daily_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Daily summary saved to: {filepath}")
```

---

## 注意事项

1. **数据量**: 24小时的新闻可能很多,注意token限制
2. **处理时间**: 分析可能需要较长时间,建议异步处理
3. **存储管理**: 每日汇总文件较大,注意存储空间
4. **错误处理**: 如果某些hourly文件缺失,应优雅处理
5. **时区**: 确保所有时间戳使用统一时区

---

## 版本信息

- 版本: 1.0
- 创建日期: 2025-11-04
- 用途: 每24小时新闻汇总与重点提取
