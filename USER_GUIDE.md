# HyperLiquid AI Trading Bot - 用户指南

**版本**: 1.0.0  
**作者**: Manus AI  
**最后更新**: 2025年10月30日

---

## 目录

1. [快速开始](#快速开始)
2. [系统要求](#系统要求)
3. [安装步骤](#安装步骤)
4. [配置指南](#配置指南)
5. [运行交易机器人](#运行交易机器人)
6. [监控和管理](#监控和管理)
7. [策略调优](#策略调优)
8. [常见问题](#常见问题)
9. [最佳实践](#最佳实践)
10. [故障排除](#故障排除)

---

## 快速开始

本系统是一个基于Deepseek大模型的AI量化交易系统,能够在HyperLiquid去中心化交易所进行自动化交易。系统具备完整的市场分析、AI决策、风险管理和交易执行功能。

### 核心特性

- **AI驱动决策**: 利用Deepseek大模型分析市场并生成交易信号
- **完善风控**: 自动止损止盈、仓位控制、杠杆管理
- **技术分析**: 集成多种技术指标(RSI、MACD、布林带等)
- **纸上交易**: 支持模拟交易测试策略
- **实时监控**: 详细的日志记录和性能监控

---

## 系统要求

### 硬件要求

- **CPU**: 2核心或以上
- **内存**: 4GB RAM或以上
- **存储**: 10GB可用空间
- **网络**: 稳定的互联网连接

### 软件要求

- **操作系统**: Linux (推荐 Ubuntu 22.04), macOS, Windows
- **Python**: 3.11 或更高版本
- **pip**: 最新版本

---

## 安装步骤

### 1. 下载项目

```bash
cd /path/to/your/workspace
# 项目已在 /home/ubuntu/hyperliquid_trading_bot
```

### 2. 安装依赖

```bash
cd hyperliquid_trading_bot
pip3 install -r requirements.txt
```

如果遇到依赖安装问题,请确保已安装以下系统依赖:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev build-essential

# macOS
brew install python@3.11
```

### 3. 验证安装

运行单元测试验证安装:

```bash
pytest tests/
```

如果所有测试通过,说明安装成功。

---

## 配置指南

### 1. 复制配置文件

```bash
cp config/config.yaml config/config.yaml.local
```

### 2. 编辑配置文件

使用您喜欢的编辑器打开配置文件:

```bash
vim config/config.yaml.local
# 或
nano config/config.yaml.local
```

### 3. 必须配置的字段

#### HyperLiquid配置

```yaml
hyperliquid:
  # API URL (测试网或主网)
  api_url: "https://api.hyperliquid-testnet.xyz"  # 测试网
  # api_url: "https://api.hyperliquid.xyz"  # 主网
  
  # 您的钱包地址 (42字符十六进制格式)
  account_address: "0xYourWalletAddress"
  
  # 您的私钥 (仅实盘交易需要,请妥善保管!)
  secret_key: "YourPrivateKey"
```

**获取钱包地址和私钥**:
- 使用MetaMask或其他以太坊钱包
- 导出您的钱包地址和私钥
- ⚠️ **警告**: 私钥是您资产的唯一凭证,请务必保密!

#### Deepseek API配置

```yaml
deepseek:
  # Deepseek API密钥
  api_key: "YourDeepseekAPIKey"
  
  # 模型选择
  model: "deepseek-chat"  # 或 "deepseek-reasoner"
```

**获取Deepseek API密钥**:
1. 访问 https://platform.deepseek.com/
2. 注册账号并登录
3. 前往 https://platform.deepseek.com/api_keys
4. 创建新的API密钥
5. 充值账户(建议先充值$10-20用于测试)

### 4. 交易配置

```yaml
trading:
  # 交易币种 (建议从少量币种开始)
  trading_pairs:
    - "BTC"
    - "ETH"
    - "SOL"
  
  # 交易模式
  mode: "paper"  # paper: 模拟交易, live: 实盘交易
  
  # 初始资金
  initial_capital: 10000  # USD
  
  # 交易决策间隔
  trading_interval: 60  # 秒
```

### 5. 风险管理配置

```yaml
risk:
  # 单币种最大仓位 (占总资金比例)
  max_position_per_coin: 0.20  # 20%
  
  # 总仓位上限
  max_total_position: 0.80  # 80%
  
  # 默认杠杆
  default_leverage: 3
  
  # 最大杠杆
  max_leverage: 5
  
  # 止损比例
  stop_loss_pct: 0.05  # 5%
  
  # 止盈比例
  take_profit_pct: 0.10  # 10%
  
  # 最大回撤阈值
  max_drawdown: 0.20  # 20%
  
  # 每日最大亏损
  max_daily_loss: 0.10  # 10%
```

---

## 运行交易机器人

### 1. 纸上交易(推荐首次使用)

纸上交易模式不会进行真实交易,用于测试策略:

```bash
python3 main.py --mode paper
```

### 2. 实盘交易

⚠️ **警告**: 实盘交易涉及真实资金,请先在测试网充分测试!

```bash
# 确保已配置正确的API密钥和钱包信息
python3 main.py --mode live
```

### 3. 使用自定义配置文件

```bash
python3 main.py --config /path/to/your/config.yaml
```

### 4. 停止交易机器人

按 `Ctrl+C` 优雅停止。系统会:
1. 停止接受新的交易信号
2. 关闭所有开仓位
3. 保存交易日志
4. 显示最终统计信息

---

## 监控和管理

### 1. 查看实时日志

```bash
# 实时查看日志
tail -f logs/trading_bot.log

# 查看最近100行日志
tail -n 100 logs/trading_bot.log

# 搜索特定内容
grep "ERROR" logs/trading_bot.log
```

### 2. 日志级别

日志包含以下级别:
- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息(交易决策、订单执行等)
- **WARNING**: 警告信息(风险提示等)
- **ERROR**: 错误信息(API调用失败等)
- **CRITICAL**: 严重错误(触发风控限制等)

### 3. 性能指标

系统会定期输出以下指标:
- 当前资金
- 回撤比例
- 持仓数量
- 总仓位价值
- 交易次数

---

## 策略调优

### 1. 调整交易频率

修改配置文件中的 `trading_interval`:

```yaml
trading:
  trading_interval: 300  # 5分钟执行一次决策
```

### 2. 调整风险参数

根据您的风险承受能力调整:

```yaml
risk:
  max_position_per_coin: 0.15  # 降低单币种仓位
  default_leverage: 2          # 降低杠杆
  stop_loss_pct: 0.03          # 更严格的止损
```

### 3. 选择交易币种

根据市场情况选择流动性好的币种:

```yaml
trading:
  trading_pairs:
    - "BTC"   # 比特币
    - "ETH"   # 以太坊
    - "SOL"   # Solana
    # 添加更多币种...
```

### 4. 技术指标参数

调整技术指标参数以适应不同市场:

```yaml
strategy:
  sma_period: 30      # 增加SMA周期
  rsi_period: 21      # 调整RSI周期
  macd_fast: 8        # 调整MACD参数
  macd_slow: 21
```

---

## 常见问题

### Q1: 如何获取HyperLiquid测试网代币?

**A**: 
1. 访问HyperLiquid测试网: https://app.hyperliquid-testnet.xyz
2. 连接您的钱包
3. 使用测试网水龙头获取测试代币

### Q2: Deepseek API费用如何计算?

**A**: 
- 输入tokens (缓存命中): $0.028/百万tokens
- 输入tokens (缓存未命中): $0.28/百万tokens
- 输出tokens: $0.42/百万tokens

一般情况下,每次决策约消耗1000-2000 tokens,费用约$0.001-0.002。

### Q3: 系统支持哪些币种?

**A**: 
系统支持HyperLiquid上所有可交易的永续合约币种。默认配置了前10大币种,您可以在配置文件中自定义。

### Q4: 如何调整交易频率?

**A**: 
修改配置文件中的 `trading.trading_interval` 参数(单位:秒):
- 60: 每分钟决策一次
- 300: 每5分钟决策一次
- 3600: 每小时决策一次

### Q5: 系统如何处理网络中断?

**A**: 
系统会自动重试API调用,并记录错误日志。建议:
- 部署在稳定的网络环境
- 使用VPS或云服务器
- 配置告警通知

### Q6: 可以同时运行多个交易机器人吗?

**A**: 
可以,但需要注意:
- 使用不同的配置文件
- 避免交易相同的币种
- 确保总风险可控

### Q7: 如何备份交易数据?

**A**: 
定期备份以下目录:
```bash
# 备份日志
cp -r logs/ backup/logs_$(date +%Y%m%d)/

# 备份配置
cp config/config.yaml.local backup/config_$(date +%Y%m%d).yaml
```

---

## 最佳实践

### 1. 从小额开始

- 首次使用建议从$100-500开始
- 熟悉系统后再逐步增加资金
- 永远不要投入超过您承受能力的资金

### 2. 充分测试

- 在测试网测试至少1周
- 在纸上交易模式测试至少1周
- 确认策略表现稳定后再实盘

### 3. 风险控制

- 严格遵守止损纪律
- 不要过度使用杠杆
- 分散投资,不要全仓单一币种
- 定期检查账户状态

### 4. 监控和维护

- 每天至少检查一次日志
- 关注市场重大事件
- 及时调整策略参数
- 定期更新系统

### 5. 记录和分析

- 保存交易日志
- 定期分析交易表现
- 总结成功和失败的经验
- 持续优化策略

### 6. 安全建议

- 不要分享您的私钥和API密钥
- 使用强密码保护配置文件
- 定期更换API密钥
- 启用双因素认证(如果支持)

---

## 故障排除

### 问题1: 无法连接到HyperLiquid API

**症状**: 日志显示 "Connection error" 或 "Timeout"

**解决方案**:
1. 检查网络连接
2. 确认API URL配置正确
3. 尝试使用VPN或代理
4. 检查防火墙设置

### 问题2: Deepseek API调用失败

**症状**: 日志显示 "Authentication failed" 或 "Invalid API key"

**解决方案**:
1. 确认API密钥正确
2. 检查账户余额是否充足
3. 确认API密钥未过期
4. 重新生成API密钥

### 问题3: 订单下单失败

**症状**: 日志显示 "Order placement failed"

**可能原因和解决方案**:
- **余额不足**: 充值账户
- **订单金额过小**: 增加订单金额(最小$10)
- **杠杆超限**: 降低杠杆倍数
- **市场波动**: 调整价格或使用市价单

### 问题4: 系统频繁触发风控

**症状**: 日志显示 "Trading disabled due to risk limits"

**解决方案**:
1. 检查回撤是否超过阈值
2. 检查每日亏损是否超限
3. 调整风险参数
4. 优化交易策略

### 问题5: 技术指标计算错误

**症状**: 日志显示 "Error calculating indicators"

**解决方案**:
1. 检查历史数据是否充足
2. 确认K线数据完整
3. 调整指标参数
4. 重启系统重新加载数据

---

## 技术支持

如需进一步帮助,请:

1. 查看项目README文档
2. 检查日志文件中的错误信息
3. 访问项目GitHub Issues页面
4. 联系技术支持邮箱

---

## 免责声明

本软件仅供学习和研究使用。加密货币交易存在高风险,可能导致本金损失。使用本软件进行交易的所有风险由用户自行承担。开发者不对任何直接或间接的损失负责。

请在充分了解风险的情况下谨慎使用,不要投入超过您承受能力的资金。

---

**祝您交易顺利!** 🚀
