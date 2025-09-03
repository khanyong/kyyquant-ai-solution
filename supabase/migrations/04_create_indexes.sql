-- ====================================================================
-- STEP 4: 인덱스 생성 (성능 최적화)
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

-- positions 인덱스 (테이블과 컬럼 존재 확인 후)
DO $$
BEGIN
    -- positions 테이블이 존재하는지 확인
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_name = 'positions') THEN
        
        -- account_no 컬럼이 있으면 인덱스 생성
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' 
                   AND table_name = 'positions' 
                   AND column_name = 'account_no') THEN
            
            -- 인덱스가 없으면 생성
            IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                          WHERE schemaname = 'public' 
                          AND tablename = 'positions' 
                          AND indexname = 'idx_positions_account') THEN
                CREATE INDEX idx_positions_account 
                ON positions(account_no, position_status);
            END IF;
        END IF;
        
        -- stock_code 인덱스
        IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                      WHERE schemaname = 'public' 
                      AND tablename = 'positions' 
                      AND indexname = 'idx_positions_stock') THEN
            CREATE INDEX idx_positions_stock 
            ON positions(stock_code, position_status);
        END IF;
        
        -- profit_loss_rate 컬럼 확인 후 인덱스 생성
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' 
                   AND table_name = 'positions' 
                   AND column_name = 'profit_loss_rate') THEN
            
            IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                          WHERE schemaname = 'public' 
                          AND tablename = 'positions' 
                          AND indexname = 'idx_positions_performance') THEN
                CREATE INDEX idx_positions_performance 
                ON positions(position_status, profit_loss_rate);
            END IF;
        END IF;
    END IF;
END $$;

-- account_balance 인덱스
CREATE INDEX IF NOT EXISTS idx_balance_account_time 
ON account_balance(account_no, updated_at DESC);

-- strategy_execution_logs 인덱스
CREATE INDEX IF NOT EXISTS idx_execution_logs_strategy 
ON strategy_execution_logs(strategy_id, executed_at DESC);

CREATE INDEX IF NOT EXISTS idx_execution_logs_type 
ON strategy_execution_logs(execution_type, executed_at DESC);

-- alerts 인덱스
CREATE INDEX IF NOT EXISTS idx_alerts_user 
ON alerts(user_id, is_read, created_at DESC);

-- trading_signals 인덱스
CREATE INDEX IF NOT EXISTS idx_signals_execution 
ON trading_signals(strategy_id, executed, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_signals_created_at 
ON trading_signals(created_at DESC) WHERE created_at IS NOT NULL;

-- orders 인덱스 (orders 테이블이 있는 경우)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_name='orders') THEN
        CREATE INDEX IF NOT EXISTS idx_orders_order_time 
        ON orders(order_time DESC) WHERE order_time IS NOT NULL;
    END IF;
END $$;