-- 키움증권 API 연동을 위한 테이블 생성

-- 1. 실시간 주식 가격 테이블
CREATE TABLE IF NOT EXISTS stock_prices (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    current_price DECIMAL(12, 2) NOT NULL,
    prev_close DECIMAL(12, 2),
    change DECIMAL(12, 2),
    change_rate DECIMAL(5, 2),
    volume BIGINT,
    total_volume BIGINT,
    high_price DECIMAL(12, 2),
    low_price DECIMAL(12, 2),
    open_price DECIMAL(12, 2),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_stock_prices_code ON stock_prices(stock_code);
CREATE INDEX idx_stock_prices_timestamp ON stock_prices(timestamp DESC);
CREATE INDEX idx_stock_prices_code_timestamp ON stock_prices(stock_code, timestamp DESC);

-- 2. 포트폴리오 테이블
CREATE TABLE IF NOT EXISTS portfolio (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    account_no VARCHAR(20),
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    quantity INTEGER NOT NULL,
    avg_price DECIMAL(12, 2) NOT NULL,
    current_price DECIMAL(12, 2),
    total_value DECIMAL(15, 2),
    profit_loss DECIMAL(15, 2),
    profit_rate DECIMAL(7, 2),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_portfolio_user ON portfolio(user_id);
CREATE INDEX idx_portfolio_account ON portfolio(account_no);
CREATE UNIQUE INDEX idx_portfolio_user_stock ON portfolio(user_id, stock_code);

-- 3. 주문 내역 테이블
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    account_no VARCHAR(20),
    order_id VARCHAR(20) UNIQUE,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    order_type VARCHAR(10) NOT NULL, -- BUY, SELL
    order_method VARCHAR(10), -- LIMIT, MARKET
    quantity INTEGER NOT NULL,
    price DECIMAL(12, 2),
    executed_quantity INTEGER DEFAULT 0,
    executed_price DECIMAL(12, 2),
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, PARTIAL, EXECUTED, CANCELLED
    order_time TIMESTAMPTZ DEFAULT NOW(),
    executed_time TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_stock ON orders(stock_code);
CREATE INDEX idx_orders_time ON orders(order_time DESC);

-- 4. 체결 내역 테이블
CREATE TABLE IF NOT EXISTS executions (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT REFERENCES orders(id),
    execution_id VARCHAR(20) UNIQUE,
    stock_code VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    commission DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    execution_time TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_executions_order ON executions(order_id);
CREATE INDEX idx_executions_time ON executions(execution_time DESC);

-- 5. 계좌 정보 테이블
CREATE TABLE IF NOT EXISTS accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    account_no VARCHAR(20) UNIQUE NOT NULL,
    account_name VARCHAR(100),
    account_type VARCHAR(20), -- 실전투자, 모의투자
    total_balance DECIMAL(15, 2),
    available_balance DECIMAL(15, 2),
    total_eval_amount DECIMAL(15, 2),
    total_profit_loss DECIMAL(15, 2),
    total_profit_rate DECIMAL(7, 2),
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_accounts_user ON accounts(user_id);

-- 6. 관심종목 테이블
CREATE TABLE IF NOT EXISTS watchlist (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    target_price DECIMAL(12, 2),
    stop_loss_price DECIMAL(12, 2),
    memo TEXT,
    is_monitoring BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_watchlist_user ON watchlist(user_id);
CREATE UNIQUE INDEX idx_watchlist_user_stock ON watchlist(user_id, stock_code);

-- 7. 일봉 데이터 테이블 (차트용)
CREATE TABLE IF NOT EXISTS daily_prices (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open_price DECIMAL(12, 2),
    high_price DECIMAL(12, 2),
    low_price DECIMAL(12, 2),
    close_price DECIMAL(12, 2),
    volume BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE UNIQUE INDEX idx_daily_prices_code_date ON daily_prices(stock_code, trade_date);
CREATE INDEX idx_daily_prices_date ON daily_prices(trade_date DESC);

-- 8. 분봉 데이터 테이블 (실시간 차트용)
CREATE TABLE IF NOT EXISTS minute_prices (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open_price DECIMAL(12, 2),
    high_price DECIMAL(12, 2),
    low_price DECIMAL(12, 2),
    close_price DECIMAL(12, 2),
    volume BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_minute_prices_code ON minute_prices(stock_code);
CREATE INDEX idx_minute_prices_timestamp ON minute_prices(timestamp DESC);
CREATE UNIQUE INDEX idx_minute_prices_code_time ON minute_prices(stock_code, timestamp);

-- 9. 실시간 알림 테이블
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    notification_type VARCHAR(50), -- PRICE_ALERT, ORDER_EXECUTED, etc.
    title VARCHAR(200),
    message TEXT,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- RLS (Row Level Security) 정책 설정
ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- 포트폴리오 RLS 정책
CREATE POLICY "Users can view own portfolio" ON portfolio
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own portfolio" ON portfolio
    FOR UPDATE USING (auth.uid() = user_id);

-- 주문 RLS 정책
CREATE POLICY "Users can view own orders" ON orders
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own orders" ON orders
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 계좌 RLS 정책
CREATE POLICY "Users can view own accounts" ON accounts
    FOR SELECT USING (auth.uid() = user_id);

-- 관심종목 RLS 정책
CREATE POLICY "Users can manage own watchlist" ON watchlist
    FOR ALL USING (auth.uid() = user_id);

-- 알림 RLS 정책
CREATE POLICY "Users can view own notifications" ON notifications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications" ON notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- 실시간 구독을 위한 Publication 설정
ALTER PUBLICATION supabase_realtime ADD TABLE stock_prices;
ALTER PUBLICATION supabase_realtime ADD TABLE portfolio;
ALTER PUBLICATION supabase_realtime ADD TABLE orders;
ALTER PUBLICATION supabase_realtime ADD TABLE notifications;