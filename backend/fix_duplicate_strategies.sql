-- ============================================================
-- 중복 전략 삭제 및 정리
-- ============================================================

-- 1. 중복 확인: 같은 이름의 전략 찾기
SELECT
    name,
    COUNT(*) as count,
    array_agg(id ORDER BY created_at) as ids,
    array_agg(created_at ORDER BY created_at) as created_times
FROM strategies
GROUP BY name
HAVING COUNT(*) > 1;

-- 2. 잘못된 형식의 전략 찾기 (type 사용하는 전략)
SELECT
    id,
    name,
    created_at,
    config->'indicators'->0 as first_indicator
FROM strategies
WHERE
    config->'indicators'->0 ? 'type'  -- 'type' 필드를 사용하는 전략
ORDER BY created_at;

-- 3. 오래된 MACD 시그널 전략 삭제 (type을 사용하는 것)
DELETE FROM strategies
WHERE
    name = '[템플릿] MACD 시그널'
    AND config->'indicators'->0 ? 'type';

-- 4. 남은 전략 확인
SELECT
    name,
    created_at,
    config->'indicators'->0->>'name' as first_indicator_name,
    config->'indicators'->0->>'type' as first_indicator_type
FROM strategies
ORDER BY name, created_at;

-- 5. 최종 검증: 모든 전략이 'name' 필드를 사용하는지 확인
SELECT
    name,
    CASE
        WHEN config->'indicators'->0 ? 'name' THEN '✅ OK'
        WHEN config->'indicators'->0 ? 'type' THEN '❌ BAD (using type)'
        ELSE '⚠️  UNKNOWN'
    END as status
FROM strategies
ORDER BY name;
