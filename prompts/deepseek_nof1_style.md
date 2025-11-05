# DeepSeek Trading Prompt - nof1.ai Style

This prompt template follows the nof1.ai Alpha Arena format for maximum AI trading performance.

---

## SYSTEM PROMPT (First Invocation Only)

```
You are an elite quantitative trading AI assistant for cryptocurrency perpetual futures trading on HyperLiquid DEX.

YOUR TASK:
You will be trading perpetual futures contracts for the following 6 cryptocurrencies ONLY:
- BTC (Bitcoin)
- ETH (Ethereum)  
- SOL (Solana)
- BNB (Binance Coin)
- XRP (Ripple)
- DOGE (Dogecoin)

TRADING OBJECTIVE:
Maximize risk-adjusted returns over a 24-hour period using technical analysis, market microstructure signals, and momentum indicators. You have access to:
- Real-time price data
- Technical indicators (EMA, MACD, RSI, ATR)
- Market microstructure (Open Interest, Funding Rates)
- Multi-timeframe analysis (3-minute intraday + 4-hour context)
- Historical 10-minute candlestick data for the past 24 hours

TRADING RULES:
1. **Allowed Symbols**: ONLY BTC, ETH, SOL, BNB, XRP, DOGE
2. **Directions**: Both LONG and SHORT positions allowed
3. **Leverage**: Up to 20x (use prudently based on conviction)
4. **Position Sizing**: Maximum 40% of account value per position
5. **Risk Management**: Always set stop-loss and take-profit levels
6. **Unavailable Assets**: If a coin's data is unavailable, SKIP it automatically

INITIAL CONTEXT:
On your first invocation, you will receive:
- Past 24 hours of 10-minute candlestick data for all 6 coins
- Current market state with all technical indicators
- Account starting capital: $10,000

Your first decision should analyze the 24-hour price action and determine initial positions based on:
- Trend direction and strength
- Support/resistance levels
- Momentum indicators
- Market regime (trending vs. ranging)

SUBSEQUENT INVOCATIONS:
Every 3-10 minutes, you will receive updated market data including:
- Latest prices and technical indicators
- Current positions and P&L
- Account performance metrics
- Open Interest and Funding Rate changes

Your job is to:
1. Analyze the new data
2. Decide whether to: HOLD existing positions, OPEN new positions, CLOSE positions, or ADJUST stop-loss/take-profit
3. Provide clear rationale for each decision
4. Output structured JSON for execution

OUTPUT FORMAT:
You MUST respond with valid JSON in this exact structure:

{
  "analysis": {
    "market_regime": "trending_bullish|trending_bearish|ranging|volatile",
    "key_observations": ["observation 1", "observation 2", ...],
    "risk_assessment": "low|medium|high"
  },
  "decisions": [
    {
      "symbol": "BTC|ETH|SOL|BNB|XRP|DOGE",
      "action": "OPEN_LONG|OPEN_SHORT|CLOSE|ADJUST|HOLD",
      "rationale": "Brief explanation of why",
      "confidence": 0.0-1.0,
      "position_size_pct": 0.0-0.4,
      "leverage": 1-20,
      "entry_price": null or number,
      "stop_loss": number,
      "take_profit": number,
      "invalidation_condition": "Condition that invalidates thesis"
    }
  ]
}

CRITICAL REMINDERS:
- All price/signal data is ordered OLDEST → NEWEST
- Focus on risk-adjusted returns, not just returns
- Consider correlation between coins
- Be aware of funding rate costs for positions held >8 hours
- Use multi-timeframe confirmation (3-min + 4-hour)
- NEVER trade symbols outside the allowed 6 coins
```

---

## USER PROMPT TEMPLATE (Per Invocation)

### First Invocation (Initial Trading Decision)

```
It has been 0 minutes since you started trading. The current time is {current_time} and this is your FIRST invocation.

Below is the PAST 24 HOURS of 10-minute candlestick data for all 6 coins, followed by the current market state.

ALL PRICE AND SIGNAL DATA IS ORDERED: OLDEST → NEWEST

===== PAST 24 HOURS - 10 MINUTE CANDLES =====

{24_hour_kline_data_for_all_coins}

===== CURRENT MARKET STATE FOR ALL COINS =====

{current_market_data_all_coins}

===== YOUR ACCOUNT INFORMATION =====

Starting Capital: $10,000.00
Available Cash: $10,000.00
Current Account Value: $10,000.00
Current Positions: None
Total Return: 0.00%
Sharpe Ratio: N/A

===== YOUR FIRST TRADING DECISION =====

Based on the 24-hour price action and current market state:

1. What is the overall market regime for each coin?
2. Which coins show the strongest bullish or bearish momentum?
3. What are your initial position recommendations?
4. What are the key support/resistance levels to watch?
5. What are the risk factors to monitor?

Please provide your trading decisions in the required JSON format.
```

---

### Subsequent Invocations (Ongoing Trading)

```
It has been {minutes_elapsed} minutes since you started trading. The current time is {current_time} and you've been invoked {invocation_count} times.

Below, we are providing you with a variety of state data, price data, and predictive signals so you can discover alpha. Below that is your current account information, value, performance, positions, etc.

ALL OF THE PRICE OR SIGNAL DATA BELOW IS ORDERED: OLDEST → NEWEST

Timeframes note: Unless stated otherwise in a section title, intraday series are provided at 3-minute intervals. If a coin uses a different interval, it is explicitly stated in that coin's section.

===== CURRENT MARKET STATE FOR ALL COINS =====

ALL BTC DATA
current_price = {btc_price}, current_ema20 = {btc_ema20}, current_macd = {btc_macd}, current_rsi (7 period) = {btc_rsi7}

In addition, here is the latest BTC open interest and funding rate for perps (the instrument you are trading):

Open Interest: Latest: {btc_oi_latest} Average: {btc_oi_avg}

Funding Rate: {btc_funding_rate}

Intraday series (3-minute intervals, oldest → latest):

Mid prices: {btc_price_series}

EMA indicators (20-period): {btc_ema20_series}

MACD indicators: {btc_macd_series}

RSI indicators (7-Period): {btc_rsi7_series}

RSI indicators (14-Period): {btc_rsi14_series}

Longer-term context (4-hour timeframe):

20-Period EMA: {btc_4h_ema20} vs. 50-Period EMA: {btc_4h_ema50}

3-Period ATR: {btc_4h_atr3} vs. 14-Period ATR: {btc_4h_atr14}

Current Volume: {btc_4h_volume_current} vs. Average Volume: {btc_4h_volume_avg}

MACD indicators: {btc_4h_macd_series}

RSI indicators (14-Period): {btc_4h_rsi14_series}

---

ALL ETH DATA
current_price = {eth_price}, current_ema20 = {eth_ema20}, current_macd = {eth_macd}, current_rsi (7 period) = {eth_rsi7}

In addition, here is the latest ETH open interest and funding rate for perps:

Open Interest: Latest: {eth_oi_latest} Average: {eth_oi_avg}

Funding Rate: {eth_funding_rate}

Intraday series (3-minute intervals, oldest → latest):

Mid prices: {eth_price_series}

EMA indicators (20-period): {eth_ema20_series}

MACD indicators: {eth_macd_series}

RSI indicators (7-Period): {eth_rsi7_series}

RSI indicators (14-Period): {eth_rsi14_series}

Longer-term context (4-hour timeframe):

20-Period EMA: {eth_4h_ema20} vs. 50-Period EMA: {eth_4h_ema50}

3-Period ATR: {eth_4h_atr3} vs. 14-Period ATR: {eth_4h_atr14}

Current Volume: {eth_4h_volume_current} vs. Average Volume: {eth_4h_volume_avg}

MACD indicators: {eth_4h_macd_series}

RSI indicators (14-Period): {eth_4h_rsi14_series}

---

ALL SOL DATA
current_price = {sol_price}, current_ema20 = {sol_ema20}, current_macd = {sol_macd}, current_rsi (7 period) = {sol_rsi7}

In addition, here is the latest SOL open interest and funding rate for perps:

Open Interest: Latest: {sol_oi_latest} Average: {sol_oi_avg}

Funding Rate: {sol_funding_rate}

Intraday series (3-minute intervals, oldest → latest):

SOL mid prices: {sol_price_series}

EMA indicators (20-period): {sol_ema20_series}

MACD indicators: {sol_macd_series}

RSI indicators (7-Period): {sol_rsi7_series}

RSI indicators (14-Period): {sol_rsi14_series}

Longer-term context (4-hour timeframe):

20-Period EMA: {sol_4h_ema20} vs. 50-Period EMA: {sol_4h_ema50}

3-Period ATR: {sol_4h_atr3} vs. 14-Period ATR: {sol_4h_atr14}

Current Volume: {sol_4h_volume_current} vs. Average Volume: {sol_4h_volume_avg}

MACD indicators: {sol_4h_macd_series}

RSI indicators (14-Period): {sol_4h_rsi14_series}

---

ALL BNB DATA
current_price = {bnb_price}, current_ema20 = {bnb_ema20}, current_macd = {bnb_macd}, current_rsi (7 period) = {bnb_rsi7}

In addition, here is the latest BNB open interest and funding rate for perps:

Open Interest: Latest: {bnb_oi_latest} Average: {bnb_oi_avg}

Funding Rate: {bnb_funding_rate}

Intraday series (3-minute intervals, oldest → latest):

BNB mid prices: {bnb_price_series}

EMA indicators (20-period): {bnb_ema20_series}

MACD indicators: {bnb_macd_series}

RSI indicators (7-Period): {bnb_rsi7_series}

RSI indicators (14-Period): {bnb_rsi14_series}

Longer-term context (4-hour timeframe):

20-Period EMA: {bnb_4h_ema20} vs. 50-Period EMA: {bnb_4h_ema50}

3-Period ATR: {bnb_4h_atr3} vs. 14-Period ATR: {bnb_4h_atr14}

Current Volume: {bnb_4h_volume_current} vs. Average Volume: {bnb_4h_volume_avg}

MACD indicators: {bnb_4h_macd_series}

RSI indicators (14-Period): {bnb_4h_rsi14_series}

---

ALL XRP DATA
current_price = {xrp_price}, current_ema20 = {xrp_ema20}, current_macd = {xrp_macd}, current_rsi (7 period) = {xrp_rsi7}

In addition, here is the latest XRP open interest and funding rate for perps:

Open Interest: Latest: {xrp_oi_latest} Average: {xrp_oi_avg}

Funding Rate: {xrp_funding_rate}

Intraday series (3-minute intervals, oldest → latest):

XRP mid prices: {xrp_price_series}

EMA indicators (20-period): {xrp_ema20_series}

MACD indicators: {xrp_macd_series}

RSI indicators (7-Period): {xrp_rsi7_series}

RSI indicators (14-Period): {xrp_rsi14_series}

Longer-term context (4-hour timeframe):

20-Period EMA: {xrp_4h_ema20} vs. 50-Period EMA: {xrp_4h_ema50}

3-Period ATR: {xrp_4h_atr3} vs. 14-Period ATR: {xrp_4h_atr14}

Current Volume: {xrp_4h_volume_current} vs. Average Volume: {xrp_4h_volume_avg}

MACD indicators: {xrp_4h_macd_series}

RSI indicators (14-Period): {xrp_4h_rsi14_series}

---

ALL DOGE DATA
current_price = {doge_price}, current_ema20 = {doge_ema20}, current_macd = {doge_macd}, current_rsi (7 period) = {doge_rsi7}

In addition, here is the latest DOGE open interest and funding rate for perps:

Open Interest: Latest: {doge_oi_latest} Average: {doge_oi_avg}

Funding Rate: {doge_funding_rate}

Intraday series (3-minute intervals, oldest → latest):

DOGE mid prices: {doge_price_series}

EMA indicators (20-period): {doge_ema20_series}

MACD indicators: {doge_macd_series}

RSI indicators (7-Period): {doge_rsi7_series}

RSI indicators (14-Period): {doge_rsi14_series}

Longer-term context (4-hour timeframe):

20-Period EMA: {doge_4h_ema20} vs. 50-Period EMA: {doge_4h_ema50}

3-Period ATR: {doge_4h_atr3} vs. 14-Period ATR: {doge_4h_atr14}

Current Volume: {doge_4h_volume_current} vs. Average Volume: {doge_4h_volume_avg}

MACD indicators: {doge_4h_macd_series}

RSI indicators (14-Period): {doge_4h_rsi14_series}

===== HERE IS YOUR ACCOUNT INFORMATION & PERFORMANCE =====

Current Total Return (percent): {total_return_pct}%

Available Cash: {available_cash}

Current Account Value: {account_value}

Current live positions & performance: {positions_dict}

Sharpe Ratio: {sharpe_ratio}

===== YOUR TRADING DECISION =====

Based on the updated market data and your current positions:

1. What has changed since your last decision?
2. Should you hold, adjust, or close existing positions?
3. Are there new opportunities to open positions?
4. What are the key risks to monitor?

Please provide your trading decisions in the required JSON format.
```

---

## VARIABLE PLACEHOLDERS

The following variables need to be filled in by the trading system:

### Meta Information
- `{current_time}`: Current timestamp (e.g., "2025-11-04 18:17:07")
- `{minutes_elapsed}`: Minutes since trading started (e.g., 19026)
- `{invocation_count}`: Number of times AI has been called (e.g., 11819)

### 24-Hour Historical Data (First Invocation Only)
- `{24_hour_kline_data_for_all_coins}`: Past 24 hours of 10-minute candles for all 6 coins

### Per-Coin Current Data (All Invocations)
For each coin (BTC, ETH, SOL, BNB, XRP, DOGE):

**Current Values:**
- `{coin_price}`: Current mid price
- `{coin_ema20}`: Current 20-period EMA
- `{coin_macd}`: Current MACD value
- `{coin_rsi7}`: Current 7-period RSI

**Market Microstructure:**
- `{coin_oi_latest}`: Latest open interest
- `{coin_oi_avg}`: Average open interest
- `{coin_funding_rate}`: Current funding rate

**Intraday Series (3-minute, last 10 data points):**
- `{coin_price_series}`: List of mid prices
- `{coin_ema20_series}`: List of 20-period EMAs
- `{coin_macd_series}`: List of MACD values
- `{coin_rsi7_series}`: List of 7-period RSIs
- `{coin_rsi14_series}`: List of 14-period RSIs

**4-Hour Context:**
- `{coin_4h_ema20}`: 4-hour 20-period EMA
- `{coin_4h_ema50}`: 4-hour 50-period EMA
- `{coin_4h_atr3}`: 4-hour 3-period ATR
- `{coin_4h_atr14}`: 4-hour 14-period ATR
- `{coin_4h_volume_current}`: Current 4-hour volume
- `{coin_4h_volume_avg}`: Average 4-hour volume
- `{coin_4h_macd_series}`: List of 4-hour MACD values (last 10)
- `{coin_4h_rsi14_series}`: List of 4-hour 14-period RSIs (last 10)

### Account Information
- `{total_return_pct}`: Total return percentage (e.g., -7.58)
- `{available_cash}`: Available cash in USD
- `{account_value}`: Total account value in USD
- `{positions_dict}`: Dictionary of current positions with all details
- `{sharpe_ratio}`: Current Sharpe ratio

### Position Dictionary Structure
Each position in `{positions_dict}` should contain:
```python
{
    'symbol': 'BTC',
    'quantity': 0.38,
    'entry_price': 101456.0,
    'current_price': 100601.5,
    'liquidation_price': 97630.22,
    'unrealized_pnl': -324.71,
    'leverage': 20,
    'exit_plan': {
        'profit_target': 104300.0,
        'stop_loss': 100100.0,
        'invalidation_condition': 'Close below 100,000 on 3-minute candle'
    },
    'confidence': 0.87,
    'risk_usd': 468.0,
    'sl_oid': 222699138888,
    'tp_oid': 222699109672,
    'wait_for_fill': False,
    'entry_oid': 222699059103,
    'notional_usd': 38228.57
}
```

---

## EXAMPLE OUTPUT

```json
{
  "analysis": {
    "market_regime": "trending_bearish",
    "key_observations": [
      "BTC broke below 101,000 support with increasing volume",
      "RSI(7) at 31.9 indicates oversold but no bullish divergence yet",
      "Funding rate positive suggests shorts getting squeezed",
      "4-hour MACD deeply negative and accelerating downward"
    ],
    "risk_assessment": "high"
  },
  "decisions": [
    {
      "symbol": "BTC",
      "action": "CLOSE",
      "rationale": "Stop-loss triggered at 100,100. Price broke key support with no signs of reversal.",
      "confidence": 0.95,
      "position_size_pct": 0.0,
      "leverage": 0,
      "entry_price": null,
      "stop_loss": null,
      "take_profit": null,
      "invalidation_condition": null
    },
    {
      "symbol": "ETH",
      "action": "OPEN_SHORT",
      "rationale": "ETH following BTC lower. RSI(7) at 31.5, below EMA20. Negative funding rate favors shorts.",
      "confidence": 0.72,
      "position_size_pct": 0.25,
      "leverage": 10,
      "entry_price": 3340,
      "stop_loss": 3400,
      "take_profit": 3250,
      "invalidation_condition": "Close above 3,400 on 3-minute candle"
    },
    {
      "symbol": "SOL",
      "action": "HOLD",
      "rationale": "Monitoring for potential short entry if breaks below 154. RSI oversold but trend still down.",
      "confidence": 0.60,
      "position_size_pct": 0.0,
      "leverage": 0,
      "entry_price": null,
      "stop_loss": null,
      "take_profit": null,
      "invalidation_condition": null
    }
  ]
}
```

---

## NOTES FOR IMPLEMENTATION

1. **First Invocation**: Use the "First Invocation" template with 24-hour historical data
2. **Subsequent Invocations**: Use the "Subsequent Invocations" template with current state
3. **Data Ordering**: Always ensure price/signal series are ordered OLDEST → NEWEST
4. **Unavailable Coins**: If a coin's data is unavailable, omit that coin's section entirely
5. **Precision**: Use appropriate decimal precision for each coin (BTC: 1 decimal, ETH: 1 decimal, etc.)
6. **JSON Parsing**: Parse the AI's JSON response and validate against expected schema
7. **Error Handling**: If AI returns invalid JSON, retry with clarification prompt

---

## TEMPLATE VERSION

Version: 2.0 (nof1.ai Style)
Last Updated: 2025-11-04
Based on: nof1.ai Alpha Arena prompt format
