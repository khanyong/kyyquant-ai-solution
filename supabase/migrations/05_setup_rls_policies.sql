-- ====================================================================
-- STEP 5: RLS (Row Level Security) 정책 설정
-- ====================================================================

-- RLS 활성화
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE technical_indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE kiwoom_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategy_execution_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE account_balance ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;

-- 시장 데이터는 모든 사용자가 읽기 가능
DROP POLICY IF EXISTS "market_data_read_all" ON market_data;
CREATE POLICY "market_data_read_all" ON market_data
    FOR SELECT USING (true);

-- 인증된 사용자만 시장 데이터 쓰기 가능
DROP POLICY IF EXISTS "market_data_write_authenticated" ON market_data;
CREATE POLICY "market_data_write_authenticated" ON market_data
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- 기술적 지표는 모든 사용자가 읽기 가능
DROP POLICY IF EXISTS "indicators_read_all" ON technical_indicators;
CREATE POLICY "indicators_read_all" ON technical_indicators
    FOR SELECT USING (true);

-- 주문은 해당 전략 소유자만 접근 가능
DROP POLICY IF EXISTS "orders_user_own" ON kiwoom_orders;
CREATE POLICY "orders_user_own" ON kiwoom_orders
    FOR ALL USING (
        strategy_id IN (
            SELECT id FROM strategies WHERE user_id = auth.uid()
        )
        OR strategy_id IS NULL
    );

-- 알림은 본인 것만 접근 가능
DROP POLICY IF EXISTS "alerts_user_own" ON alerts;
CREATE POLICY "alerts_user_own" ON alerts
    FOR ALL USING (auth.uid() = user_id OR user_id IS NULL);

-- 설정은 본인 것만 접근 가능
DROP POLICY IF EXISTS "settings_user_own" ON system_settings;
CREATE POLICY "settings_user_own" ON system_settings
    FOR ALL USING (auth.uid() = user_id OR user_id IS NULL);

-- 계좌 잔고는 본인 것만 접근 가능
DROP POLICY IF EXISTS "balance_user_own" ON account_balance;
CREATE POLICY "balance_user_own" ON account_balance
    FOR ALL USING (auth.uid() = user_id OR user_id IS NULL);

-- 포지션은 본인 것만 접근 가능
DROP POLICY IF EXISTS "positions_user_own" ON positions;
CREATE POLICY "positions_user_own" ON positions
    FOR ALL USING (auth.uid() = user_id OR user_id IS NULL);

-- 전략 실행 로그는 해당 전략 소유자만 접근 가능
DROP POLICY IF EXISTS "execution_logs_user_own" ON strategy_execution_logs;
CREATE POLICY "execution_logs_user_own" ON strategy_execution_logs
    FOR ALL USING (
        strategy_id IN (
            SELECT id FROM strategies WHERE user_id = auth.uid()
        )
        OR strategy_id IS NULL
    );