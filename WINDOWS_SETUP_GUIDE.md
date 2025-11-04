# Windows系统运行指南

本指南将帮助您在Windows系统上运行AITrading量化交易系统。

---

## 📋 系统要求

- **操作系统**: Windows 10/11 (64位)
- **Python版本**: Python 3.8 或更高版本
- **内存**: 至少 4GB RAM
- **网络**: 稳定的互联网连接

---

## 🚀 快速开始 (5分钟)

### 步骤1: 安装Python

1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.11 或 3.12 (推荐)
3. 运行安装程序
4. ⚠️ **重要**: 勾选 "Add Python to PATH"
5. 点击 "Install Now"

**验证安装**:
```cmd
python --version
```
应该显示: `Python 3.11.x` 或更高

---

### 步骤2: 下载代码

**方法A: 使用Git (推荐)**

1. 安装Git: https://git-scm.com/download/win
2. 打开命令提示符 (Win+R, 输入 `cmd`)
3. 运行:
```cmd
cd C:\Users\你的用户名\Desktop
git clone https://github.com/AnakinRM/AITrading.git
cd AITrading
```

**方法B: 直接下载ZIP**

1. 访问 https://github.com/AnakinRM/AITrading
2. 点击绿色 "Code" 按钮
3. 选择 "Download ZIP"
4. 解压到桌面或任意目录
5. 打开命令提示符,进入解压目录:
```cmd
cd C:\Users\你的用户名\Desktop\AITrading-master
```

---

### 步骤3: 安装依赖

在AITrading目录下运行:

```cmd
pip install -r requirements.txt
```

**如果遇到权限问题**:
```cmd
pip install --user -r requirements.txt
```

**如果pip不可用**:
```cmd
python -m pip install -r requirements.txt
```

---

### 步骤4: 配置系统

#### 4.1 复制配置文件

```cmd
copy config\config.yaml config\my_config.yaml
```

#### 4.2 编辑配置文件

使用记事本或VSCode打开 `config\my_config.yaml`:

```cmd
notepad config\my_config.yaml
```

**必须修改的配置**:

```yaml
# Deepseek API配置
deepseek:
  api_key: "sk-你的Deepseek API密钥"  # ⚠️ 必填!
  api_url: "https://api.deepseek.com"
  model: "deepseek-chat"
  temperature: 1.0

# HyperLiquid配置
hyperliquid:
  api_url: "https://api.hyperliquid-testnet.xyz"  # 测试网
  # api_url: "https://api.hyperliquid.xyz"  # 正式网
  wallet_address: "你的钱包地址"  # 可选,实盘交易需要
  private_key: "你的私钥"  # ⚠️ 实盘交易必填,测试可不填

# 交易配置
trading:
  mode: "paper"  # paper=模拟交易, live=实盘交易
  trading_pairs:
    - "XRP"
    - "DOGE"
    - "BTC"
    - "ETH"
    - "SOL"
    - "BNB"
  trade_interval: 300  # 5分钟交易一次
  initial_capital: 10000  # 初始资金 $10,000

# 风险管理
risk:
  max_position_size: 0.4  # 单币种最大仓位40%
  max_leverage: 20  # 最大杠杆20x
  stop_loss_pct: 0.1  # 止损10%
  take_profit_pct: 0.2  # 止盈20%
```

**获取Deepseek API密钥**:
1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的API密钥
5. 复制密钥到配置文件

---

### 步骤5: 运行系统

#### 5.1 模拟交易 (推荐先运行这个!)

```cmd
python main.py --config config\my_config.yaml --mode paper
```

**或者使用默认配置**:
```cmd
python main.py --mode paper
```

#### 5.2 实盘交易 (谨慎!)

⚠️ **警告**: 实盘交易涉及真实资金,请确保:
- 已充分测试模拟交易
- 理解所有风险
- 配置了正确的止损止盈

```cmd
python main.py --config config\my_config.yaml --mode live
```

---

## 📊 运行效果

系统启动后,您会看到:

```
2025-11-03 10:00:00 [INFO] Starting HyperLiquid AI Trading Bot...
2025-11-03 10:00:01 [INFO] Trading mode: paper
2025-11-03 10:00:01 [INFO] Initial capital: $10,000.00
2025-11-03 10:00:02 [INFO] Allowed symbols: ['XRP', 'DOGE', 'BTC', 'ETH', 'SOL', 'BNB']
2025-11-03 10:00:03 [INFO] Fetching market data...
2025-11-03 10:00:05 [INFO] Available symbols: ['BTC', 'ETH', 'SOL', 'BNB']
2025-11-03 10:00:05 [WARN] skip_unavailable_symbol=XRP - Symbol not available
2025-11-03 10:00:05 [WARN] skip_unavailable_symbol=DOGE - Symbol not available
2025-11-03 10:00:06 [INFO] Calling Deepseek AI for trading decision...
2025-11-03 10:00:10 [INFO] AI Decision: BUY BTC @ $50000 (Confidence: 0.85)
2025-11-03 10:00:10 [INFO] ORDER EXECUTED: BUY 0.05 BTC @ $50000
...
```

---

## 🛠️ 常见问题

### Q1: "python不是内部或外部命令"

**解决方案**:
1. 重新安装Python,确保勾选 "Add Python to PATH"
2. 或者手动添加到PATH:
   - 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
   - 在"系统变量"中找到"Path"
   - 添加: `C:\Users\你的用户名\AppData\Local\Programs\Python\Python311`

### Q2: "No module named 'xxx'"

**解决方案**:
```cmd
pip install -r requirements.txt --upgrade
```

### Q3: "API key not found"

**解决方案**:
1. 检查 `config\my_config.yaml` 中是否填写了API密钥
2. 确保密钥格式正确,没有多余空格
3. 确保使用了 `--config config\my_config.yaml` 参数

### Q4: 系统运行一会就停止

**可能原因**:
1. **Deepseek API额度用完**: 检查账户余额
2. **网络连接问题**: 检查防火墙设置
3. **程序错误**: 查看日志文件 `logs\trading.log`

### Q5: 如何停止系统?

**方法**:
- 按 `Ctrl+C` 优雅停止
- 或者直接关闭命令提示符窗口

---

## 📁 项目文件结构

```
AITrading/
├── main.py                    # ⭐ 主入口文件 (运行这个!)
├── config/
│   ├── config.yaml           # 默认配置
│   └── my_config.yaml        # 你的配置 (自己创建)
├── src/
│   ├── ai/
│   │   └── deepseek_trading_agent.py  # AI决策引擎
│   ├── data/
│   │   └── market_data.py    # 市场数据采集
│   ├── trading/
│   │   └── executor.py       # 交易执行
│   ├── risk/
│   │   └── risk_manager.py   # 风险管理
│   └── trading_bot.py        # 交易机器人主类
├── tests/                     # 测试文件
├── logs/                      # 日志目录 (自动创建)
├── requirements.txt           # Python依赖
└── README.md                  # 项目说明
```

---

## 🔧 高级配置

### 使用虚拟环境 (推荐)

**创建虚拟环境**:
```cmd
python -m venv venv
```

**激活虚拟环境**:
```cmd
venv\Scripts\activate
```

**安装依赖**:
```cmd
pip install -r requirements.txt
```

**运行系统**:
```cmd
python main.py --mode paper
```

**退出虚拟环境**:
```cmd
deactivate
```

---

### 后台运行 (Windows服务)

**方法A: 使用pythonw (无窗口运行)**

创建 `run_background.bat`:
```batch
@echo off
cd /d "%~dp0"
start /B pythonw main.py --mode paper
```

双击运行,系统在后台运行,无窗口。

**方法B: 使用任务计划程序**

1. 打开"任务计划程序" (Win+R, 输入 `taskschd.msc`)
2. 创建基本任务
3. 触发器: 每天/每小时
4. 操作: 启动程序
   - 程序: `C:\Users\你的用户名\AppData\Local\Programs\Python\Python311\python.exe`
   - 参数: `main.py --mode paper`
   - 起始于: `C:\Users\你的用户名\Desktop\AITrading`

---

### 查看日志

**实时查看日志** (需要安装Git Bash或WSL):
```bash
tail -f logs/trading.log
```

**Windows原生方法**:
```cmd
powershell Get-Content logs\trading.log -Wait -Tail 50
```

**或者用记事本打开**:
```cmd
notepad logs\trading.log
```

---

## 📊 监控系统状态

### 方法1: 查看日志文件

```cmd
type logs\trading.log
```

### 方法2: 创建监控脚本

创建 `monitor.py`:
```python
import time
import os

log_file = "logs/trading.log"

print("=== AITrading Monitor ===")
print("Press Ctrl+C to stop\n")

while True:
    os.system('cls')  # 清屏
    print("=== Latest 20 lines ===")
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[-20:]:
            print(line.strip())
    time.sleep(5)  # 每5秒刷新
```

运行:
```cmd
python monitor.py
```

---

## 🔒 安全建议

### 1. 保护API密钥

- ❌ 不要将 `my_config.yaml` 提交到Git
- ❌ 不要在公开场合分享配置文件
- ✅ 使用环境变量存储密钥

**使用环境变量**:

Windows PowerShell:
```powershell
$env:DEEPSEEK_API_KEY="sk-你的密钥"
$env:HYPERLIQUID_PRIVATE_KEY="你的私钥"
python main.py --mode paper
```

### 2. 测试网先测试

- ✅ 先在测试网充分测试
- ✅ 确认策略有效后再用实盘
- ✅ 实盘从小资金开始

### 3. 设置止损止盈

- ✅ 在配置文件中设置合理的止损止盈
- ✅ 不要使用过高的杠杆
- ✅ 分散投资,不要全仓一个币种

---

## 📞 获取帮助

### 遇到问题?

1. **查看日志**: `logs\trading.log`
2. **查看文档**: `README.md`, `USER_GUIDE.md`
3. **GitHub Issues**: https://github.com/AnakinRM/AITrading/issues
4. **检查配置**: 确保API密钥正确

### 常用命令

```cmd
# 查看Python版本
python --version

# 查看已安装的包
pip list

# 更新pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 运行测试
python -m pytest tests/

# 查看帮助
python main.py --help
```

---

## 🎯 下一步

1. ✅ 成功运行模拟交易
2. ✅ 观察系统运行1-2天
3. ✅ 分析交易日志和收益
4. ✅ 调整配置参数优化策略
5. ⚠️ 谨慎考虑是否进行实盘交易

---

## 📚 推荐阅读

- **README.md** - 项目总览
- **USER_GUIDE.md** - 详细使用指南
- **CHANGELOG.md** - 版本更新日志
- **prompts/deepseek_trading.md** - AI Prompt说明

---

**祝您交易顺利! 📈💰🚀**

如有问题,请查看GitHub仓库的Issues页面或文档。
