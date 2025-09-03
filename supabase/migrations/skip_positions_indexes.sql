-- ====================================================================
-- positions 관련 인덱스를 제외한 모든 인덱스 생성
-- account_no 오류를 완전히 회피
-- ====================================================================

-- market_data 인덱스
CREATE INDEX IF NOT EXISTS idx_market_data_stock_time 
ON market_data(stock_code, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_market_data_timestamp 
ON market_data(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_market_data_analysis 
ON market_data(stock_code, timestamp DESC, current_price);

-- technical_indicators 인덱스
CREATE INDEX IF NOT EXISTS idx_indicators_stock_time 
ON technical_indicators(stock_code, timeframe, calculated_at DESC);

-- kiwoom_orders 인덱스
CREATE INDEX IF NOT EXISTS idx_orders_status 
ON kiwoom_orders(order_status, order_time DESC);

CREATE INDEX IF NOT EXISTS idx_orders_stock 
ON kiwoom_orders(stock_code, order_time DESC);

CREATE INDEX IF NOT EXISTS idx_orders_account 
ON kiwoom_orders(account_no, order_time DESC);

-- account_balance 인덱스
CREATE INDEX IF NOT EXISTS idx_balance_account_time 
ON account_balance(account_no, updated_at DESC);

-- strategy_execution_logs 인덱스
CREATE INDEX IF NOT EXISTS idx_execution_logs_strategy 
ON strategy_execution_logs(strategy_id, executed_at DESC);

CREATE INDEX IF NOT EXISTS idx_execution_logs_type 
ON strategy_execution_logs(execution_type, executed_at DESC);

-- positions 테이블 인덱스는 나중에 수동으로 추가
-- 아래 쿼리로 positions 테이블 상태 확인
SELECT 
    'positions 테이블 상태' as info,
    COUNT(*) as column_count,
    string_agg(column_name, ', ' ORDER BY ordinal_position) as all_columns
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions';

-- 생성된 인덱스 확인
SELECT 
    tablename as "테이블",
    COUNT(*) as "인덱스 개수"
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

SELECT '인덱스 생성 완료 (positions 제외)' as status;