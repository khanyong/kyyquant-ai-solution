-- ====================================================================
-- STEP 4: 인덱스 생성 (수정된 안전한 버전)
-- positions 테이블이 이미 생성되었으므로 안전하게 인덱스 생성
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

-- positions 인덱스 (테이블이 이미 있으므로 직접 생성)
CREATE INDEX IF NOT EXISTS idx_positions_account 
ON positions(account_no, position_status);

CREATE INDEX IF NOT EXISTS idx_positions_stock 
ON positions(stock_code, position_status);

CREATE INDEX IF NOT EXISTS idx_positions_performance 
ON positions(position_status, profit_loss_rate);

-- account_balance 인덱스
CREATE INDEX IF NOT EXISTS idx_balance_account_time 
ON account_balance(account_no, updated_at DESC);

-- strategy_execution_logs 인덱스
CREATE INDEX IF NOT EXISTS idx_execution_logs_strategy 
ON strategy_execution_logs(strategy_id, executed_at DESC);

CREATE INDEX IF NOT EXISTS idx_execution_logs_type 
ON strategy_execution_logs(execution_type, executed_at DESC);

-- alerts 인덱스 (테이블이 있는 경우만)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_name = 'alerts') THEN
        CREATE INDEX IF NOT EXISTS idx_alerts_user 
        ON alerts(user_id, is_read, created_at DESC);
    END IF;
END $$;

-- trading_signals 인덱스
DO $$
BEGIN
    -- executed 컬럼이 있는 경우
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_schema = 'public' 
               AND table_name = 'trading_signals' 
               AND column_name = 'executed') THEN
        CREATE INDEX IF NOT EXISTS idx_signals_execution 
        ON trading_signals(strategy_id, executed, timestamp DESC);
    END IF;
    
    -- created_at 컬럼이 있는 경우
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_schema = 'public' 
               AND table_name = 'trading_signals' 
               AND column_name = 'created_at') THEN
        CREATE INDEX IF NOT EXISTS idx_signals_created_at 
        ON trading_signals(created_at DESC);
    END IF;
END $$;

-- orders 테이블 인덱스 (테이블이 있는 경우)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_name = 'orders') THEN
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' 
                   AND table_name = 'orders' 
                   AND column_name = 'order_time') THEN
            CREATE INDEX IF NOT EXISTS idx_orders_order_time 
            ON orders(order_time DESC);
        END IF;
    END IF;
END $$;

-- 완료 메시지
SELECT '인덱스 생성 완료' as status;