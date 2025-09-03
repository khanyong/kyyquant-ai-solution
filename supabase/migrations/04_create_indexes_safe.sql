-- ====================================================================
-- STEP 4: 인덱스 생성 (완전히 안전한 버전)
-- account_no 컬럼 확인 후 인덱스 생성
-- ====================================================================

-- 먼저 account_no 컬럼 확인 및 추가
DO $$
BEGIN
    -- positions 테이블에 account_no 컬럼이 없으면 추가
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_name = 'positions') THEN
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema = 'public' 
                       AND table_name = 'positions' 
                       AND column_name = 'account_no') THEN
            ALTER TABLE positions ADD COLUMN account_no varchar(20);
            RAISE NOTICE 'positions 테이블에 account_no 컬럼 추가됨';
        END IF;
    END IF;
END $$;

-- ====================================================================
-- 기본 테이블 인덱스 (안전함)
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

-- ====================================================================
-- positions 테이블 인덱스 (조건부 생성)
-- ====================================================================
DO $$
BEGIN
    -- positions 테이블과 컬럼들이 모두 존재하는지 확인
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_name = 'positions') THEN
        
        -- stock_code 인덱스 (기본 컬럼이므로 안전)
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' 
                   AND table_name = 'positions' 
                   AND column_name = 'stock_code') THEN
            
            IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                          WHERE tablename = 'positions' 
                          AND indexname = 'idx_positions_stock') THEN
                CREATE INDEX idx_positions_stock 
                ON positions(stock_code, position_status);
                RAISE NOTICE 'idx_positions_stock 인덱스 생성됨';
            END IF;
        END IF;
        
        -- account_no 인덱스 (컬럼 있을 때만)
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' 
                   AND table_name = 'positions' 
                   AND column_name = 'account_no') 
           AND 
           EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' 
                   AND table_name = 'positions' 
                   AND column_name = 'position_status') THEN
            
            IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                          WHERE tablename = 'positions' 
                          AND indexname = 'idx_positions_account') THEN
                CREATE INDEX idx_positions_account 
                ON positions(account_no, position_status);
                RAISE NOTICE 'idx_positions_account 인덱스 생성됨';
            END IF;
        END IF;
        
        -- profit_loss_rate 인덱스 (컬럼 있을 때만)
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' 
                   AND table_name = 'positions' 
                   AND column_name = 'profit_loss_rate') 
           AND 
           EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' 
                   AND table_name = 'positions' 
                   AND column_name = 'position_status') THEN
            
            IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                          WHERE tablename = 'positions' 
                          AND indexname = 'idx_positions_performance') THEN
                CREATE INDEX idx_positions_performance 
                ON positions(position_status, profit_loss_rate);
                RAISE NOTICE 'idx_positions_performance 인덱스 생성됨';
            END IF;
        END IF;
    END IF;
END $$;

-- ====================================================================
-- 기타 선택적 테이블 인덱스
-- ====================================================================

-- alerts 인덱스 (테이블 있을 때만)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_name = 'alerts') THEN
        CREATE INDEX IF NOT EXISTS idx_alerts_user 
        ON alerts(user_id, is_read, created_at DESC);
    END IF;
END $$;

-- trading_signals 인덱스 (컬럼 있을 때만)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_name = 'trading_signals') THEN
        
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
    END IF;
END $$;

-- 완료 상태 확인
SELECT 
    'positions 테이블 account_no 상태' as check_item,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'positions' 
            AND column_name = 'account_no'
        ) THEN '✓ account_no 컬럼 있음'
        ELSE '✗ account_no 컬럼 없음'
    END as status
UNION ALL
SELECT 
    'positions 인덱스' as check_item,
    COUNT(*)::text || '개 생성됨' as status
FROM pg_indexes 
WHERE tablename = 'positions';