# Changelog

All notable changes to the AITrading project will be documented in this file.

## [Unreleased] - 2025-11-03

### Added

#### Trading Symbol Whitelist
- **BREAKING**: Limited trading to 6 allowed symbols only: `XRP`, `DOGE`, `BTC`, `ETH`, `SOL`, `BNB`
- Added `src/utils/constants.py` with `ALLOWED_SYMBOLS` constant
- Implemented symbol whitelist validation in all trading modules
- Added support for both LONG and SHORT directions on all symbols

#### Error Handling & Fault Tolerance
- Added `get_available_symbols()` method to filter available symbols from whitelist
- Added `get_price_safe()` method with comprehensive error handling
- Added `get_market_data_for_symbols()` method that skips unavailable symbols instead of failing
- Implemented automatic skip for symbols with:
  - No price data available
  - Invalid price (None, 0, negative)
  - Contract not available on Hyperliquid
- Added structured logging events:
  - `skip_unavailable_symbol` - when a symbol is skipped
  - `price_fetch_failed` - when price fetching fails
  - `contract_unavailable` - when contract is not available

#### DeepSeek Prompt System (nof1.ai Style)
- Created `prompts/deepseek_trading.md` with comprehensive prompt templates
- Implemented `DeepseekTradingAgent` class with:
  - Orchestrator system prompt for task initialization
  - Per-cycle trading decision prompts
  - Context caching for historical decisions (last 5 decisions)
  - Structured JSON output format
  - Market view with news signals and on-chain/off-chain analysis
- Added JSON response parsing with markdown code block handling
- Added trading plan validation:
  - Filters disallowed symbols
  - Filters unavailable symbols
  - Validates directions (LONG/SHORT only)
  - Validates position sizes (0-1 range)

#### Testing
- Added `tests/test_symbol_filtering.py` with 12 unit tests:
  - Symbol whitelist validation
  - Price fetching with error handling
  - Available symbols filtering
  - Market data collection with skip logic
- Added `tests/test_json_schema.py` with JSON schema validation:
  - Trading plan structure validation
  - Symbol enum validation
  - Direction enum validation (LONG/SHORT)
  - Position size range validation
  - Required fields validation
- Added `jsonschema>=4.0.0` dependency

### Changed

#### Configuration
- Updated `config/config.yaml`:
  - Changed `trading_pairs` from 10 coins to 6 allowed symbols
  - Updated `temperature` from 0.7 to 1.0 (recommended for data analysis per Deepseek docs)
  - Increased `max_leverage` from 5 to 20 (removed artificial limit, use system risk controls)
  - Added comments explaining whitelist enforcement

#### Market Data Module
- Modified `src/data/market_data.py`:
  - Added `allowed_symbols` instance variable
  - Imported constants from `src/utils/constants.py`
  - Added 3 new methods with fault tolerance
  - Enhanced logging with structured events

#### AI Agent
- Created new `src/ai/deepseek_trading_agent.py` (recommended over old `deepseek_agent.py`):
  - Implements nof1.ai-style prompt system
  - Supports context caching
  - Outputs structured JSON
  - Validates all trading decisions
  - Handles both LONG and SHORT directions

### Technical Details

#### Symbol Filtering Flow
```
1. Load ALLOWED_SYMBOLS constant
2. Fetch all market prices from Hyperliquid
3. Filter symbols:
   - Must be in ALLOWED_SYMBOLS
   - Must have valid price (not None, >0)
   - Must be available on exchange
4. Log skipped symbols with reason
5. Continue processing available symbols only
```

#### DeepSeek Prompt Flow
```
1. Initialize with Orchestrator prompt (system message)
2. Build context with:
   - Current positions
   - Latest prices
   - Recent news/events
   - Unavailable symbols list
3. Add historical context (last 5 decisions)
4. Call Deepseek API
5. Parse JSON response
6. Validate trading plan:
   - Filter disallowed symbols
   - Filter unavailable symbols
   - Validate directions
7. Cache decision in context history
8. Return validated trading plan
```

#### Logging Events
- `skip_unavailable_symbol={SYMBOL}` - Symbol skipped due to unavailability
- `price_fetch_failed={SYMBOL}` - Failed to fetch price for symbol
- `contract_unavailable={SYMBOL}` - Contract not available on Hyperliquid
- `symbol_not_allowed={SYMBOL}` - Symbol not in whitelist

### Migration Guide

#### For Existing Users

1. **Update Configuration**:
   ```yaml
   trading:
     trading_pairs:
       - "XRP"
       - "DOGE"
       - "BTC"
       - "ETH"
       - "SOL"
       - "BNB"
   
   deepseek:
     temperature: 1.0  # Changed from 0.7
   
   risk:
     max_leverage: 20  # Changed from 5
   ```

2. **Update Code**:
   - Replace `deepseek_agent.py` imports with `deepseek_trading_agent.py`
   - Use `get_market_data_for_symbols()` instead of manual iteration
   - Handle unavailable symbols gracefully (no need to check, automatic)

3. **Run Tests**:
   ```bash
   pip install jsonschema
   python -m pytest tests/test_symbol_filtering.py
   python -m pytest tests/test_json_schema.py
   ```

### Breaking Changes

- **Trading symbols limited to 6**: Any code assuming other symbols will fail
- **New AI agent interface**: `DeepseekTradingAgent` has different method signatures
- **JSON output format**: Trading plans now use structured JSON schema

### Verification Checklist

- [x] Only XRP/DOGE/BTC/ETH/SOL/BNB can be traded
- [x] Unavailable symbols are skipped with warning logs
- [x] System continues when some symbols fail
- [x] Both LONG and SHORT directions supported
- [x] DeepSeek receives orchestrator prompt at start
- [x] DeepSeek outputs valid JSON
- [x] Trading plan includes news/events analysis
- [x] Unit tests for symbol filtering
- [x] JSON schema validation tests
- [x] Leverage limit removed (uses system defaults)

### References

- nof1.ai Alpha Arena: https://nof1.ai/
- Deepseek API Docs: https://api-docs.deepseek.com/
- Deepseek Temperature Settings: Use 1.0 for data analysis/trading
- Hyperliquid Docs: https://hyperliquid.gitbook.io/

---

## [1.0.0] - 2025-10-30

### Added
- Initial release of AITrading system
- Basic Deepseek integration
- HyperLiquid API integration
- Risk management module
- Trading execution module
- Configuration system
- Logging system
- Basic documentation
