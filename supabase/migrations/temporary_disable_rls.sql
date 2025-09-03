-- ====================================================================
-- 테스트를 위한 임시 RLS 비활성화
-- 주의: 테스트 후 다시 활성화해야 함
-- ====================================================================

-- RLS 비활성화
ALTER TABLE market_data DISABLE ROW LEVEL SECURITY;
ALTER TABLE technical_indicators DISABLE ROW LEVEL SECURITY;
ALTER TABLE kiwoom_orders DISABLE ROW LEVEL SECURITY;
ALTER TABLE account_balance DISABLE ROW LEVEL SECURITY;
ALTER TABLE strategy_execution_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE positions DISABLE ROW LEVEL SECURITY;

-- 상태 확인
SELECT 
    tablename,
    CASE 
        WHEN rowsecurity THEN 'ENABLED'
        ELSE 'DISABLED'
    END as rls_status
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN (
    'market_data',
    'technical_indicators',
    'kiwoom_orders',
    'account_balance',
    'strategy_execution_logs',
    'positions'
)
ORDER BY tablename;

SELECT 'RLS 임시 비활성화 완료 - 테스트 가능' as status;