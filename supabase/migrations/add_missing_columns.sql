-- strategies 테이블에 누락된 컬럼 추가
ALTER TABLE strategies 
ADD COLUMN IF NOT EXISTS conditions jsonb,
ADD COLUMN IF NOT EXISTS target_stocks text[],
ADD COLUMN IF NOT EXISTS position_size numeric DEFAULT 10,
ADD COLUMN IF NOT EXISTS auto_execute boolean DEFAULT false;

-- trading_signals 테이블에 누락된 컬럼 추가
ALTER TABLE trading_signals
ADD COLUMN IF NOT EXISTS created_at timestamp with time zone DEFAULT now(),
ADD COLUMN IF NOT EXISTS volume bigint,
ADD COLUMN IF NOT EXISTS current_price numeric,
ADD COLUMN IF NOT EXISTS rsi_value numeric;

-- orders 테이블에 누락된 컬럼 추가  
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS signal_id uuid REFERENCES trading_signals(id),
ADD COLUMN IF NOT EXISTS order_time timestamp with time zone DEFAULT now(),
ADD COLUMN IF NOT EXISTS kiwoom_order_id text,
ADD COLUMN IF NOT EXISTS executed_quantity integer DEFAULT 0,
ADD COLUMN IF NOT EXISTS executed_price numeric;

-- market_data_cache 테이블 생성
CREATE TABLE IF NOT EXISTS market_data_cache (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_code varchar(10) NOT NULL,
    current_price numeric,
    volume bigint,
    change_rate numeric,
    fetched_at timestamp with time zone DEFAULT now(),
    expires_at bigint,
    created_at timestamp with time zone DEFAULT now(),
    UNIQUE(stock_code)
);

-- positions 테이블 생성
CREATE TABLE IF NOT EXISTS positions (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    stock_code varchar(10) NOT NULL,
    stock_name varchar(100),
    quantity integer NOT NULL,
    avg_price numeric NOT NULL,
    current_price numeric,
    profit_loss numeric,
    profit_loss_rate numeric,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_market_data_cache_stock_code ON market_data_cache(stock_code);
CREATE INDEX IF NOT EXISTS idx_market_data_cache_expires_at ON market_data_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_positions_user_id ON positions(user_id);
CREATE INDEX IF NOT EXISTS idx_positions_stock_code ON positions(stock_code);
CREATE INDEX IF NOT EXISTS idx_trading_signals_created_at ON trading_signals(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_order_time ON orders(order_time);

-- RLS 정책 설정
ALTER TABLE market_data_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;

-- market_data_cache는 모든 사용자가 읽을 수 있음
CREATE POLICY "market_data_cache_read_all" ON market_data_cache
    FOR SELECT USING (true);

-- market_data_cache는 인증된 사용자만 쓸 수 있음
CREATE POLICY "market_data_cache_write_authenticated" ON market_data_cache
    FOR ALL USING (auth.role() = 'authenticated');

-- positions는 자신의 포지션만 볼 수 있음
CREATE POLICY "positions_user_own" ON positions
    FOR ALL USING (auth.uid() = user_id OR user_id IS NULL);