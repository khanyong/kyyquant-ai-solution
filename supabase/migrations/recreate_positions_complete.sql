-- ====================================================================
-- positions 테이블 완전 재생성
-- 문제: 현재 positions 테이블에 컬럼이 1개만 있음
-- 해결: 테이블 삭제 후 올바른 구조로 재생성
-- ====================================================================

-- 1. 현재 상태 확인
SELECT 
    'BEFORE: positions 테이블 컬럼 수' as status,
    COUNT(*) as column_count
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions';

-- 2. 기존 테이블 완전 삭제 (CASCADE로 관련 객체도 삭제)
DROP TABLE IF EXISTS positions CASCADE;

-- 3. positions 테이블 올바르게 생성
CREATE TABLE IF NOT EXISTS positions (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    strategy_id uuid REFERENCES strategies(id),
    account_no varchar(20),
    stock_code varchar(10) NOT NULL,
    stock_name varchar(100),
    quantity integer NOT NULL,
    available_quantity integer,
    avg_buy_price numeric NOT NULL,
    current_price numeric,
    total_buy_amount numeric,
    current_value numeric,
    profit_loss numeric,
    profit_loss_rate numeric(6,2),
    realized_profit_loss numeric DEFAULT 0,
    stop_loss_price numeric,
    take_profit_price numeric,
    trailing_stop_percent numeric(5,2),
    position_status varchar(20) DEFAULT 'OPEN',
    entry_signal_id uuid REFERENCES trading_signals(id),
    exit_signal_id uuid REFERENCES trading_signals(id),
    opened_at timestamp with time zone DEFAULT now(),
    closed_at timestamp with time zone,
    last_updated timestamp with time zone DEFAULT now()
);

-- 4. 생성 결과 확인
SELECT 
    'AFTER: positions 테이블 컬럼 수' as status,
    COUNT(*) as column_count
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions';

-- 5. 생성된 컬럼 목록 확인
SELECT 
    ordinal_position as seq,
    column_name,
    data_type,
    CASE WHEN is_nullable = 'NO' THEN 'NOT NULL' ELSE 'NULL' END as nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions'
ORDER BY ordinal_position;

-- 6. 중요 컬럼 존재 확인
SELECT 
    'account_no 컬럼' as column_check,
    EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'positions' 
        AND column_name = 'account_no'
    ) as exists;

-- 7. UNIQUE 제약조건 추가
ALTER TABLE positions 
ADD CONSTRAINT positions_unique_key 
UNIQUE(account_no, stock_code, strategy_id);

-- 8. 인덱스 생성
CREATE INDEX idx_positions_account 
ON positions(account_no, position_status);

CREATE INDEX idx_positions_stock 
ON positions(stock_code, position_status);

CREATE INDEX idx_positions_performance 
ON positions(position_status, profit_loss_rate);

CREATE INDEX idx_positions_user 
ON positions(user_id, position_status);

-- 9. 인덱스 생성 확인
SELECT 
    'positions 인덱스' as category,
    COUNT(*) as index_count,
    string_agg(indexname, ', ' ORDER BY indexname) as index_names
FROM pg_indexes
WHERE schemaname = 'public' 
AND tablename = 'positions';

-- 10. 최종 상태
SELECT 
    '✅ positions 테이블 재생성 완료' as final_status,
    'columns: ' || COUNT(*)::text as details
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions';