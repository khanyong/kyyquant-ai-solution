-- ====================================================================
-- STEP 5: RLS (Row Level Security) 정책 설정 (안전한 버전)
-- 테이블 존재 여부를 확인하고 정책 설정
-- ====================================================================

-- RLS 활성화 (EXISTS 체크 포함)
DO $$
BEGIN
    -- market_data
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'market_data') THEN
        ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
    END IF;
    
    -- technical_indicators
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'technical_indicators') THEN
        ALTER TABLE technical_indicators ENABLE ROW LEVEL SECURITY;
    END IF;
    
    -- kiwoom_orders
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'kiwoom_orders') THEN
        ALTER TABLE kiwoom_orders ENABLE ROW LEVEL SECURITY;
    END IF;
    
    -- account_balance
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'account_balance') THEN
        ALTER TABLE account_balance ENABLE ROW LEVEL SECURITY;
    END IF;
    
    -- strategy_execution_logs
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'strategy_execution_logs') THEN
        ALTER TABLE strategy_execution_logs ENABLE ROW LEVEL SECURITY;
    END IF;
    
    -- positions
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'positions') THEN
        ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
    END IF;
    
    -- alerts (있는 경우만)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'alerts') THEN
        ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
    END IF;
    
    -- system_settings (있는 경우만)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'system_settings') THEN
        ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;
    END IF;
END $$;

-- ====================================================================
-- 정책 생성 (기존 정책 삭제 후 생성)
-- ====================================================================

-- market_data 정책
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'market_data') THEN
        -- 기존 정책 삭제
        DROP POLICY IF EXISTS "market_data_read_all" ON market_data;
        DROP POLICY IF EXISTS "market_data_write_authenticated" ON market_data;
        
        -- 새 정책 생성
        CREATE POLICY "market_data_read_all" ON market_data
            FOR SELECT USING (true);
        
        CREATE POLICY "market_data_write_authenticated" ON market_data
            FOR INSERT WITH CHECK (auth.role() = 'authenticated');
    END IF;
END $$;

-- technical_indicators 정책
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'technical_indicators') THEN
        DROP POLICY IF EXISTS "indicators_read_all" ON technical_indicators;
        
        CREATE POLICY "indicators_read_all" ON technical_indicators
            FOR SELECT USING (true);
    END IF;
END $$;

-- kiwoom_orders 정책
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'kiwoom_orders') THEN
        DROP POLICY IF EXISTS "orders_user_own" ON kiwoom_orders;
        
        CREATE POLICY "orders_user_own" ON kiwoom_orders
            FOR ALL USING (
                strategy_id IN (
                    SELECT id FROM strategies WHERE user_id = auth.uid()
                )
                OR strategy_id IS NULL
                OR auth.uid() IS NOT NULL  -- 인증된 사용자는 모두 접근 가능 (개발 단계)
            );
    END IF;
END $$;

-- account_balance 정책
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'account_balance') THEN
        DROP POLICY IF EXISTS "balance_user_own" ON account_balance;
        
        CREATE POLICY "balance_user_own" ON account_balance
            FOR ALL USING (
                auth.uid() = user_id 
                OR user_id IS NULL
                OR auth.uid() IS NOT NULL  -- 인증된 사용자는 모두 접근 가능 (개발 단계)
            );
    END IF;
END $$;

-- positions 정책
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'positions') THEN
        DROP POLICY IF EXISTS "positions_user_own" ON positions;
        
        CREATE POLICY "positions_user_own" ON positions
            FOR ALL USING (
                auth.uid() = user_id 
                OR user_id IS NULL
                OR auth.uid() IS NOT NULL  -- 인증된 사용자는 모두 접근 가능 (개발 단계)
            );
    END IF;
END $$;

-- strategy_execution_logs 정책
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'strategy_execution_logs') THEN
        DROP POLICY IF EXISTS "execution_logs_user_own" ON strategy_execution_logs;
        
        CREATE POLICY "execution_logs_user_own" ON strategy_execution_logs
            FOR ALL USING (
                strategy_id IN (
                    SELECT id FROM strategies WHERE user_id = auth.uid()
                )
                OR strategy_id IS NULL
                OR auth.uid() IS NOT NULL  -- 인증된 사용자는 모두 접근 가능 (개발 단계)
            );
    END IF;
END $$;

-- alerts 정책 (테이블이 있는 경우만)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'alerts') THEN
        DROP POLICY IF EXISTS "alerts_user_own" ON alerts;
        
        CREATE POLICY "alerts_user_own" ON alerts
            FOR ALL USING (
                auth.uid() = user_id 
                OR user_id IS NULL
            );
    END IF;
END $$;

-- system_settings 정책 (테이블이 있는 경우만)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'system_settings') THEN
        DROP POLICY IF EXISTS "settings_user_own" ON system_settings;
        
        CREATE POLICY "settings_user_own" ON system_settings
            FOR ALL USING (
                auth.uid() = user_id 
                OR user_id IS NULL
            );
    END IF;
END $$;

-- 완료 메시지
SELECT 'RLS 정책 설정 완료' as status;

-- 설정된 정책 확인
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
AND tablename IN ('market_data', 'technical_indicators', 'kiwoom_orders', 'positions', 'account_balance')
ORDER BY tablename, policyname;