-- [템플릿] 스윙 트레이딩 전략 수정
-- MACD_SIGNAL 중복 제거 및 조건 수정

UPDATE strategies
SET config = '{
    "indicators": [
        {"name": "sma_20", "type": "SMA", "params": {"period": 20}},
        {"name": "sma_60", "type": "SMA", "params": {"period": 60}},
        {"name": "ema_10", "type": "EMA", "params": {"period": 10}},
        {"name": "rsi_14", "type": "RSI", "params": {"period": 14}},
        {"name": "macd", "type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}},
        {"name": "adx_14", "type": "ADX", "params": {"period": 14}},
        {"name": "volume_ma_20", "type": "SMA", "params": {"period": 20, "source": "volume"}}
    ],
    "buyConditions": [
        {"left": "sma_20", "operator": ">", "right": "sma_60"},
        {"left": "ema_10", "operator": ">", "right": "sma_20"},
        {"left": "rsi_14", "operator": "<", "right": "60"},
        {"left": "rsi_14", "operator": ">", "right": "35"},
        {"left": "macd_12_26", "operator": ">", "right": "0"},
        {"left": "adx_14", "operator": ">", "right": "20"},
        {"left": "volume", "operator": ">", "right": "volume_ma_20"}
    ],
    "sellConditions": [
        {"left": "sma_20", "operator": "<", "right": "sma_60"},
        {"left": "rsi_14", "operator": ">", "right": "70"},
        {"left": "macd_12_26", "operator": "<", "right": "macd_signal_12_26_9"}
    ],
    "targetProfit": {
        "simple": {
            "enabled": true,
            "value": 15
        }
    },
    "stopLoss": {
        "enabled": true,
        "value": 7
    },
    "risk": {
        "stopLoss": 7,
        "takeProfit": 15,
        "positionSize": 20,
        "maxPositions": 5,
        "trailingStop": 5
    }
}'::jsonb
WHERE name = '[템플릿] 스윙 트레이딩';

-- 결과 확인
SELECT
    name,
    config->'indicators' as indicators,
    config->'buyConditions' as buy_conditions,
    config->'sellConditions' as sell_conditions
FROM strategies
WHERE name = '[템플릿] 스윙 트레이딩';