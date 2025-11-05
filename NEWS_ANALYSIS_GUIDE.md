# 新闻分析系统使用指南

## 📋 概述

新闻分析系统通过Deepseek AI自动搜索、分析和总结影响加密货币市场的新闻,为交易决策提供信息支持。

---

## 🎯 核心功能

### 1. 每小时新闻搜索 (Hourly News Analysis)

**功能**: 每小时搜索和分析最新新闻

**搜索类别**:
- Web3 & Blockchain News
- Financial News  
- International Affairs
- Macroeconomic News
- Bitcoin-Specific News

**输出**:
- 每条新闻的标题、摘要、来源
- 市场影响评估 (Bullish/Bearish/Neutral)
- 影响的币种
- 紧急程度 (High/Medium/Low)

**存储**: `news_data/hourly/news_2025-11-04_15-00-00.json`

---

### 2. 每24小时新闻汇总 (Daily News Summary)

**功能**: 汇总过去24小时的所有新闻,提取关键主题

**分析内容**:
- 每日综述 (1-2段落)
- Top 5-10 最重要新闻
- 关键主题和叙事
- 市场情绪演变
- 新闻之间的关联
- 战略交易建议

**存储**: `news_data/daily/daily_summary_2025-11-04.json`

---

## 🚀 快速开始

### 安装依赖

```bash
pip install openai
```

### 配置API密钥

```bash
# Linux/Mac
export DEEPSEEK_API_KEY="your_api_key_here"

# Windows
set DEEPSEEK_API_KEY=your_api_key_here
```

### 基本使用

```python
from src.news.news_analyzer import NewsAnalyzer

# 创建分析器
analyzer = NewsAnalyzer(api_key="your_deepseek_api_key")

# 每小时分析
hourly_result = analyzer.analyze_hourly_news()
print(f"Found {hourly_result['total_news_found']} news items")

# 每日汇总
daily_result = analyzer.analyze_daily_news()
print(f"Analyzed {daily_result['total_news_analyzed']} news items")
```

---

## 📁 文件结构

```
AITrading/
├── prompts/
│   ├── news_analysis_hourly.md      # 每小时新闻prompt模板
│   └── news_analysis_daily.md       # 每日汇总prompt模板
├── src/
│   └── news/
│       ├── __init__.py
│       ├── news_analyzer.py         # 新闻分析器
│       └── news_storage.py          # 存储管理器
└── news_data/                       # 新闻数据目录
    ├── hourly/                      # 每小时新闻
    ├── daily/                       # 每日汇总
    └── archive/                     # 归档数据
```

---

## 🔄 自动化运行

### 方法1: Cron Job (Linux/Mac)

```bash
# 编辑crontab
crontab -e

# 添加以下行:

# 每小时运行新闻分析 (每小时的第0分钟)
0 * * * * cd /path/to/AITrading && python -c "from src.news.news_analyzer import NewsAnalyzer; import os; NewsAnalyzer(os.getenv('DEEPSEEK_API_KEY')).analyze_hourly_news()"

# 每天00:00运行每日汇总
0 0 * * * cd /path/to/AITrading && python -c "from src.news.news_analyzer import NewsAnalyzer; import os; NewsAnalyzer(os.getenv('DEEPSEEK_API_KEY')).analyze_daily_news()"
```

### 方法2: Windows Task Scheduler

创建两个任务:

**任务1: 每小时新闻分析**
- 触发器: 每小时
- 操作: 运行Python脚本

```python
# hourly_news.py
from src.news.news_analyzer import NewsAnalyzer
import os

api_key = os.getenv('DEEPSEEK_API_KEY')
analyzer = NewsAnalyzer(api_key)
analyzer.analyze_hourly_news()
```

**任务2: 每日新闻汇总**
- 触发器: 每天00:00
- 操作: 运行Python脚本

```python
# daily_news.py
from src.news.news_analyzer import NewsAnalyzer
import os

api_key = os.getenv('DEEPSEEK_API_KEY')
analyzer = NewsAnalyzer(api_key)
analyzer.analyze_daily_news()
```

### 方法3: 集成到交易系统

```python
# 在main.py中添加
from src.news.news_analyzer import NewsAnalyzer
from datetime import datetime

# 初始化
news_analyzer = NewsAnalyzer(api_key=config['deepseek']['api_key'])

# 在主循环中
while True:
    current_time = datetime.now()
    
    # 每小时执行一次新闻分析
    if current_time.minute == 0:
        try:
            news_analyzer.analyze_hourly_news()
        except Exception as e:
            logger.error(f"Hourly news analysis failed: {e}")
    
    # 每天00:00执行每日汇总
    if current_time.hour == 0 and current_time.minute == 0:
        try:
            news_analyzer.analyze_daily_news()
        except Exception as e:
            logger.error(f"Daily news analysis failed: {e}")
    
    # 继续交易逻辑...
    time.sleep(60)  # 每分钟检查一次
```

---

## 🔗 与交易系统集成

### 在交易决策中使用新闻

```python
from src.news.news_analyzer import NewsAnalyzer

# 创建分析器
news_analyzer = NewsAnalyzer(api_key="your_api_key")

# 获取最新新闻摘要
latest_news = news_analyzer.get_latest_news_summary()

# 获取每日汇总
daily_summary = news_analyzer.get_daily_news_summary()

# 添加到交易决策prompt
trading_prompt = f"""
{market_data}

{latest_news}

{daily_summary}

Based on the above market data and news, what trading decisions should be made?
"""

# 发送给Deepseek进行决策
response = deepseek_client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": trading_prompt}
    ]
)
```

---

## 📊 数据格式

### Hourly News JSON格式

```json
{
  "search_time": "2025-11-04 15:00:00",
  "search_period": "past_1_hour",
  "total_news_found": 5,
  "news_items": [
    {
      "title": "Federal Reserve Holds Interest Rates Steady",
      "category": "Macro",
      "summary": "Fed maintains rates at 5.25-5.50%...",
      "source": "Reuters",
      "timestamp": "2025-11-04 14:30:00",
      "url": "https://...",
      "market_impact": "Bearish",
      "impact_reasoning": "Higher rates pressure risk assets",
      "affected_coins": ["BTC", "ETH", "SOL"],
      "urgency": "High"
    }
  ],
  "market_sentiment_summary": "Mixed sentiment...",
  "key_themes": ["Fed hawkishness", "Institutional adoption"],
  "trading_implications": "Watch Bitcoin support levels..."
}
```

### Daily Summary JSON格式

```json
{
  "analysis_time": "2025-11-05 00:00:00",
  "period_start": "2025-11-04 00:00:00",
  "period_end": "2025-11-05 00:00:00",
  "total_news_analyzed": 87,
  "daily_summary": {
    "overview": "The past 24 hours were dominated by...",
    "market_narrative": "Institutional demand vs. Macro headwinds",
    "sentiment_evolution": "Started bearish, ended cautiously bullish"
  },
  "top_important_news": [...],
  "key_themes": [...],
  "market_sentiment": {...},
  "interconnections": [...],
  "strategic_implications": {...},
  "statistics": {...}
}
```

---

## 🛠️ 高级功能

### 1. 存储管理

```python
from src.news.news_storage import NewsStorage

storage = NewsStorage()

# 获取存储统计
stats = storage.get_storage_stats()
print(f"Total size: {stats['total_size_mb']:.2f} MB")

# 归档旧数据 (保留最近7天)
storage.archive_old_news(days_to_keep=7)

# 清理存储空间 (限制1GB)
storage.cleanup_storage(max_size_mb=1000)
```

### 2. 获取历史新闻

```python
from datetime import datetime, timedelta

# 获取特定时间的新闻
news = storage.get_hourly_news(datetime(2025, 11, 4, 15, 0, 0))

# 获取时间范围内的所有新闻
start = datetime.now() - timedelta(hours=24)
end = datetime.now()
news_list = storage.get_hourly_news_range(start, end)

# 获取最新新闻
latest = storage.get_latest_hourly_news()
```

### 3. 自定义Prompt

如果需要修改prompt,编辑以下文件:
- `prompts/news_analysis_hourly.md` - 每小时prompt
- `prompts/news_analysis_daily.md` - 每日汇总prompt

然后在代码中更新对应的SYSTEM_PROMPT。

---

## ⚠️ 注意事项

### 1. API限制

- Deepseek API有调用频率限制
- 每小时分析消耗约2000-4000 tokens
- 每日汇总消耗约4000-8000 tokens
- 注意不要超过API配额

### 2. 搜索能力

- Deepseek可能需要联网搜索功能
- 如果Deepseek无法直接搜索,需要:
  1. 先用搜索API (如Google News API, CryptoPanic API)获取新闻
  2. 再让Deepseek分析和总结

### 3. 数据质量

- AI生成的新闻分析可能不完全准确
- 建议人工审核重要决策
- 将新闻作为参考,而非唯一依据

### 4. 存储空间

- 每小时存储一次,每天24个文件
- 每月约720个hourly文件 + 30个daily文件
- 建议定期归档或清理旧数据

---

## 📈 性能优化

### 1. 并行处理

如果需要加速,可以并行处理多个小时的新闻:

```python
from concurrent.futures import ThreadPoolExecutor

def analyze_multiple_hours(hours_list):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(analyzer.analyze_hourly_news, hours_list)
    return list(results)
```

### 2. 缓存

缓存最近的新闻摘要,避免重复读取文件:

```python
from functools import lru_cache

@lru_cache(maxsize=10)
def get_cached_news_summary():
    return analyzer.get_latest_news_summary()
```

### 3. 异步处理

使用异步IO避免阻塞主程序:

```python
import asyncio

async def async_hourly_analysis():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, analyzer.analyze_hourly_news)
    return result
```

---

## 🐛 故障排查

### 问题1: API调用失败

```python
# 检查API密钥
import os
print(os.getenv('DEEPSEEK_API_KEY'))

# 测试API连接
from openai import OpenAI
client = OpenAI(api_key="your_key", base_url="https://api.deepseek.com")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

### 问题2: JSON解析错误

Deepseek可能返回非JSON格式的内容,需要处理:

```python
import re
import json

def extract_json(text):
    # 尝试提取JSON部分
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON found in response")
```

### 问题3: 存储空间不足

```python
# 检查存储使用情况
stats = storage.get_storage_stats()
print(f"Total size: {stats['total_size_mb']:.2f} MB")

# 清理旧数据
storage.archive_old_news(days_to_keep=3)
storage.cleanup_storage(max_size_mb=500)
```

---

## 📞 技术支持

如有问题,请查看:
1. `prompts/news_analysis_hourly.md` - Hourly prompt文档
2. `prompts/news_analysis_daily.md` - Daily prompt文档
3. `src/news/news_analyzer.py` - 源代码
4. GitHub Issues: https://github.com/AnakinRM/AITrading/issues

---

## 📝 更新日志

### Version 1.0 (2025-11-04)
- ✅ 初始版本
- ✅ 每小时新闻搜索
- ✅ 每24小时新闻汇总
- ✅ 完整的存储管理
- ✅ 与交易系统集成

---

**祝您使用愉快!** 📰🤖💰
