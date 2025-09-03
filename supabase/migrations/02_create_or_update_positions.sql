-- ====================================================================
-- STEP 2: positions 테이블 생성 또는 수정
-- ====================================================================

-- positions 테이블이 없으면 생성
CREATE TABLE IF NOT EXISTS positions (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    strategy_id uuid REFERENCES strategies(id),
    account_no varchar(20),  -- 필요한 컬럼 추가
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

-- account_no 컬럼이 없는 경우 추가
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='positions' AND column_name='account_no') THEN
        ALTER TABLE positions ADD COLUMN account_no varchar(20);
    END IF;
END $$;

-- UNIQUE 제약조건 추가 (이미 존재하면 무시)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'positions_account_no_stock_code_strategy_id_key'
    ) THEN
        ALTER TABLE positions 
        ADD CONSTRAINT positions_account_no_stock_code_strategy_id_key 
        UNIQUE(account_no, stock_code, strategy_id);
    END IF;
END $$;