-- 초단순 전략으로 변경 - 반드시 거래가 발생하도록
-- MA5 > MA10 매수, MA5 < MA10 매도

UPDATE strategies
SET config = jsonb_build_object(
    'templateId', 'swing-trading',
    'templateName', '스윙 트레이딩',
    'strategy_type', 'custom',
    'indicators', '[
        {"type": "MA", "params": {"period": 5}},
        {"type": "MA", "params": {"period": 10}}
    ]'::jsonb,
    'buyConditions', '[
        {
            "indicator": "ma_5",
            "operator": ">",
            "value": "ma_10"
        }
    ]'::jsonb,
    'sellConditions', '[
        {
            "indicator": "ma_5",
            "operator": "<",
            "value": "ma_10"
        }
    ]'::jsonb,
    'riskManagement', '{
        "stopLoss": -10,
        "takeProfit": 20,
        "maxPositions": 5,
        "positionSize": 20,
        "trailingStop": false,
        "trailingStopPercent": 0
    }'::jsonb
)
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- 수정 확인
SELECT
    id,
    name,
    jsonb_pretty(config) as full_config
FROM strategies
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- 조건 간단 확인
SELECT
    config->'indicators'->0->>'type' as ind1_type,
    config->'indicators'->0->'params'->>'period' as ind1_period,
    config->'indicators'->1->>'type' as ind2_type,
    config->'indicators'->1->'params'->>'period' as ind2_period,
    config->'buyConditions'->0->>'indicator' as buy_indicator,
    config->'buyConditions'->0->>'operator' as buy_operator,
    config->'buyConditions'->0->>'value' as buy_value,
    config->'sellConditions'->0->>'indicator' as sell_indicator,
    config->'sellConditions'->0->>'operator' as sell_operator,
    config->'sellConditions'->0->>'value' as sell_value
FROM strategies
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';