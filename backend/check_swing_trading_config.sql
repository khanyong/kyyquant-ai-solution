-- 스윙 트레이딩 전략의 실제 config 확인

SELECT
    id,
    name,
    config->'buyConditions' as buy_conditions,
    config->'sellConditions' as sell_conditions,
    config->'indicators' as indicators
FROM strategies
WHERE name LIKE '%스윙%' OR name LIKE '%Swing%'
ORDER BY created_at DESC
LIMIT 1;

-- buyConditions의 left 값들만 추출
SELECT
    name,
    jsonb_array_elements(config->'buyConditions')->>'left' as buy_condition_left
FROM strategies
WHERE name LIKE '%스윙%' OR name LIKE '%Swing%';

-- 골든크로스도 확인
SELECT
    name,
    config->'buyConditions' as buy_conditions,
    config->'indicators' as indicators
FROM strategies
WHERE name LIKE '%골든%' OR name LIKE '%Golden%'
ORDER BY created_at DESC
LIMIT 1;
