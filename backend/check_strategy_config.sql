-- 전략 config 상세 확인
SELECT
    name,
    config->'indicators' as indicators,
    config->'buyConditions' as buy_conditions,
    config->'sellConditions' as sell_conditions
FROM strategies
WHERE name = '[템플릿] 골든크로스'
LIMIT 1;

-- 모든 전략의 indicators 구조 확인
SELECT
    name,
    jsonb_pretty(config->'indicators') as indicators_formatted
FROM strategies
ORDER BY created_at DESC;
