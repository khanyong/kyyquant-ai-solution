-- ====================================================================
-- STEP 4: 안전한 인덱스만 생성 (account_no 관련 제외)
-- account_no가 있는 인덱스는 모두 제외
-- ====================================================================

-- market_data 인덱스 (안전)
CREATE INDEX IF NOT EXISTS idx_market_data_stock_time 
ON market_data(stock_code, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_market_data_timestamp 
ON market_data(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_market_data_analysis 
ON market_data(stock_code, timestamp DESC, current_price);

-- technical_indicators 인덱스 (안전)
CREATE INDEX IF NOT EXISTS idx_indicators_stock_time 
ON technical_indicators(stock_code, timeframe, calculated_at DESC);

-- kiwoom_orders 인덱스 (account_no 제외)
CREATE INDEX IF NOT EXISTS idx_orders_status 
ON kiwoom_orders(order_status, order_time DESC);

CREATE INDEX IF NOT EXISTS idx_orders_stock 
ON kiwoom_orders(stock_code, order_time DESC);

-- account_no 인덱스는 제외 (오류 원인)
-- CREATE INDEX IF NOT EXISTS idx_orders_account 
-- ON kiwoom_orders(account_no, order_time DESC);

-- account_balance 인덱스도 제외 (account_no 때문)
-- CREATE INDEX IF NOT EXISTS idx_balance_account_time 
-- ON account_balance(account_no, updated_at DESC);

-- strategy_execution_logs 인덱스 (안전)
CREATE INDEX IF NOT EXISTS idx_execution_logs_strategy 
ON strategy_execution_logs(strategy_id, executed_at DESC);

CREATE INDEX IF NOT EXISTS idx_execution_logs_type 
ON strategy_execution_logs(execution_type, executed_at DESC);

-- 생성 결과 확인
SELECT 
    tablename as "테이블",
    COUNT(*) as "인덱스 개수"
FROM pg_indexes
WHERE schemaname = 'public' 
AND tablename IN (
    'market_data',
    'technical_indicators',
    'kiwoom_orders',
    'strategy_execution_logs'
)
GROUP BY tablename
ORDER BY tablename;

SELECT '안전한 인덱스 생성 완료' as status;