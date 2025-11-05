# 📰 新闻集成使用指南

本文档详细说明如何在AITrading系统中使用新闻集成功能,实现事件驱动的AI交易决策。

---

## 📋 目录

- [功能概述](#功能概述)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [工作原理](#工作原理)
- [常见问题](#常见问题)

---

## 功能概述

新闻集成功能为AITrading系统提供了**事件驱动交易**的能力。系统现在可以:

1. **自动获取新闻**: 从多个来源收集加密货币相关新闻
2. **智能分析**: 使用Deepseek AI分析新闻的市场影响
3. **双重时间框架**: 
   - **今日每小时新闻**: 捕捉短期市场动态
   - **过去7天每日摘要**: 理解中期市场趋势
4. **注入交易决策**: 将新闻分析结果直接注入到AI的交易决策prompt中

---

## 系统架构

新闻集成模块的核心组件:

```
src/news/
├── news_analyzer.py    # 新闻分析器 - 负责获取、分析新闻
└── news_storage.py     # 新闻存储 - 负责存储和检索新闻数据

news_data/              # 新闻数据存储目录
├── hourly/             # 每小时新闻
│   └── YYYY-MM-DD/
│       └── HH.json
└── daily/              # 每日摘要
    └── YYYY-MM-DD.json
```

**工作流程**:

```
NewsAnalyzer → 获取新闻 → 分析影响 → NewsStorage → 存储
                                              ↓
DeepseekTradingAgent ← 格式化新闻 ← 检索新闻 ←┘
         ↓
    构建Prompt → Deepseek API → 交易决策
```

---

## 快速开始

### 1. 启用新闻集成

编辑 `config/config.yaml`:

```yaml
news:
  enabled: true                   # 启用新闻集成
  news_data_dir: "news_data"      # 新闻数据存储目录
```

### 2. 初始化新闻分析器

在您的交易系统中,新闻分析器会自动初始化:

```python
from src.news.news_analyzer import NewsAnalyzer
from src.ai.deepseek_trading_agent import DeepseekTradingAgent

# 初始化NewsAnalyzer
news_analyzer = NewsAnalyzer(
    api_key="your_deepseek_api_key",
    news_data_dir="news_data"
)

# 初始化DeepseekTradingAgent并传入NewsAnalyzer
agent = DeepseekTradingAgent(
    config=deepseek_config,
    news_analyzer=news_analyzer  # 传入新闻分析器
)
```

### 3. 运行交易系统

新闻集成会自动工作,无需额外操作:

```bash
python3 main.py --mode paper
```

---

## 配置说明

### 完整配置示例

```yaml
# config/config.yaml

# Deepseek AI配置
deepseek:
  api_key: "sk-xxxxx"
  model: "deepseek-chat"
  temperature: 1.0
  max_tokens: 4000              # 建议增加到4000以容纳新闻内容

# 新闻集成配置
news:
  enabled: true                 # true=启用, false=禁用
  news_data_dir: "news_data"    # 新闻数据存储目录
```

### 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `news.enabled` | boolean | `true` | 是否启用新闻集成功能 |
| `news.news_data_dir` | string | `"news_data"` | 新闻数据存储目录路径 |
| `deepseek.max_tokens` | integer | `4000` | 建议增加以容纳新闻内容 |

---

## 使用方法

### 方法1: 自动模式(推荐)

当`news.enabled: true`时,系统会自动:

1. 在每次交易决策时获取最新新闻
2. 格式化新闻数据
3. 注入到AI的trading prompt中
4. AI基于新闻+市场数据做出决策

**无需任何额外代码!**

### 方法2: 手动调用(高级用户)

如果您需要手动控制新闻分析流程:

```python
from src.news.news_analyzer import NewsAnalyzer

# 初始化
analyzer = NewsAnalyzer(api_key="your_key", news_data_dir="news_data")

# 获取今天的hourly news
today_news = analyzer.format_today_hourly_news_for_prompt()
print(today_news)

# 获取过去7天的daily summaries
past_7_days = analyzer.format_past_n_days_summaries_for_prompt(7)
print(past_7_days)
```

---

## 工作原理

### 1. 新闻数据格式

#### Hourly News (每小时新闻)

```json
{
  "search_time": "2025-11-04 09:00:00",
  "search_period": "past_1_hour",
  "total_news_found": 3,
  "news_items": [
    {
      "title": "Fed Holds Rates Steady",
      "category": "Macro",
      "summary": "Federal Reserve maintains interest rates...",
      "market_impact": "Bearish",
      "affected_coins": ["BTC", "ETH", "SOL"],
      "urgency": "High"
    }
  ],
  "market_sentiment_summary": "Mixed - Fed hawkishness offset by...",
  "trading_implications": "Watch BTC support at $100K..."
}
```

#### Daily Summary (每日摘要)

```json
{
  "analysis_time": "2025-11-03 23:59:59",
  "total_news_analyzed": 87,
  "daily_summary": {
    "overview": "Market was dominated by conflicting signals...",
    "market_narrative": "Institutional demand vs. macro headwinds",
    "sentiment_evolution": "Started bearish, shifted to cautiously bullish..."
  },
  "top_important_news": [
    {
      "rank": 1,
      "category": "Bitcoin",
      "title": "Record $500M Single-Day ETF Inflow",
      "market_impact": "Bullish",
      "importance_reasoning": "Largest single-day inflow since ETF launch..."
    }
  ],
  "strategic_implications": {
    "next_24h_focus": ["CPI data release", "ETF flow data"],
    "key_risks": ["Fed hawkish surprise"],
    "key_opportunities": ["Dip buying on strong support levels"]
  }
}
```

### 2. Prompt结构

新闻集成后的trading prompt采用nof1.ai风格,分为4个section:

```
═══════════════════════════════════════════════════════════════
SECTION 1: NEWS CONTEXT
═══════════════════════════════════════════════════════════════

1A. TODAY'S HOURLY NEWS UPDATES
[今天每小时新闻,按时间倒序]

1B. PAST 7 DAYS DAILY NEWS SUMMARIES
[过去7天每日摘要,按日期倒序]

═══════════════════════════════════════════════════════════════
SECTION 2: MARKET DATA
═══════════════════════════════════════════════════════════════

[最新价格、技术指标等]

═══════════════════════════════════════════════════════════════
SECTION 3: ACCOUNT INFORMATION
═══════════════════════════════════════════════════════════════

[当前持仓、订单状态等]

═══════════════════════════════════════════════════════════════
SECTION 4: YOUR TRADING DECISION
═══════════════════════════════════════════════════════════════

STEP 1: NEWS UPDATE CHECK
1. Has any new news emerged since your last decision?
2. Does any new news contradict your current positions?
3. Are there new catalysts that create opportunities?

STEP 2: POSITION REVIEW
[基于新闻和市场数据评估持仓]

STEP 3: NEW OPPORTUNITIES
[基于新闻发现新机会]

STEP 4: RISK MANAGEMENT
[基于新闻评估风险]

STEP 5: OUTPUT
[输出JSON格式的交易决策]
```

### 3. AI决策流程

```
1. AI首先阅读NEWS CONTEXT
   ↓
2. 理解最新的市场事件和趋势
   ↓
3. 结合MARKET DATA分析技术面
   ↓
4. 评估ACCOUNT INFORMATION中的持仓
   ↓
5. 按照5步框架做出决策
   ↓
6. 输出JSON格式的交易计划
```

---

## 常见问题

### Q1: 新闻数据从哪里来?

目前系统支持通过`NewsAnalyzer`从多个来源获取新闻。您需要:
1. 配置Deepseek API密钥用于新闻分析
2. 系统会自动搜索和分析相关新闻

### Q2: 如何禁用新闻集成?

在`config/config.yaml`中设置:

```yaml
news:
  enabled: false
```

系统将退回至仅依赖技术指标的模式。

### Q3: 新闻数据会占用多少存储空间?

- 每小时新闻: ~5-10 KB
- 每日摘要: ~20-30 KB
- 一个月数据: ~10-15 MB

建议定期清理超过30天的旧数据。

### Q4: 新闻分析会增加API成本吗?

是的,新闻集成会增加Deepseek API的调用:
1. **新闻分析**: 每次搜索新闻时调用
2. **Trading决策**: Prompt更长,token消耗增加约30%

建议监控API使用量。

### Q5: 如何查看新闻数据?

新闻数据以JSON格式存储在`news_data/`目录:

```bash
# 查看今天的hourly news
cat news_data/hourly/2025-11-04/09.json | jq .

# 查看昨天的daily summary
cat news_data/daily/2025-11-03.json | jq .
```

### Q6: 可以自定义新闻来源吗?

是的!您可以修改`src/news/news_analyzer.py`中的新闻搜索逻辑,添加自定义的新闻源。

### Q7: 新闻集成对交易性能有提升吗?

根据Alpha Arena比赛结果,结合新闻的AI交易策略通常表现更好,因为:
1. 能够捕捉事件驱动的价格波动
2. 避免在重大新闻前后盲目交易
3. 更好地理解市场情绪变化

但具体效果取决于市场环境和AI模型的理解能力。

---

## 最佳实践

1. **定期检查新闻数据**: 确保新闻分析正常工作
2. **监控API使用**: 新闻集成会增加API调用
3. **调整max_tokens**: 建议设置为4000以容纳新闻内容
4. **结合回测**: 在纸上交易模式充分测试后再实盘
5. **关注日志**: 查看`logs/trading_bot.log`了解新闻集成状态

---

## 技术支持

如有问题,请查看:
- 主README文档: `README.md`
- 系统日志: `logs/trading_bot.log`
- 源代码: `src/news/`

---

**祝您交易顺利! 📈🚀**
