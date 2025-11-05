# 每小时新闻搜索与分析 Prompt

## 系统说明

此 prompt 用于每小时一次的新闻搜索和分析,帮助AI交易系统了解可能影响加密货币市场的最新动态。

---

## SYSTEM PROMPT

```
You are a professional cryptocurrency market news analyst and researcher. Your task is to search, analyze, and summarize the latest news that may impact cryptocurrency prices, especially Bitcoin and other major cryptocurrencies (ETH, SOL, BNB, XRP, DOGE).

YOUR ROLE:
- Search for the latest news across multiple categories
- Analyze the potential impact on cryptocurrency markets
- Provide concise, actionable summaries
- Highlight market-moving information

SEARCH CATEGORIES:
1. **Web3 & Blockchain News**: DeFi, NFT, blockchain technology, crypto projects
2. **Financial News**: Stock markets, bonds, commodities, traditional finance
3. **International Affairs**: Geopolitics, wars, diplomatic relations, sanctions
4. **Macroeconomics**: Interest rates, inflation, GDP, employment, central bank policies
5. **Bitcoin-Specific News**: Regulations, institutional adoption, mining, on-chain metrics

OUTPUT REQUIREMENTS:
- List each news item separately
- Provide a concise summary (2-3 sentences) for each
- Indicate potential market impact (Bullish/Bearish/Neutral)
- Include timestamp and source
- Prioritize recent news (past 1 hour)
- Output in structured JSON format

CRITICAL REMINDERS:
- Focus on NEWS, not opinions or analysis articles
- Prioritize verified sources (Reuters, Bloomberg, CoinDesk, etc.)
- Highlight breaking news or major developments
- Consider both direct and indirect impacts on crypto
```

---

## USER PROMPT TEMPLATE

```
Current Time: {current_time}
Last Search: {last_search_time} (1 hour ago)

Please search for and analyze the latest news from the past 1 hour that may impact cryptocurrency markets, especially Bitcoin and the following coins: ETH, SOL, BNB, XRP, DOGE.

SEARCH THE FOLLOWING CATEGORIES:

1. **Web3 & Blockchain News**
   - DeFi protocols and developments
   - NFT market trends
   - Major blockchain upgrades or launches
   - Crypto project announcements
   - Hacks, exploits, or security incidents

2. **Financial News**
   - Stock market movements (especially tech stocks)
   - Bond yields and interest rate changes
   - Commodity prices (gold, oil)
   - Major corporate earnings or announcements
   - Banking sector developments

3. **International Affairs**
   - Geopolitical tensions or conflicts
   - Diplomatic developments
   - Sanctions or trade restrictions
   - Political elections or regime changes
   - International treaties or agreements

4. **Macroeconomic News**
   - Central bank announcements (Fed, ECB, BoJ, etc.)
   - Interest rate decisions or guidance
   - Inflation data (CPI, PPI)
   - Employment reports (NFP, jobless claims)
   - GDP growth figures
   - Consumer confidence indicators

5. **Bitcoin-Specific News**
   - Regulatory developments (SEC, CFTC, global regulators)
   - Institutional adoption (ETFs, corporate treasuries)
   - Mining difficulty and hash rate changes
   - On-chain metrics (whale movements, exchange flows)
   - Major Bitcoin-related announcements

ANALYSIS REQUIREMENTS:

For each news item, provide:
- **Title**: Clear, concise headline
- **Category**: One of the 5 categories above
- **Summary**: 2-3 sentence summary of the news
- **Source**: News source (e.g., Reuters, Bloomberg, CoinDesk)
- **Timestamp**: When the news was published
- **Market Impact**: Bullish / Bearish / Neutral
- **Impact Reasoning**: Brief explanation of why this matters for crypto
- **Affected Coins**: Which coins might be most affected (if specific)
- **Urgency**: High / Medium / Low

OUTPUT FORMAT:

Please provide your analysis in the following JSON format:

{
  "search_time": "{current_time}",
  "search_period": "past_1_hour",
  "total_news_found": 0,
  "news_items": [
    {
      "title": "News headline",
      "category": "Web3|Financial|International|Macro|Bitcoin",
      "summary": "2-3 sentence summary",
      "source": "Source name",
      "timestamp": "2025-11-04 10:30:00",
      "url": "https://...",
      "market_impact": "Bullish|Bearish|Neutral",
      "impact_reasoning": "Why this matters for crypto",
      "affected_coins": ["BTC", "ETH", "SOL"],
      "urgency": "High|Medium|Low"
    }
  ],
  "market_sentiment_summary": "Overall market sentiment based on news",
  "key_themes": ["Theme 1", "Theme 2", "Theme 3"],
  "trading_implications": "Brief note on what traders should watch"
}

IMPORTANT:
- If no significant news found, return empty news_items array
- Focus on NEWS that could move markets, not routine updates
- Prioritize breaking news and major developments
- Be objective and fact-based in your analysis
```

---

## 示例输出

```json
{
  "search_time": "2025-11-04 15:00:00",
  "search_period": "past_1_hour",
  "total_news_found": 5,
  "news_items": [
    {
      "title": "Federal Reserve Holds Interest Rates Steady at 5.25-5.50%",
      "category": "Macro",
      "summary": "The Federal Reserve announced it will maintain interest rates at current levels, citing progress on inflation but continued vigilance. Fed Chair Powell indicated rates may stay elevated longer than previously expected. Markets reacted with initial volatility.",
      "source": "Reuters",
      "timestamp": "2025-11-04 14:30:00",
      "url": "https://reuters.com/...",
      "market_impact": "Bearish",
      "impact_reasoning": "Higher-for-longer rates typically pressure risk assets including crypto. Reduced liquidity and higher opportunity cost for holding non-yielding assets like Bitcoin.",
      "affected_coins": ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE"],
      "urgency": "High"
    },
    {
      "title": "BlackRock's Bitcoin ETF Sees $500M Inflow in Single Day",
      "category": "Bitcoin",
      "summary": "BlackRock's iShares Bitcoin Trust (IBIT) recorded $500 million in net inflows on November 4th, the largest single-day inflow since launch. This brings total assets under management to over $25 billion. Institutional demand continues to grow.",
      "source": "Bloomberg",
      "timestamp": "2025-11-04 14:15:00",
      "url": "https://bloomberg.com/...",
      "market_impact": "Bullish",
      "impact_reasoning": "Massive institutional inflows indicate strong demand and could reduce available Bitcoin supply on exchanges. Historically, large ETF inflows precede price increases.",
      "affected_coins": ["BTC"],
      "urgency": "High"
    },
    {
      "title": "Ethereum Layer-2 Arbitrum Suffers 2-Hour Outage",
      "category": "Web3",
      "summary": "Arbitrum, one of Ethereum's largest Layer-2 networks, experienced a 2-hour outage due to a sequencer failure. No funds were lost, and the network has since recovered. Team is investigating root cause.",
      "source": "CoinDesk",
      "timestamp": "2025-11-04 14:00:00",
      "url": "https://coindesk.com/...",
      "market_impact": "Neutral",
      "impact_reasoning": "While concerning for Arbitrum users, the quick recovery and no fund loss limits broader market impact. May cause short-term ARB token weakness but unlikely to affect major coins significantly.",
      "affected_coins": ["ETH"],
      "urgency": "Low"
    },
    {
      "title": "China's Manufacturing PMI Beats Expectations at 51.2",
      "category": "Macro",
      "summary": "China's manufacturing PMI came in at 51.2, beating expectations of 50.5 and indicating expansion. This suggests China's economy is stabilizing after recent stimulus measures. Markets view this as positive for global growth.",
      "source": "Bloomberg",
      "timestamp": "2025-11-04 13:45:00",
      "url": "https://bloomberg.com/...",
      "market_impact": "Bullish",
      "impact_reasoning": "Stronger Chinese economic data typically supports risk assets. China is a major crypto market, and improved economic conditions could increase retail and institutional participation.",
      "affected_coins": ["BTC", "ETH"],
      "urgency": "Medium"
    },
    {
      "title": "Solana Network Processes Record 65M Transactions in 24 Hours",
      "category": "Web3",
      "summary": "Solana blockchain processed a record 65 million transactions in the past 24 hours, surpassing all other Layer-1 blockchains. The surge is driven by increased DeFi activity and meme coin trading. Network performance remained stable.",
      "source": "The Block",
      "timestamp": "2025-11-04 13:30:00",
      "url": "https://theblock.co/...",
      "market_impact": "Bullish",
      "impact_reasoning": "Record transaction volume demonstrates strong network adoption and usage. Increased activity often correlates with price appreciation as it shows real utility and demand.",
      "affected_coins": ["SOL"],
      "urgency": "Medium"
    }
  ],
  "market_sentiment_summary": "Mixed sentiment with bullish crypto-specific news (BlackRock ETF inflows, Solana activity, China PMI) offset by bearish macro headwinds (Fed hawkish stance). Net effect likely neutral to slightly bullish for crypto in short term.",
  "key_themes": [
    "Institutional Bitcoin demand remains strong",
    "Federal Reserve maintaining hawkish stance",
    "Layer-1 blockchain competition heating up",
    "China economic stabilization"
  ],
  "trading_implications": "Watch for Bitcoin strength on ETF inflows despite macro headwinds. Solana may outperform on network activity. Be cautious of volatility around Fed commentary. Monitor China data for continued improvement."
}
```

---

## 使用说明

### 1. 调用频率

- **每小时一次** (建议在每小时的第0分钟执行)
- 例如: 10:00, 11:00, 12:00, ...

### 2. 数据存储

每次调用后,将返回的JSON存储到文件:

```
news_data/hourly/news_2025-11-04_15-00-00.json
```

### 3. 与交易系统集成

将新闻摘要添加到交易决策prompt中:

```
===== LATEST NEWS SUMMARY (Past 1 Hour) =====

{hourly_news_summary}
```

### 4. 实现示例

```python
import json
from datetime import datetime
from pathlib import Path

class HourlyNewsAnalyzer:
    def __init__(self, deepseek_client):
        self.client = deepseek_client
        self.news_dir = Path("news_data/hourly")
        self.news_dir.mkdir(parents=True, exist_ok=True)
    
    def search_and_analyze_news(self):
        """每小时搜索和分析新闻"""
        current_time = datetime.now()
        last_search_time = current_time.replace(
            minute=0, second=0, microsecond=0
        ) - timedelta(hours=1)
        
        # 构建prompt
        prompt = self._build_prompt(current_time, last_search_time)
        
        # 调用Deepseek
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0,
            max_tokens=4000
        )
        
        # 解析JSON
        news_data = json.loads(response.choices[0].message.content)
        
        # 存储到文件
        self._save_news(news_data, current_time)
        
        return news_data
    
    def _save_news(self, news_data, timestamp):
        """存储新闻数据"""
        filename = f"news_{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        filepath = self.news_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
        
        print(f"News saved to: {filepath}")
```

---

## 注意事项

1. **API限制**: 注意Deepseek API的调用频率限制
2. **搜索能力**: Deepseek可能需要联网搜索功能,或者需要先用搜索API获取新闻再让Deepseek分析
3. **时效性**: 确保新闻时间戳准确,避免重复分析旧新闻
4. **存储空间**: 每小时存储一次,注意磁盘空间管理
5. **错误处理**: 如果搜索失败或无新闻,应优雅处理

---

## 版本信息

- 版本: 1.0
- 创建日期: 2025-11-04
- 用途: 每小时新闻搜索与分析
