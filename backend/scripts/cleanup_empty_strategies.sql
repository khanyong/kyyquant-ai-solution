-- ============================================
-- Empty Config 전략 정리 스크립트
-- ============================================

-- 1. 먼저 config가 비어있는 전략 확인
SELECT
    id,
    name,
    user_id,
    created_at,
    config,
    CASE
        WHEN config IS NULL THEN 'NULL'
        WHEN config::text = '{}' THEN 'EMPTY_OBJECT'
        WHEN config::text = 'null' THEN 'NULL_STRING'
        ELSE 'HAS_CONFIG'
    END as config_status
FROM strategies
WHERE
    config IS NULL
    OR config::text = '{}'
    OR config::text = 'null'
ORDER BY created_at DESC;

-- 2. 관련 테이블 확인 (foreign key 제약 확인)
-- strategies 테이블을 참조하는 테이블들:
-- - backtest_results (strategy_id)
-- - user_favorites (strategy_id)
-- - strategy_performance (strategy_id)
-- - trading_signals (strategy_id)

-- 3. 삭제할 전략과 관련된 데이터 개수 확인
WITH empty_strategies AS (
    SELECT id
    FROM strategies
    WHERE config IS NULL
       OR config::text = '{}'
       OR config::text = 'null'
)
SELECT
    'strategies' as table_name,
    COUNT(*) as count
FROM empty_strategies
UNION ALL
SELECT
    'backtest_results' as table_name,
    COUNT(*) as count
FROM backtest_results
WHERE strategy_id IN (SELECT id FROM empty_strategies)
UNION ALL
SELECT
    'user_favorites' as table_name,
    COUNT(*) as count
FROM user_favorites
WHERE strategy_id IN (SELECT id FROM empty_strategies)
UNION ALL
SELECT
    'strategy_performance' as table_name,
    COUNT(*) as count
FROM strategy_performance
WHERE strategy_id IN (SELECT id FROM empty_strategies)
UNION ALL
SELECT
    'trading_signals' as table_name,
    COUNT(*) as count
FROM trading_signals
WHERE strategy_id IN (SELECT id FROM empty_strategies);

-- ============================================
-- 삭제 스크립트 (주의: 순서 중요!)
-- ============================================

-- 4. 트랜잭션으로 안전하게 삭제
BEGIN;

-- 4.1. 먼저 참조하는 테이블의 데이터 삭제
DELETE FROM trading_signals
WHERE strategy_id IN (
    SELECT id FROM strategies
    WHERE config IS NULL
       OR config::text = '{}'
       OR config::text = 'null'
);

DELETE FROM strategy_performance
WHERE strategy_id IN (
    SELECT id FROM strategies
    WHERE config IS NULL
       OR config::text = '{}'
       OR config::text = 'null'
);

DELETE FROM user_favorites
WHERE strategy_id IN (
    SELECT id FROM strategies
    WHERE config IS NULL
       OR config::text = '{}'
       OR config::text = 'null'
);

DELETE FROM backtest_results
WHERE strategy_id IN (
    SELECT id FROM strategies
    WHERE config IS NULL
       OR config::text = '{}'
       OR config::text = 'null'
);

-- 4.2. 마지막으로 strategies 테이블에서 삭제
DELETE FROM strategies
WHERE config IS NULL
   OR config::text = '{}'
   OR config::text = 'null';

-- 5. 변경사항 확인 (실제 적용 전)
-- ROLLBACK;  -- 테스트 시 사용

-- 6. 실제 적용
-- COMMIT;  -- 확인 후 주석 해제하여 실행

-- ============================================
-- 대안: CASCADE 옵션 사용 (더 위험함)
-- ============================================

-- ALTER TABLE backtest_results
-- DROP CONSTRAINT backtest_results_strategy_id_fkey,
-- ADD CONSTRAINT backtest_results_strategy_id_fkey
--   FOREIGN KEY (strategy_id)
--   REFERENCES strategies(id)
--   ON DELETE CASCADE;

-- 이후 간단히:
-- DELETE FROM strategies
-- WHERE config IS NULL OR config::text = '{}' OR config::text = 'null';