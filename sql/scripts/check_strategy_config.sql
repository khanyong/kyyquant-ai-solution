-- ============================================================
-- 전략 config 확인 및 수정
-- ============================================================

-- 1. 최근 전략 목록 확인 (config의 indicators 포함)
SELECT
    id,
    name,
    created_at,
    config->'indicators' as indicators,
    jsonb_array_length(COALESCE(config->'indicators', '[]'::jsonb)) as indicator_count,
    config->'buyConditions' as buy_conditions,
    config->'sellConditions' as sell_conditions
FROM strategies
ORDER BY created_at DESC
LIMIT 10;


-- 2. 특정 전략의 상세 config 확인 (strategy_id 교체 필요)
SELECT
    id,
    name,
    config
FROM strategies
WHERE id = 'YOUR_STRATEGY_ID_HERE';  -- ← 실제 ID로 교체


-- 3. MACD를 사용하는데 indicators에 없는 전략 찾기
SELECT
    id,
    name,
    created_at,
    config->'indicators' as indicators
FROM strategies
WHERE
    -- buyConditions 또는 sellConditions에 'macd' 문자열 포함
    (
        config::text LIKE '%macd%'
        OR config::text LIKE '%macd_signal%'
    )
    AND
    -- 하지만 indicators 배열에 macd가 없음
    NOT EXISTS (
        SELECT 1
        FROM jsonb_array_elements(config->'indicators') AS ind
        WHERE ind->>'name' = 'macd'
    )
ORDER BY created_at DESC;


-- 4. MACD 지표 추가 (strategy_id 교체 필요)
UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{indicators}',
        COALESCE(config->'indicators', '[]'::jsonb) ||
        '[{
            "name": "macd",
            "type": "MACD",
            "params": {
                "fast": 12,
                "slow": 26,
                "signal": 9
            }
        }]'::jsonb
    ),
    updated_at = NOW()
WHERE id = 'YOUR_STRATEGY_ID_HERE';  -- ← 실제 ID로 교체

-- 확인
SELECT
    id,
    name,
    config->'indicators' as indicators
FROM strategies
WHERE id = 'YOUR_STRATEGY_ID_HERE';


-- 5. 모든 MACD 사용 전략에 일괄 추가 (주의: 실행 전 확인!)
-- 먼저 영향받을 전략 확인
SELECT
    id,
    name,
    config->'indicators' as current_indicators
FROM strategies
WHERE
    (config::text LIKE '%macd%' OR config::text LIKE '%macd_signal%')
    AND NOT EXISTS (
        SELECT 1
        FROM jsonb_array_elements(config->'indicators') AS ind
        WHERE ind->>'name' = 'macd'
    );

-- 일괄 업데이트 (위 쿼리 결과 확인 후 실행)
/*
UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{indicators}',
        COALESCE(config->'indicators', '[]'::jsonb) ||
        '[{
            "name": "macd",
            "type": "MACD",
            "params": {
                "fast": 12,
                "slow": 26,
                "signal": 9
            }
        }]'::jsonb
    ),
    updated_at = NOW()
WHERE
    (config::text LIKE '%macd%' OR config::text LIKE '%macd_signal%')
    AND NOT EXISTS (
        SELECT 1
        FROM jsonb_array_elements(config->'indicators') AS ind
        WHERE ind->>'name' = 'macd'
    );
*/


-- 6. 결과 확인 - 이제 모든 필드가 매치되는지 체크
SELECT
    s.id,
    s.name,

    -- indicators 배열의 지표명들
    (
        SELECT jsonb_agg(ind->>'name')
        FROM jsonb_array_elements(s.config->'indicators') AS ind
    ) as registered_indicators,

    -- buyConditions에서 사용하는 컬럼들 (간단한 예시)
    s.config->'buyConditions' as buy_conditions,

    -- 검증 결과
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM jsonb_array_elements(s.config->'indicators') AS ind
            WHERE ind->>'name' = 'macd'
        ) THEN '✓ MACD registered'
        ELSE '✗ MACD missing'
    END as validation_status

FROM strategies s
WHERE s.config::text LIKE '%macd%'
ORDER BY s.created_at DESC
LIMIT 10;