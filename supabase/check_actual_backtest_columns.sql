-- 실제 backtest_results 테이블의 컬럼 확인
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'backtest_results'
ORDER BY ordinal_position;

-- 테이블이 존재하는지 확인
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'backtest_results'
) as table_exists;
