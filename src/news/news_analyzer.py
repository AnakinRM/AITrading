"""
新闻分析器

集成每小时新闻搜索和每24小时汇总功能
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from openai import OpenAI

from .news_storage import NewsStorage

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """新闻分析器 - 集成hourly和daily分析"""
    
    # System prompts
    HOURLY_SYSTEM_PROMPT = """You are a professional cryptocurrency market news analyst and researcher. Your task is to search, analyze, and summarize the latest news that may impact cryptocurrency prices, especially Bitcoin and other major cryptocurrencies (ETH, SOL, BNB, XRP, DOGE).

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
- Consider both direct and indirect impacts on crypto"""
    
    DAILY_SYSTEM_PROMPT = """You are a senior cryptocurrency market analyst specializing in synthesizing large amounts of news data into actionable insights. Your task is to review all news collected over the past 24 hours, identify key themes, and highlight the most important developments that could impact cryptocurrency markets.

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
- Be objective and balanced in assessment"""
    
    def __init__(self, api_key: str, storage_dir: str = "news_data"):
        """
        初始化新闻分析器
        
        Args:
            api_key: Deepseek API密钥
            storage_dir: 新闻数据存储目录
        """
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.storage = NewsStorage(storage_dir)
        logger.info("NewsAnalyzer initialized")
    
    def analyze_hourly_news(self) -> Dict:
        """
        每小时新闻搜索和分析
        
        Returns:
            新闻分析结果字典
        """
        current_time = datetime.now()
        last_search_time = current_time - timedelta(hours=1)
        
        logger.info(f"Starting hourly news analysis at {current_time}")
        
        # 构建prompt
        prompt = self._build_hourly_prompt(current_time, last_search_time)
        
        try:
            # 调用Deepseek
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.HOURLY_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                max_tokens=4000
            )
            
            # 解析JSON
            content = response.choices[0].message.content
            news_data = json.loads(content)
            
            # 保存到存储
            self.storage.save_hourly_news(news_data, current_time)
            
            logger.info(f"Hourly news analysis completed: {news_data.get('total_news_found', 0)} news items found")
            return news_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content: {content}")
            raise
        except Exception as e:
            logger.error(f"Error in hourly news analysis: {e}")
            raise
    
    def analyze_daily_news(self) -> Dict:
        """
        每24小时新闻汇总和分析
        
        Returns:
            每日汇总结果字典
        """
        current_time = datetime.now()
        start_time = current_time - timedelta(hours=24)
        end_time = current_time
        
        logger.info(f"Starting daily news analysis at {current_time}")
        
        # 收集过去24小时的所有新闻
        all_hourly_news = self.storage.get_hourly_news_range(start_time, end_time)
        
        if not all_hourly_news:
            logger.warning("No hourly news data found for past 24 hours")
            return {
                "error": "No data available",
                "analysis_time": current_time.isoformat()
            }
        
        # 构建prompt
        prompt = self._build_daily_prompt(current_time, start_time, end_time, all_hourly_news)
        
        try:
            # 调用Deepseek
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.DAILY_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                max_tokens=8000
            )
            
            # 解析JSON
            content = response.choices[0].message.content
            daily_summary = json.loads(content)
            
            # 保存到存储
            self.storage.save_daily_summary(daily_summary, current_time)
            
            logger.info(f"Daily news analysis completed: {daily_summary.get('total_news_analyzed', 0)} news items analyzed")
            return daily_summary
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content: {content}")
            raise
        except Exception as e:
            logger.error(f"Error in daily news analysis: {e}")
            raise
    
    def _build_hourly_prompt(self, current_time: datetime, last_search_time: datetime) -> str:
        """构建hourly prompt"""
        return f"""Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
Last Search: {last_search_time.strftime('%Y-%m-%d %H:%M:%S')} (1 hour ago)

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

{{
  "search_time": "{current_time.strftime('%Y-%m-%d %H:%M:%S')}",
  "search_period": "past_1_hour",
  "total_news_found": 0,
  "news_items": [
    {{
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
    }}
  ],
  "market_sentiment_summary": "Overall market sentiment based on news",
  "key_themes": ["Theme 1", "Theme 2", "Theme 3"],
  "trading_implications": "Brief note on what traders should watch"
}}

IMPORTANT:
- If no significant news found, return empty news_items array
- Focus on NEWS that could move markets, not routine updates
- Prioritize breaking news and major developments
- Be objective and fact-based in your analysis"""
    
    def _build_daily_prompt(self, current_time: datetime, start_time: datetime, 
                           end_time: datetime, all_hourly_news: List[Dict]) -> str:
        """构建daily prompt"""
        # 统计总新闻数
        total_news_count = sum(
            len(news.get('news_items', [])) 
            for news in all_hourly_news
        )
        
        # 格式化所有hourly news数据
        hourly_data_str = "\n\n".join([
            f"=== Hour {i+1}: {news.get('search_time', 'Unknown')} ===\n" +
            f"News found: {news.get('total_news_found', 0)}\n" +
            f"Sentiment: {news.get('market_sentiment_summary', 'N/A')}\n" +
            f"Key themes: {', '.join(news.get('key_themes', []))}\n" +
            f"News items:\n" +
            json.dumps(news.get('news_items', []), indent=2)
            for i, news in enumerate(all_hourly_news)
        ])
        
        return f"""Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
Analysis Period: Past 24 Hours ({start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')})

Below is ALL the news collected over the past 24 hours through hourly searches. Each entry represents one hour's worth of news analysis.

TOTAL NEWS ITEMS: {total_news_count}
HOURLY REPORTS: {len(all_hourly_news)}

===== 24-HOUR NEWS DATA =====

{hourly_data_str}

===== YOUR TASK =====

Please analyze ALL the news above and provide a comprehensive 24-hour summary following the structure in the system prompt.

Focus on:
1. Daily Summary (1-2 paragraphs)
2. Top 5-10 Most Important News
3. Key Themes (3-5 major themes)
4. Market Sentiment Evolution
5. Interconnections between events
6. Strategic Implications for next 24 hours

Output in valid JSON format as specified in the system prompt."""
    
    def get_latest_news_summary(self) -> Optional[str]:
        """
        获取最新新闻摘要,用于添加到交易决策prompt
        
        Returns:
            新闻摘要字符串
        """
        # 获取最新hourly news
        hourly = self.storage.get_latest_hourly_news()
        
        if not hourly:
            return None
        
        summary = f"""===== LATEST NEWS SUMMARY (Past 1 Hour) =====
Search Time: {hourly.get('search_time', 'Unknown')}
News Found: {hourly.get('total_news_found', 0)}

Market Sentiment: {hourly.get('market_sentiment_summary', 'N/A')}

Key Themes: {', '.join(hourly.get('key_themes', []))}

Trading Implications: {hourly.get('trading_implications', 'N/A')}

Top News Items:
"""
        
        for i, item in enumerate(hourly.get('news_items', [])[:5], 1):
            summary += f"\n{i}. [{item.get('category', 'Unknown')}] {item.get('title', 'No title')}"
            summary += f"\n   Impact: {item.get('market_impact', 'N/A')} | Urgency: {item.get('urgency', 'N/A')}"
            summary += f"\n   {item.get('summary', 'No summary')}\n"
        
        return summary
    
    def get_daily_news_summary(self) -> Optional[str]:
        """
        获取每日新闻汇总,用于添加到交易决策prompt
        
        Returns:
            每日汇总字符串
        """
        # 获取最新daily summary
        daily = self.storage.get_latest_daily_summary()
        
        if not daily:
            return None
        
        daily_summary_data = daily.get('daily_summary', {})
        
        summary = f"""===== 24-HOUR NEWS SUMMARY =====
Analysis Time: {daily.get('analysis_time', 'Unknown')}
Total News Analyzed: {daily.get('total_news_analyzed', 0)}

DAILY OVERVIEW:
{daily_summary_data.get('overview', 'N/A')}

MARKET NARRATIVE:
{daily_summary_data.get('market_narrative', 'N/A')}

SENTIMENT EVOLUTION:
{daily_summary_data.get('sentiment_evolution', 'N/A')}

TOP IMPORTANT NEWS:
"""
        
        for item in daily.get('top_important_news', [])[:5]:
            summary += f"\n{item.get('rank', '?')}. [{item.get('category', 'Unknown')}] {item.get('title', 'No title')}"
            summary += f"\n   Impact: {item.get('market_impact', 'N/A')} | Timeframe: {item.get('impact_timeframe', 'N/A')}"
            summary += f"\n   Why Important: {item.get('importance_reasoning', 'N/A')}\n"
        
        # 添加key themes
        summary += "\nKEY THEMES:\n"
        for theme in daily.get('key_themes', [])[:3]:
            summary += f"- {theme.get('theme', 'Unknown')}: {theme.get('description', 'N/A')}\n"
        
        # 添加strategic implications
        implications = daily.get('strategic_implications', {})
        summary += f"\nSTRATEGIC IMPLICATIONS:\n"
        summary += f"Next 24h Focus: {', '.join(implications.get('next_24h_focus', []))}\n"
        summary += f"Key Risks: {', '.join(implications.get('key_risks', []))}\n"
        summary += f"Key Opportunities: {', '.join(implications.get('key_opportunities', []))}\n"
        
        return summary
    
    def format_today_hourly_news_for_prompt(self) -> str:
        """
        格式化今天所有hourly news为trading prompt格式
        
        Returns:
            格式化的新闻文本,用于注入到trading prompt
        """
        today_news = self.storage.get_today_hourly_news()
        
        if not today_news:
            return "No hourly news available for today."
        
        result = []
        
        for i, hour_data in enumerate(today_news, 1):
            if not isinstance(hour_data, dict):
                continue
            hour_text = f"""Hour {i}: {hour_data.get('search_time', 'Unknown')}
Total News: {hour_data.get('total_news_found', 0)}
Market Sentiment: {hour_data.get('market_sentiment_summary', 'N/A')}
Key Themes: {', '.join(hour_data.get('key_themes', []))}

News Items:"""
            
            news_items = hour_data.get('news_items', [])
            if news_items:
                for j, news in enumerate(news_items, 1):
                    news_text = f"""
{j}. [{news.get('category', 'Unknown')}] {news.get('title', 'No title')} - Impact: {news.get('market_impact', 'N/A')} | Urgency: {news.get('urgency', 'N/A')}
   Summary: {news.get('summary', 'No summary')}
   Affected Coins: {', '.join(news.get('affected_coins', []))}"""
                    hour_text += news_text
            else:
                hour_text += "\nNo significant news found for this hour."
            
            hour_text += f"\n\nTrading Implications: {hour_data.get('trading_implications', 'N/A')}"
            result.append(hour_text)
        
        return "\n\n---\n\n".join(result)
    
    def format_past_n_days_summaries_for_prompt(self, n: int = 7) -> str:
        """
        格式化过去N天的daily summaries为trading prompt格式
        
        Args:
            n: 天数,默认7天
            
        Returns:
            格式化的汇总文本,用于注入到trading prompt
        """
        summaries = self.storage.get_past_n_days_summaries(n)
        
        if not summaries:
            return f"No daily summaries available for past {n} days."
        
        result = []
        
        for i, day_data in enumerate(summaries, 1):
            if not isinstance(day_data, dict):
                continue
            metadata = day_data.get('_metadata', {})
            date = metadata.get('date', 'Unknown')
            
            daily_summary = day_data.get('daily_summary', {})
            
            day_text = f"""Day {i}: {date}
Total News Analyzed: {day_data.get('total_news_analyzed', 0)}

Daily Overview:
{daily_summary.get('overview', 'N/A')}

Market Narrative:
{daily_summary.get('market_narrative', 'N/A')}

Top 5 Important News:"""
            
            top_news = day_data.get('top_important_news', [])[:5]
            for j, news in enumerate(top_news, 1):
                news_text = f"""
{j}. [{news.get('category', 'Unknown')}] {news.get('title', 'No title')} - Impact: {news.get('market_impact', 'N/A')}
   Why Important: {news.get('importance_reasoning', 'N/A')}"""
                day_text += news_text
            
            # 添加key themes
            themes = day_data.get('key_themes', [])[:3]
            if themes:
                day_text += "\n\nKey Themes:"
                for theme in themes:
                    day_text += f"\n- {theme.get('theme', 'Unknown')}: {theme.get('description', 'N/A')}"
            
            # 添加strategic implications
            implications = day_data.get('strategic_implications', {})
            day_text += f"""

Strategic Implications:
- Next 24h Focus: {', '.join(implications.get('next_24h_focus', []))}
- Key Risks: {', '.join(implications.get('key_risks', []))}
- Key Opportunities: {', '.join(implications.get('key_opportunities', []))}

Sentiment Evolution:
{daily_summary.get('sentiment_evolution', 'N/A')}"""
            
            result.append(day_text)
        
        return "\n\n---\n\n".join(result)


# 使用示例
if __name__ == "__main__":
    import os
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 从环境变量获取API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        logger.error("DEEPSEEK_API_KEY not found in environment variables")
        exit(1)
    
    # 创建分析器
    analyzer = NewsAnalyzer(api_key)
    
    # 示例: 每小时分析
    print("Running hourly news analysis...")
    hourly_result = analyzer.analyze_hourly_news()
    print(f"Found {hourly_result.get('total_news_found', 0)} news items")
    
    # 示例: 获取新闻摘要
    summary = analyzer.get_latest_news_summary()
    if summary:
        print("\n" + summary)
    
    # 示例: 每日分析 (如果有24小时数据)
    # daily_result = analyzer.analyze_daily_news()
    # print(f"Analyzed {daily_result.get('total_news_analyzed', 0)} news items")
