-- 특정 전략 ID의 설정 확인
-- strategy_id: 88d01e47-c979-4e80-bef8-746a53f3bbca

-- 1. 전략 기본 정보
SELECT
    id,
    name,
    config->>'templateId' as template_id,
    created_at,
    updated_at
FROM strategies
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- 2. 전략의 indicators 확인
SELECT
    id,
    name,
    jsonb_pretty(config->'indicators') as indicators
FROM strategies
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- 3. 전략의 buyConditions 확인
SELECT
    id,
    name,
    jsonb_pretty(config->'buyConditions') as buy_conditions
FROM strategies
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- 4. 전략의 sellConditions 확인
SELECT
    id,
    name,
    jsonb_pretty(config->'sellConditions') as sell_conditions
FROM strategies
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- 5. 전체 config 확인
SELECT
    id,
    name,
    jsonb_pretty(config) as full_config
FROM strategies
WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca';

-- 6. 이 전략과 같은 템플릿의 다른 전략들 비교
SELECT
    id,
    name,
    config->>'templateId' as template_id,
    jsonb_array_length(COALESCE(config->'indicators', '[]'::jsonb)) as indicator_count,
    jsonb_array_length(COALESCE(config->'buyConditions', '[]'::jsonb)) as buy_count,
    jsonb_array_length(COALESCE(config->'sellConditions', '[]'::jsonb)) as sell_count
FROM strategies
WHERE config->>'templateId' = (
    SELECT config->>'templateId'
    FROM strategies
    WHERE id = '88d01e47-c979-4e80-bef8-746a53f3bbca'
)
LIMIT 5;