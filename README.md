# 🤖 AITrading - Deepseek AI量化交易系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![HyperLiquid](https://img.shields.io/badge/Exchange-HyperLiquid-green.svg)](https://hyperliquid.xyz/)
[![Deepseek](https://img.shields.io/badge/AI-Deepseek-orange.svg)](https://www.deepseek.com/)

> 基于Deepseek大模型的HyperLiquid去中心化交易所AI量化交易系统,参考Alpha Arena AI交易大赛设计。

---

## 📖 目录

- [项目简介](#-项目简介)
- [核心特性](#-核心特性)
- [系统架构](#️-系统架构)
- [快速开始](#-快速开始)
- [配置说明](#️-配置说明)
- [使用指南](#-使用指南)
- [部署方案](#-部署方案)
- [常见问题](#-常见问题)
- [免责声明](#️-免责声明)

---

## 🎯 项目简介

**AITrading** 是一个完整的AI驱动的加密货币量化交易系统,灵感来自于[Alpha Arena AI交易大赛](https://nof1.ai/),其中Deepseek V3.1模型取得了+76%的惊人收益。

本系统集成了:
- 🧠 **Deepseek AI决策引擎** - 使用最新的Deepseek Chat/Reasoner模型进行市场分析和交易决策
- 📊 **技术指标分析** - SMA、EMA、RSI、MACD、布林带、ATR等多种指标
- 🛡️ **完善的风险管理** - 仓位控制、杠杆管理、止损止盈机制
- ⚡ **HyperLiquid集成** - 去中心化永续合约交易所API对接
- 📈 **实时监控** - 详细的日志系统和状态报告
- 🔄 **上下文缓存** - AI记住历史交易,持续学习优化

---

## ✨ 核心特性

### 🤖 AI决策系统

- **Deepseek Chat模式** - 快速决策,适合高频交易(temperature=1.0优化)
- **Deepseek Reasoner模式** - 深度推理,提供详细的决策解释
- **上下文记忆** - AI记住所有历史交易和市场状态
- **市场消息分析** - 整合新闻和市场情绪

### 📊 技术分析

- **多种技术指标** - SMA、EMA、RSI、MACD、Bollinger Bands、ATR
- **自动状态摘要** - 智能生成市场状态描述
- **实时数据采集** - K线、价格、订单簿、账户状态

### 🛡️ 风险管理

- **仓位控制** - 单币种最大20%,总仓位最大80%
- **杠杆管理** - 可配置杠杆倍数(默认5x,最大20x)
- **止损止盈** - 自动止损(默认10%)和止盈(默认20%)
- **最大回撤限制** - 保护本金安全
- **每日亏损限制** - 防止单日巨额亏损

### ⚡ 交易执行

- **纸上交易模式** - 安全的模拟交易,无真实资金风险
- **实盘交易模式** - 连接HyperLiquid测试网/主网
- **订单管理** - 限价单、市价单、触发单支持
- **持仓跟踪** - 实时跟踪所有持仓和盈亏

---

## 🏗️ 系统架构

```
AITrading/
├── src/
│   ├── data/              # 数据采集和处理
│   │   ├── market_data.py # 市场数据采集
│   │   └── indicators.py  # 技术指标计算
│   ├── ai/                # AI决策引擎
│   │   └── deepseek_agent.py
│   ├── strategy/          # 交易策略
│   │   └── ai_strategy.py
│   ├── trading/           # 交易执行
│   │   └── executor.py
│   ├── risk/              # 风险管理
│   │   └── risk_manager.py
│   └── utils/             # 工具函数
│       ├── config_loader.py
│       └── logger.py
├── config/                # 配置文件
│   └── config.yaml
├── live_trading_system.py # 7天持续交易系统
├── main.py                # 主程序入口
├── requirements.txt       # Python依赖
└── README.md              # 本文档
```

---

## 🚀 快速开始

### 前置要求

- Python 3.11+
- pip3
- Git

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/AITrading.git
cd AITrading
```

### 2. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 3. 配置API密钥

编辑 `config/config.yaml`:

```yaml
deepseek:
  api_key: "your_deepseek_api_key_here"
  model: "deepseek-chat"  # 或 "deepseek-reasoner"
  temperature: 1.0

hyperliquid:
  testnet: true
  wallet_address: ""  # 可选,实盘需要
  private_key: ""     # 可选,实盘需要
```

### 4. 运行纸上交易

```bash
# 方式1: 使用主程序
python3 main.py --mode paper

# 方式2: 使用7天持续交易系统
python3 live_trading_system.py
```

### 5. 查看实时监控

```bash
# 实时日志流
tail -f logs/trading_bot.log
```

---

## ⚙️ 配置说明

### 核心配置 (config/config.yaml)

```yaml
# Deepseek AI配置
deepseek:
  api_key: "sk-xxxxx"
  model: "deepseek-chat"  # 或 "deepseek-reasoner"
  temperature: 1.0        # 推荐用于数据分析
  max_tokens: 1000

# HyperLiquid配置
hyperliquid:
  testnet: true           # true=测试网, false=主网
  wallet_address: ""      # 实盘必填
  private_key: ""         # 实盘必填

# 交易策略配置
strategy:
  symbols: ["BTC", "ETH", "SOL"]  # 交易币种
  initial_capital: 10000          # 初始资金(USD)
  leverage: 5                     # 杠杆倍数
  max_leverage: 20                # 最大杠杆
  
  # 仓位管理
  max_position_size: 0.2          # 单币种最大仓位(20%)
  max_total_position: 0.8         # 总仓位上限(80%)
  
  # 风险控制
  stop_loss_pct: 0.10             # 止损比例(10%)
  take_profit_pct: 0.20           # 止盈比例(20%)
  max_drawdown: 0.20              # 最大回撤(20%)
  max_daily_loss: 0.05            # 每日最大亏损(5%)
  
  # AI决策
  confidence_threshold: 0.7       # 最低置信度阈值
  use_context_cache: true         # 启用上下文缓存
  use_market_news: true           # 启用市场消息

# 系统配置
system:
  mode: "paper"                   # paper=纸上交易, live=实盘
  trade_interval: 300             # 交易间隔(秒)
  report_interval: 3600           # 报告间隔(秒)
  log_level: "INFO"               # 日志级别
```

---

## 📚 使用指南

### 纸上交易模式

**推荐用于测试和学习**,不涉及真实资金:

```bash
# 1. 配置为纸上交易模式
# config/config.yaml: system.mode = "paper"

# 2. 运行系统
python3 main.py --mode paper

# 3. 查看日志
tail -f logs/trading_bot.log
```

### 实盘交易模式

**⚠️ 警告**: 实盘交易涉及真实资金,存在亏损风险!

```bash
# 1. 配置HyperLiquid钱包
# config/config.yaml:
#   hyperliquid.testnet = false
#   hyperliquid.wallet_address = "your_address"
#   hyperliquid.private_key = "your_private_key"

# 2. 运行实盘
python3 main.py --mode live

# 3. 密切监控
tail -f logs/trading_bot.log
```

### 7天持续交易

```bash
# 1. 后台运行
nohup python3 live_trading_system.py > live_trading.log 2>&1 &

# 2. 查看进程
ps aux | grep live_trading_system.py

# 3. 实时监控
tail -f live_trading.log

# 4. 停止系统
kill -INT $(pgrep -f live_trading_system.py)
```

---

## 🌐 部署方案

### 方案1: 本地运行

**适合**: 测试和开发

```bash
# 直接运行
python3 main.py --mode paper
```

**优点**: 简单快速  
**缺点**: 需要保持电脑开机

---

### 方案2: 云服务器部署

**适合**: 生产环境,7×24小时运行

#### AWS EC2 / 阿里云ECS

```bash
# 1. SSH连接服务器
ssh -i your-key.pem ubuntu@your-server-ip

# 2. 安装依赖
sudo apt update
sudo apt install python3.11 python3-pip git -y

# 3. 克隆仓库
git clone https://github.com/YOUR_USERNAME/AITrading.git
cd AITrading

# 4. 安装Python依赖
pip3 install -r requirements.txt

# 5. 配置API密钥
nano config/config.yaml

# 6. 使用screen后台运行
screen -S trading
python3 live_trading_system.py
# Ctrl+A D detach

# 7. 重新连接
screen -r trading
```

#### Docker部署

```bash
# 1. 创建Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "live_trading_system.py"]
EOF

# 2. 构建镜像
docker build -t aitrading:latest .

# 3. 运行容器
docker run -d \
  --name aitrading \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  aitrading:latest

# 4. 查看日志
docker logs -f aitrading
```

---

### 方案3: 定时任务(Cron)

**适合**: 避免Sandbox休眠问题

```bash
# 1. 创建单次执行脚本
cat > run_once.sh << 'EOF'
#!/bin/bash
cd /path/to/AITrading
python3 -c "
from src.trading_bot import TradingBot
bot = TradingBot()
bot.run_once()
"
EOF

# 2. 添加到crontab
crontab -e

# 3. 添加定时任务(每5分钟执行一次)
*/5 * * * * /path/to/AITrading/run_once.sh >> /path/to/AITrading/logs/cron.log 2>&1
```

---

## ❓ 常见问题

### Q1: 如何获取Deepseek API密钥?

访问 [Deepseek官网](https://platform.deepseek.com/) 注册账号并创建API密钥。

### Q2: HyperLiquid测试网如何获取测试资金?

访问 [HyperLiquid Discord](https://discord.gg/hyperliquid) 申请测试网水龙头。

### Q3: 为什么AI一直选择HOLD?

可能原因:
1. 置信度阈值太高 - 降低`confidence_threshold`
2. 市场波动小 - AI认为没有明确机会
3. 已有持仓 - AI认为当前持仓合理

### Q4: 如何提高交易频率?

1. 降低置信度阈值
2. 缩短交易间隔
3. 修改AI提示词,让其更激进
4. 使用Reasoner模式

### Q5: 系统在Sandbox中会休眠吗?

是的,Manus Sandbox会自动休眠。建议:
1. 使用定时任务(cron)模式
2. 部署到真实服务器
3. 添加心跳机制

### Q6: 如何切换到实盘交易?

⚠️ **警告**: 实盘交易有风险!

1. 配置钱包地址和私钥
2. 切换到主网URL
3. 设置`system.mode = "live"`
4. 小额测试后再增加资金

---

## ⚠️ 免责声明

**重要**: 本项目仅供学习和研究使用!

1. **投资风险**: 加密货币交易存在极高风险,可能导致本金全部损失
2. **无保证**: 本系统不保证盈利,过去的表现不代表未来结果
3. **自负责任**: 使用本系统进行交易的所有后果由用户自行承担
4. **合规性**: 请确保您所在地区允许加密货币交易
5. **测试建议**: 强烈建议先在测试网和纸上交易模式充分测试

**使用本系统即表示您已理解并接受上述风险!**

---

## 📄 许可证

本项目采用 MIT License 开源协议。

---

## 🙏 致谢

- [Deepseek](https://www.deepseek.com/) - 提供强大的AI模型
- [HyperLiquid](https://hyperliquid.xyz/) - 去中心化交易平台
- [Alpha Arena](https://nof1.ai/) - AI交易大赛提供灵感

---

**Happy Trading! 🚀📈💰**
