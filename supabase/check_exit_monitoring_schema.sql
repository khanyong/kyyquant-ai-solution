-- =====================================================
-- strategy_monitoring 테이블 스키마 확인
-- =====================================================

-- 1. 테이블 컬럼 확인
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'strategy_monitoring'
ORDER BY ordinal_position;

-- 2. 인덱스 확인
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'strategy_monitoring'
ORDER BY indexname;

-- 3. 실제 데이터 확인 (샘플 5개)
SELECT
    stock_code,
    stock_name,
    condition_match_score,
    exit_condition_match_score,
    is_near_entry,
    is_near_exit,
    is_held,
    updated_at
FROM strategy_monitoring
ORDER BY updated_at DESC
LIMIT 5;

-- 4. 보유 종목 중 매도 대기 종목 확인
SELECT
    stock_code,
    stock_name,
    current_price,
    exit_condition_match_score,
    is_held,
    updated_at
FROM strategy_monitoring
WHERE is_held = true
  AND is_near_exit = true
ORDER BY exit_condition_match_score DESC;
