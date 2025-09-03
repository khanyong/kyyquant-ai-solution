-- ====================================================================
-- positions 테이블 문제 해결
-- 테이블을 삭제하고 다시 생성
-- ====================================================================

-- 1. 기존 positions 테이블 관련 모든 것 삭제
DROP TABLE IF EXISTS positions CASCADE;

-- 2. positions 테이블 새로 생성 (account_no 포함)
CREATE TABLE positions (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    strategy_id uuid REFERENCES strategies(id),
    account_no varchar(20),  -- account_no 명확히 포함
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

-- 3. 테이블 생성 확인
SELECT 
    'positions 테이블 재생성 완료' as status,
    COUNT(*) as column_count
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions';

-- 4. account_no 컬럼 확인
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions'
AND column_name IN ('account_no', 'stock_code', 'position_status', 'profit_loss_rate')
ORDER BY column_name;

-- 5. 이제 인덱스 생성 (오류 없이)
CREATE INDEX idx_positions_account 
ON positions(account_no, position_status);

CREATE INDEX idx_positions_stock 
ON positions(stock_code, position_status);

CREATE INDEX idx_positions_performance 
ON positions(position_status, profit_loss_rate);

-- 6. 생성된 인덱스 확인
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public' 
AND tablename = 'positions'
ORDER BY indexname;

SELECT 'positions 테이블 및 인덱스 생성 완료!' as final_status;