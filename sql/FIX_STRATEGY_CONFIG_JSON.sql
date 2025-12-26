-- [FIX STRATEGY CONFIG]
-- Purpose: Populate 'config' column for test strategies with full JSON structure required by BacktestEngine
-- This resolves the issue where indicators are not calculated and signals are 0.

-- 1. Update MACD Strategy
UPDATE strategies
SET config = '{
    "indicators": [
        {
            "id": "macd_1",
            "name": "MACD",
            "params": {"fast": 12, "slow": 26, "signal": 9}
        }
    ],
    "buyConditions": [
        {
            "indicator": "MACD",
            "compareTo": "MACD_SIGNAL",
            "operator": ">",
            "value": 0
        }
    ],
    "sellConditions": [
        {
            "indicator": "MACD",
            "compareTo": "MACD_SIGNAL",
            "operator": "<",
            "value": 0
        }
    ],
    "useStageBasedStrategy": false
}'::jsonb
WHERE name = 'TEST_STRATEGY_A_MACD';

-- 2. Update Bollinger Bands Strategy
UPDATE strategies
SET config = '{
    "indicators": [
        {
            "id": "bb_1",
            "name": "Bollinger Bands",
            "params": {"period": 20, "std_dev": 2}
        }
    ],
    "buyConditions": [
        {
            "indicator": "close",
            "compareTo": "BB_UPPER",
            "operator": "<",
            "value": 0
        }
    ],
    "sellConditions": [
        {
            "indicator": "close",
            "compareTo": "BB_MIDDLE",
            "operator": ">",
            "value": 0
        }
    ],
    "useStageBasedStrategy": false
}'::jsonb
WHERE name = 'TEST_STRATEGY_B_BB';
