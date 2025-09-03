-- ============================================
-- Supabase에서 실행해야 할 전체 테이블 생성 SQL
-- ============================================

-- 1. 전략 저장 테이블 (핵심)
CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,
    
    -- 기본 정보
    name TEXT NOT NULL,
    version TEXT DEFAULT '1.0.0',
    description TEXT,
    author TEXT,
    strategy_type TEXT DEFAULT 'custom',
    timeframe TEXT DEFAULT '1d',
    universe TEXT[], -- 대상 종목 배열
    
    -- 상태
    is_active BOOLEAN DEFAULT FALSE,
    is_test_mode BOOLEAN DEFAULT TRUE,
    auto_trade_enabled BOOLEAN DEFAULT FALSE,
    
    -- 전체 설정 (JSON)
    indicators JSONB DEFAULT '{}',
    entry_conditions JSONB DEFAULT '{}',
    exit_conditions JSONB DEFAULT '{}',
    risk_management JSONB DEFAULT '{}',
    backtest_settings JSONB DEFAULT '{}',
    notifications JSONB DEFAULT '{}',
    custom_parameters JSONB DEFAULT '{}',
    
    -- 성과 메트릭
    performance_metrics JSONB DEFAULT '{}',
    last_signal_at TIMESTAMPTZ,
    last_trade_at TIMESTAMPTZ,
    
    -- 코드 및 메타데이터
    strategy_code TEXT, -- Python 코드
    code_hash TEXT, -- 코드 버전 체크용
    
    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 사용자
    user_id UUID REFERENCES auth.users(id),
    
    UNIQUE(name, version, user_id)
);

-- 2. 사용자 API 인증 정보
CREATE TABLE IF NOT EXISTS user_api_credentials (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) UNIQUE,
    
    -- 한국투자증권 API 정보
    api_key TEXT,
    api_secret TEXT, -- 암호화 필요
    account_no TEXT, -- 암호화 필요
    account_product_code TEXT DEFAULT '01',
    
    -- API 모드
    is_demo BOOLEAN DEFAULT TRUE,
    api_url TEXT,
    
    -- 상태
    is_active BOOLEAN DEFAULT TRUE,
    last_connected_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 주문 내역 테이블
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id TEXT UNIQUE,
    stock_code TEXT NOT NULL,
    stock_name TEXT,
    order_type TEXT NOT NULL, -- buy/sell
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    order_method TEXT DEFAULT 'limit',
    status TEXT DEFAULT 'pending',
    executed_price DECIMAL(10, 2),
    executed_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    executed_at TIMESTAMPTZ,
    strategy_id INTEGER REFERENCES strategies(id),
    strategy TEXT,
    notes TEXT,
    user_id UUID REFERENCES auth.users(id)
);

-- 4. 포트폴리오 테이블
CREATE TABLE IF NOT EXISTS portfolio (
    id SERIAL PRIMARY KEY,
    stock_code TEXT NOT NULL,
    stock_name TEXT,
    quantity INTEGER NOT NULL,
    avg_price DECIMAL(10, 2) NOT NULL,
    current_price DECIMAL(10, 2),
    profit_loss DECIMAL(10, 2),
    profit_loss_rate DECIMAL(5, 2),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id),
    UNIQUE(stock_code, user_id)
);

-- 5. 가격 데이터 테이블
CREATE TABLE IF NOT EXISTS price_data (
    id SERIAL PRIMARY KEY,
    stock_code TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2) NOT NULL,
    volume BIGINT,
    UNIQUE(stock_code, timestamp)
);

-- 6. 거래 신호 테이블
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    stock_code TEXT NOT NULL,
    signal_type TEXT NOT NULL, -- buy/sell/hold
    strategy TEXT NOT NULL,
    strategy_id INTEGER REFERENCES strategies(id),
    strength DECIMAL(3, 2),
    price DECIMAL(10, 2),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    executed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    user_id UUID REFERENCES auth.users(id)
);

-- 7. 전략 실행 로그
CREATE TABLE IF NOT EXISTS strategy_execution_logs (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    
    execution_time TIMESTAMPTZ NOT NULL,
    market_data JSONB,
    
    -- 지표 값들
    indicator_values JSONB,
    
    -- 조건 체크 결과
    entry_conditions_met JSONB,
    exit_conditions_met JSONB,
    risk_checks_passed JSONB,
    
    -- 신호 및 결정
    signal_generated TEXT,
    signal_strength FLOAT,
    action_taken TEXT,
    action_reason TEXT,
    
    -- 주문 정보
    order_placed BOOLEAN DEFAULT FALSE,
    order_details JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. 성과 분석 테이블
CREATE TABLE IF NOT EXISTS performance (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_value DECIMAL(15, 2),
    daily_return DECIMAL(10, 4),
    cumulative_return DECIMAL(10, 4),
    win_rate DECIMAL(5, 2),
    trades_count INTEGER,
    profit_trades INTEGER,
    loss_trades INTEGER,
    max_drawdown DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id),
    UNIQUE(date, user_id)
);

-- 9. 시스템 로그 테이블
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    level TEXT NOT NULL,
    module TEXT,
    message TEXT NOT NULL,
    details JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id)
);

-- 10. 백테스트 결과
CREATE TABLE IF NOT EXISTS backtests (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15, 2),
    final_capital DECIMAL(15, 2),
    total_return DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    win_rate DECIMAL(5, 2),
    total_trades INTEGER,
    parameters JSONB,
    detailed_results JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. 전략 실행 스케줄
CREATE TABLE IF NOT EXISTS strategy_schedules (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    start_time TIME,
    end_time TIME,
    days_of_week INTEGER[], -- 0=일, 1=월, ... 6=토
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 인덱스 생성
-- ============================================

CREATE INDEX IF NOT EXISTS idx_strategies_user_active ON strategies(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_orders_user_date ON orders(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_portfolio_user ON portfolio(user_id);
CREATE INDEX IF NOT EXISTS idx_price_data_stock_time ON price_data(stock_code, timestamp);
CREATE INDEX IF NOT EXISTS idx_signals_user_stock ON signals(user_id, stock_code);
CREATE INDEX IF NOT EXISTS idx_execution_logs_strategy ON strategy_execution_logs(strategy_id);
CREATE INDEX IF NOT EXISTS idx_performance_user_date ON performance(user_id, date);

-- ============================================
-- RLS (Row Level Security) 정책
-- ============================================

-- strategies 테이블
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own strategies" ON strategies
    FOR ALL USING (auth.uid() = user_id);

-- user_api_credentials 테이블
ALTER TABLE user_api_credentials ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own credentials" ON user_api_credentials
    FOR ALL USING (auth.uid() = user_id);

-- orders 테이블
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own orders" ON orders
    FOR ALL USING (auth.uid() = user_id);

-- portfolio 테이블
ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own portfolio" ON portfolio
    FOR ALL USING (auth.uid() = user_id);

-- signals 테이블
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own signals" ON signals
    FOR ALL USING (auth.uid() = user_id);

-- performance 테이블
ALTER TABLE performance ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own performance" ON performance
    FOR ALL USING (auth.uid() = user_id);

-- system_logs 테이블
ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own logs" ON system_logs
    FOR ALL USING (auth.uid() = user_id);

-- price_data는 모든 사용자가 볼 수 있음
CREATE POLICY "Anyone can view price data" ON price_data
    FOR SELECT USING (true);

-- ============================================
-- 트리거 함수
-- ============================================

-- updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- strategies 테이블 트리거
CREATE TRIGGER update_strategies_updated_at 
BEFORE UPDATE ON strategies 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- user_api_credentials 테이블 트리거
CREATE TRIGGER update_credentials_updated_at 
BEFORE UPDATE ON user_api_credentials 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 초기 데이터 (선택사항)
-- ============================================

-- 기본 전략 템플릿 (예시)
/*
INSERT INTO strategies (name, description, strategy_type, indicators, user_id) 
VALUES (
    'Sample Momentum Strategy',
    'Example momentum strategy template',
    'momentum',
    '{
        "rsi_enabled": true,
        "rsi_period": 14,
        "macd_enabled": true,
        "volume_enabled": true
    }'::jsonb,
    NULL -- 공용 템플릿
);
*/

-- ============================================
-- 실행 방법:
-- 1. Supabase Dashboard 접속
-- 2. SQL Editor 열기
-- 3. 이 SQL 전체 복사/붙여넣기
-- 4. Run 버튼 클릭
-- ============================================