-- ====================================================================
-- 테이블 생성 확인 스크립트
-- 필수 테이블들이 제대로 생성되었는지 확인
-- ====================================================================

-- 1. 생성된 테이블 목록
SELECT '=== 생성된 테이블 ===' as section;
SELECT table_name, 
       CASE 
           WHEN table_name IS NOT NULL THEN '✓ 생성됨'
           ELSE '✗ 없음'
       END as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'market_data',
    'technical_indicators', 
    'kiwoom_orders',
    'account_balance',
    'strategy_execution_logs',
    'trading_signals',
    'strategies'
)
ORDER BY table_name;

-- 2. trading_signals 테이블 새 컬럼 확인
SELECT '=== trading_signals 새 컬럼 ===' as section;
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'trading_signals'
AND column_name IN (
    'signal_strength',
    'confidence_score',
    'entry_price',
    'target_price',
    'stop_loss_price',
    'executed'
)
ORDER BY column_name;

-- 3. strategies 테이블 새 컬럼 확인  
SELECT '=== strategies 새 컬럼 ===' as section;
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'strategies'
AND column_name IN (
    'conditions',
    'target_stocks',
    'position_size',
    'auto_execute'
)
ORDER BY column_name;

-- 4. 인덱스 확인
SELECT '=== 생성된 인덱스 ===' as section;
SELECT tablename, COUNT(*) as index_count
FROM pg_indexes
WHERE schemaname = 'public' 
AND tablename IN (
    'market_data',
    'technical_indicators',
    'kiwoom_orders',
    'account_balance',
    'strategy_execution_logs'
)
GROUP BY tablename
ORDER BY tablename;

-- 5. 전체 상태 요약
SELECT '=== 전체 요약 ===' as section;
SELECT 
    (SELECT COUNT(*) FROM information_schema.tables 
     WHERE table_schema = 'public' 
     AND table_name IN ('market_data','technical_indicators','kiwoom_orders','account_balance','strategy_execution_logs')
    ) as new_tables_created,
    (SELECT COUNT(*) FROM information_schema.columns
     WHERE table_schema = 'public' 
     AND table_name = 'trading_signals'
     AND column_name IN ('signal_strength','confidence_score','entry_price','target_price','stop_loss_price','executed')
    ) as trading_signals_new_columns,
    (SELECT COUNT(*) FROM information_schema.columns
     WHERE table_schema = 'public' 
     AND table_name = 'strategies'
     AND column_name IN ('conditions','target_stocks','position_size','auto_execute')
    ) as strategies_new_columns;