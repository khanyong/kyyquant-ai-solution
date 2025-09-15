-- 스윙 트레이딩 전략 수정
-- 1. 누락된 지표 추가
-- 2. cross_above/below를 단순 비교로 변경

UPDATE strategies
SET config = jsonb_set(
    config,
    '{indicators}',
    '[
        {"type": "MA", "params": {"period": 20}},
        {"type": "MA", "params": {"period": 60}},
        {"type": "RSI", "params": {"period": 14}},
        {"type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}}
    ]'::jsonb
)
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- buyConditions 수정 (cross_above → >)
UPDATE strategies
SET config = jsonb_set(
    config,
    '{buyConditions}',
    '[
        {
            "id": "1",
            "type": "buy",
            "value": "ma_60",
            "operator": ">",
            "indicator": "ma_20",
            "combineWith": "AND"
        },
        {
            "id": "2",
            "type": "buy",
            "value": 60,
            "operator": "<",
            "indicator": "rsi_14",
            "combineWith": "AND"
        },
        {
            "id": "3",
            "type": "buy",
            "value": 0,
            "operator": ">",
            "indicator": "macd_12_26",
            "combineWith": "AND"
        }
    ]'::jsonb
)
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- sellConditions 수정 (cross_below → <)
UPDATE strategies
SET config = jsonb_set(
    config,
    '{sellConditions}',
    '[
        {
            "id": "4",
            "type": "sell",
            "value": "ma_60",
            "operator": "<",
            "indicator": "ma_20",
            "combineWith": "AND"
        },
        {
            "id": "5",
            "type": "sell",
            "value": 70,
            "operator": ">",
            "indicator": "rsi_14",
            "combineWith": "AND"
        }
    ]'::jsonb
)
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- 수정 후 확인
SELECT
    id,
    name,
    jsonb_pretty(config->'indicators') as indicators,
    jsonb_pretty(config->'buyConditions') as buy_conditions,
    jsonb_pretty(config->'sellConditions') as sell_conditions
FROM strategies
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';