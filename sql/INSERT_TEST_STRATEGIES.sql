-- [TEST STRATEGY INSERTION]
-- Purpose: Insert 2 high-frequency strategies for Multi-Strategy Allocation Testing
-- Allocation: 50% each

-- 1. Test Strategy A: MACD Golden Cross (Trend Following)
-- Logic: Buy if MACD Histogram > 0 (Momentum Up), Sell if MACD Histogram < 0
INSERT INTO strategies (
    name, 
    description, 
    type, 
    timeframe, 
    universe, 
    allocated_capital, 
    allocated_percent, 
    is_active, 
    auto_trade_enabled,
    entry_conditions,
    conditions
) VALUES (
    'TEST_STRATEGY_A_MACD',
    'High Frequency MACD Strategy for Allocation Test',
    'MACD',
    '1m',
    ARRAY['KOSPI'], -- [FIX] Array syntax
    -- [DYNAMIC ALLOCATION] 50% of Actual Account Balance (Fallback to 500M if empty)
    (SELECT COALESCE(total_asset, 500000000) * 0.5 FROM kw_account_balance ORDER BY updated_at DESC LIMIT 1),
    0.5,       -- 50% Ratio
    true,
    false, 
    '{"type": "formula", "value": "macd_hist > 0"}',   -- entry_conditions (JSON)
    '{"exit": {"type": "formula", "value": "macd_hist < 0"}}' -- conditions (JSON for Exit)
);

-- 2. Test Strategy B: Bollinger Reversal (High Turnover)
-- Logic: Buy if Close < Upper Band (Easy entry), Sell if Close > Moving Average
INSERT INTO strategies (
    name, 
    description, 
    type, 
    timeframe, 
    universe, 
    allocated_capital, 
    allocated_percent, 
    is_active, 
    auto_trade_enabled,
    entry_conditions,
    conditions
) VALUES (
    'TEST_STRATEGY_B_BB',
    'High Frequency Bollinger Strategy for Allocation Test',
    'Bollinger',
    '1m',
    ARRAY['KOSDAQ'],
    -- [DYNAMIC ALLOCATION] 50% of Actual Account Balance
    (SELECT COALESCE(total_asset, 500000000) * 0.5 FROM kw_account_balance ORDER BY updated_at DESC LIMIT 1),
    0.5,       -- 50% Ratio
    true,
    false,
    '{"type": "formula", "value": "close < bb_upper"}', -- entry_conditions (JSON)
    '{"exit": {"type": "formula", "value": "close > bb_middle"}}' -- conditions (JSON for Exit)
);
