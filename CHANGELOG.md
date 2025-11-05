# 更新日志 (Changelog)

## [v2.0.0] - 2025-11-05

### ✨ 新增功能

#### 📰 新闻集成系统
- **新增**: `src/news/news_analyzer.py` - 新闻分析器模块
- **新增**: `src/news/news_storage.py` - 新闻存储模块
- **新增**: 双重时间框架新闻分析
  - 今日每小时新闻更新
  - 过去7天每日新闻摘要
- **新增**: 事件驱动交易决策能力

#### 🤖 AI决策增强
- **更新**: `src/ai/deepseek_trading_agent.py` - 集成新闻分析
- **优化**: Trading prompt结构,采用nof1.ai风格
- **新增**: 4-section prompt设计:
  - Section 1: NEWS CONTEXT
  - Section 2: MARKET DATA
  - Section 3: ACCOUNT INFORMATION
  - Section 4: YOUR TRADING DECISION
- **新增**: 5步决策框架

### 📚 文档更新
- **更新**: `README.md` - 添加新闻集成功能说明
- **新增**: `NEWS_INTEGRATION_GUIDE.md` - 详细使用指南
- **新增**: `CHANGELOG.md` - 本文档

### 🛠️ 技术改进
- **优化**: Prompt token效率,新闻内容约3000 tokens
- **新增**: 新闻数据持久化存储
- **新增**: 格式化方法用于prompt注入
- **改进**: 错误处理和fallback机制

### 🧹 代码清理
- **删除**: 所有测试文件和临时文件
- **优化**: 项目结构更清晰

---

## [v1.0.0] - 2025-10-30

### 初始版本
- 基础AI交易系统
- Deepseek集成
- HyperLiquid交易所对接
- 技术指标分析
- 风险管理系统
- 纸上交易和实盘模式

---

**版本说明**:
- v2.0.0: 新闻集成重大更新
- v1.0.0: 初始发布版本
