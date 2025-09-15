-- ================================================
-- SQL 수정 후 전략 상태 확인
-- ================================================

-- 1. 전체 전략 개수와 indicators 상태 확인
SELECT
    COUNT(*) as total_strategies,
    COUNT(CASE WHEN config->'indicators' IS NOT NULL AND jsonb_array_length(config->'indicators') > 0 THEN 1 END) as with_indicators,
    COUNT(CASE WHEN config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0 THEN 1 END) as without_indicators
FROM strategies;

-- 2. 템플릿별 indicators 상태 확인
SELECT
    config->>'templateId' as template_id,
    COUNT(*) as strategy_count,
    jsonb_array_length(COALESCE(config->'indicators', '[]'::jsonb)) as indicator_count,
    config->'indicators' as indicators_sample
FROM strategies
GROUP BY config->>'templateId', config->'indicators'
ORDER BY template_id;

-- 3. Golden Cross 전략 상세 확인
SELECT
    id,
    name,
    config->>'templateId' as template_id,
    jsonb_pretty(config->'indicators') as indicators,
    jsonb_pretty(config->'buyConditions') as buy_conditions,
    jsonb_pretty(config->'sellConditions') as sell_conditions
FROM strategies
WHERE config->>'templateId' = 'golden-cross'
LIMIT 1;

-- 4. RSI Reversal 전략 상세 확인
SELECT
    id,
    name,
    config->>'templateId' as template_id,
    jsonb_pretty(config->'indicators') as indicators,
    jsonb_pretty(config->'buyConditions') as buy_conditions,
    jsonb_pretty(config->'sellConditions') as sell_conditions
FROM strategies
WHERE config->>'templateId' = 'rsi-reversal'
LIMIT 1;

-- 5. 대문자가 여전히 남아있는지 확인
SELECT
    id,
    name,
    'Uppercase found' as issue,
    config::text as config_text
FROM strategies
WHERE config::text LIKE '%"MA_%'
   OR config::text LIKE '%"RSI_%'
   OR config::text LIKE '%"CROSS_ABOVE"%'
   OR config::text LIKE '%"CROSS_BELOW"%'
LIMIT 5;

-- 6. 최근 업데이트된 전략 확인
SELECT
    id,
    name,
    config->>'templateId' as template_id,
    jsonb_array_length(COALESCE(config->'indicators', '[]'::jsonb)) as indicator_count,
    updated_at
FROM strategies
WHERE updated_at > NOW() - INTERVAL '1 hour'
ORDER BY updated_at DESC;

-- 7. 조건문에 사용된 지표명 확인
WITH conditions AS (
    SELECT
        id,
        name,
        jsonb_array_elements(config->'buyConditions') as buy_cond,
        jsonb_array_elements(config->'sellConditions') as sell_cond
    FROM strategies
    WHERE config->>'templateId' IN ('golden-cross', 'rsi-reversal')
)
SELECT DISTINCT
    buy_cond->>'indicator' as buy_indicator,
    buy_cond->>'operator' as buy_operator,
    buy_cond->>'value' as buy_value,
    sell_cond->>'indicator' as sell_indicator,
    sell_cond->>'operator' as sell_operator
FROM conditions
LIMIT 10;