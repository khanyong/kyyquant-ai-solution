-- ====================================================================
-- 테이블 상태 확인 스크립트
-- 현재 데이터베이스 상태를 파악하기 위한 쿼리
-- ====================================================================

-- 1. positions 테이블 존재 여부 확인
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'positions'
        ) THEN 'positions 테이블이 존재합니다'
        ELSE 'positions 테이블이 없습니다'
    END as positions_status;

-- 2. positions 테이블의 모든 컬럼 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions'
ORDER BY ordinal_position;

-- 3. 다른 주요 테이블들의 존재 여부
SELECT 
    table_name,
    CASE 
        WHEN table_name IS NOT NULL THEN '존재'
        ELSE '없음'
    END as status
FROM (
    VALUES 
        ('market_data'),
        ('technical_indicators'),
        ('kiwoom_orders'),
        ('positions'),
        ('account_balance'),
        ('strategy_execution_logs'),
        ('alerts'),
        ('system_settings'),
        ('strategies'),
        ('trading_signals'),
        ('orders'),
        ('backtest_results')
) AS required_tables(table_name)
LEFT JOIN information_schema.tables ist 
    ON ist.table_schema = 'public' 
    AND ist.table_name = required_tables.table_name
ORDER BY required_tables.table_name;

-- 4. positions 테이블의 제약조건 확인
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint
WHERE conrelid = 'positions'::regclass;

-- 5. positions 테이블의 인덱스 확인  
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public' 
AND tablename = 'positions';