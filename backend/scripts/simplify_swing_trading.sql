-- 스윙 트레이딩 전략을 단순화 (MA 크로스만 사용)
-- RSI와 MACD 조건을 제거하여 거래 발생 확률 높임

UPDATE strategies
SET config = jsonb_set(
    jsonb_set(
        jsonb_set(
            config,
            '{indicators}',
            '[
                {"type": "MA", "params": {"period": 20}},
                {"type": "MA", "params": {"period": 60}}
            ]'::jsonb
        ),
        '{buyConditions}',
        '[
            {
                "id": "1",
                "type": "buy",
                "value": "ma_60",
                "operator": ">",
                "indicator": "ma_20",
                "combineWith": "AND"
            }
        ]'::jsonb
    ),
    '{sellConditions}',
    '[
        {
            "id": "2",
            "type": "sell",
            "value": "ma_60",
            "operator": "<",
            "indicator": "ma_20",
            "combineWith": "AND"
        }
    ]'::jsonb
)
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- 수정 후 확인
SELECT
    id,
    name,
    jsonb_array_length(config->'indicators') as indicator_count,
    jsonb_array_length(config->'buyConditions') as buy_condition_count,
    jsonb_array_length(config->'sellConditions') as sell_condition_count,
    config->'buyConditions'->0->>'indicator' as first_buy_indicator,
    config->'buyConditions'->0->>'operator' as first_buy_operator,
    config->'buyConditions'->0->>'value' as first_buy_value
FROM strategies
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';