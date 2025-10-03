-- 백엔드가 로드하는 정확한 전략 찾기
SELECT
    id,
    name,
    created_at,
    config->'indicators'->0 as first_indicator,
    jsonb_pretty(config) as config_full
FROM strategies
WHERE id = 'f77a432a-e2a8-45ef-b2ae-7f5a820fc626';

-- 모든 MACD 시그널 전략 찾기
SELECT
    id,
    name,
    created_at,
    config->'indicators'->0->>'name' as indicator_name,
    config->'indicators'->0->>'type' as indicator_type
FROM strategies
WHERE name LIKE '%MACD%'
ORDER BY created_at;

-- 잘못된 형식(type 사용) 전략 찾기
SELECT
    id,
    name,
    created_at,
    config->'indicators'->0 as first_indicator
FROM strategies
WHERE config->'indicators'->0 ? 'type'
ORDER BY created_at;

-- 위 잘못된 전략 삭제
DELETE FROM strategies
WHERE config->'indicators'->0 ? 'type';

-- 최종 확인
SELECT
    id,
    name,
    created_at,
    CASE
        WHEN config->'indicators'->0 ? 'name' THEN '✅ OK'
        WHEN config->'indicators'->0 ? 'type' THEN '❌ BAD'
        ELSE '⚠️  UNKNOWN'
    END as status
FROM strategies
ORDER BY name, created_at;
