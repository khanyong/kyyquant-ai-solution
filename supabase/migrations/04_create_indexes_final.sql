-- ====================================================================
-- STEP 4: 인덱스 생성 (최종 안전 버전)
-- 각 인덱스를 개별적으로 조건 체크 후 생성
-- ====================================================================

-- ====================================================================
-- 1. 기본 테이블 인덱스 (문제 없는 것들)
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
-- 2. positions 테이블 인덱스 (DO 블록으로 안전하게 처리)
-- ====================================================================

-- positions 테이블의 stock_code 인덱스만 생성 (이 컬럼은 확실히 존재)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_name = 'positions') THEN
        
        -- stock_code와 position_status 모두 있는지 확인
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' AND table_name = 'positions' 
                   AND column_name = 'stock_code')
           AND
           EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' AND table_name = 'positions' 
                   AND column_name = 'position_status') THEN
            
            -- 인덱스가 없으면 생성
            IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                          WHERE schemaname = 'public' 
                          AND tablename = 'positions' 
                          AND indexname = 'idx_positions_stock') THEN
                EXECUTE 'CREATE INDEX idx_positions_stock ON positions(stock_code, position_status)';
                RAISE NOTICE 'idx_positions_stock 인덱스 생성됨';
            END IF;
        END IF;
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'positions 테이블 stock_code 인덱스 생성 중 오류: %', SQLERRM;
END $$;

-- account_no가 있는 경우에만 해당 인덱스 생성
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_schema = 'public' 
               AND table_name = 'positions' 
               AND column_name = 'account_no')
       AND
       EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_schema = 'public' 
               AND table_name = 'positions' 
               AND column_name = 'position_status') THEN
        
        -- 동적 SQL로 인덱스 생성
        IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                      WHERE schemaname = 'public' 
                      AND tablename = 'positions' 
                      AND indexname = 'idx_positions_account') THEN
            EXECUTE 'CREATE INDEX idx_positions_account ON positions(account_no, position_status)';
            RAISE NOTICE 'idx_positions_account 인덱스 생성됨';
        END IF;
    ELSE
        RAISE NOTICE 'account_no 또는 position_status 컬럼이 없어 idx_positions_account 인덱스 생략';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'positions 테이블 account_no 인덱스 생성 중 오류: %', SQLERRM;
END $$;

-- profit_loss_rate 인덱스
DO $$
BEGIN
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
                      WHERE schemaname = 'public' 
                      AND tablename = 'positions' 
                      AND indexname = 'idx_positions_performance') THEN
            EXECUTE 'CREATE INDEX idx_positions_performance ON positions(position_status, profit_loss_rate)';
            RAISE NOTICE 'idx_positions_performance 인덱스 생성됨';
        END IF;
    ELSE
        RAISE NOTICE 'profit_loss_rate 또는 position_status 컬럼이 없어 idx_positions_performance 인덱스 생략';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'positions 테이블 performance 인덱스 생성 중 오류: %', SQLERRM;
END $$;

-- ====================================================================
-- 3. 기타 선택적 인덱스
-- ====================================================================

-- trading_signals 인덱스
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_schema = 'public' 
               AND table_name = 'trading_signals' 
               AND column_name = 'executed') THEN
        
        IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                      WHERE schemaname = 'public' 
                      AND tablename = 'trading_signals' 
                      AND indexname = 'idx_signals_execution') THEN
            EXECUTE 'CREATE INDEX idx_signals_execution ON trading_signals(strategy_id, executed, timestamp DESC)';
            RAISE NOTICE 'idx_signals_execution 인덱스 생성됨';
        END IF;
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'trading_signals 인덱스 생성 중 오류: %', SQLERRM;
END $$;

-- ====================================================================
-- 4. 결과 확인
-- ====================================================================

-- 생성된 인덱스 목록
SELECT 
    '생성된 인덱스' as category,
    tablename,
    COUNT(*) as index_count
FROM pg_indexes
WHERE schemaname = 'public' 
AND tablename IN (
    'market_data',
    'technical_indicators',
    'kiwoom_orders',
    'account_balance',
    'strategy_execution_logs',
    'positions'
)
GROUP BY tablename
ORDER BY tablename;

-- positions 테이블 상태
SELECT 
    'positions 테이블 컬럼' as info,
    string_agg(column_name, ', ' ORDER BY ordinal_position) as columns
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions';

SELECT 'STEP 4 완료: 인덱스 생성 완료' as status;