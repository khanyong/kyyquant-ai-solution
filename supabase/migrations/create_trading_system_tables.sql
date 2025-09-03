-- ==================== 자동매매 시스템 테이블 구조 ====================

-- 1. 전략 테이블 (이미 존재하는 경우 수정)
CREATE TABLE IF NOT EXISTS strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT false,
    
    -- 전략 조건 설정
    conditions JSONB NOT NULL DEFAULT '{}',
    /* 예시:
    {
        "entry": {
            "rsi": {"operator": "<", "value": 30},
            "volume": {"operator": ">", "value": "avg_volume * 2"},
            "price": {"operator": ">", "value": "ma20"}
        },
        "exit": {
            "profit_target": 5,  -- 5% 수익
            "stop_loss": -3      -- -3% 손절
        }
    }
    */
    
    -- 리스크 관리
    position_size DECIMAL(5,2) DEFAULT 10.00, -- 포지션 크기 (%)
    max_positions INTEGER DEFAULT 5,           -- 최대 보유 종목수
    
    -- 실행 설정
    execution_time JSONB DEFAULT '{"start": "09:00", "end": "15:20"}',
    target_stocks JSONB DEFAULT '[]', -- 특정 종목만 거래시
    
    -- 통계
    total_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    total_profit DECIMAL(15,2) DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 전략 실행 로그
CREATE TABLE IF NOT EXISTS strategy_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
    execution_time TIMESTAMPTZ DEFAULT NOW(),
    status TEXT NOT NULL, -- 'running', 'completed', 'failed'
    
    -- 실행 상세
    scanned_stocks INTEGER,
    signals_generated INTEGER,
    orders_placed INTEGER,
    
    -- 실행 결과
    execution_log JSONB,
    error_message TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 거래 신호
CREATE TABLE IF NOT EXISTS trading_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
    execution_id UUID REFERENCES strategy_executions(id) ON DELETE CASCADE,
    
    -- 신호 정보
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    signal_type VARCHAR(10) NOT NULL, -- 'BUY', 'SELL', 'HOLD'
    signal_strength DECIMAL(3,2), -- 0.00 ~ 1.00
    
    -- 시장 데이터 (신호 발생 시점)
    current_price DECIMAL(12,2),
    volume BIGINT,
    
    -- 기술적 지표값
    indicators JSONB,
    /* 예시:
    {
        "rsi": 28.5,
        "macd": {"value": 0.5, "signal": 0.3},
        "volume_ratio": 2.5,
        "ma20": 50000,
        "ma60": 48000
    }
    */
    
    -- 주문 정보
    order_id VARCHAR(20),
    order_price DECIMAL(12,2),
    order_quantity INTEGER,
    order_status VARCHAR(20), -- 'pending', 'executed', 'cancelled', 'failed'
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 실제 주문 내역 (키움 API 응답 저장)
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id UUID REFERENCES trading_signals(id),
    strategy_id UUID REFERENCES strategies(id),
    
    -- 주문 정보
    kiwoom_order_id VARCHAR(20) UNIQUE,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    order_type VARCHAR(10) NOT NULL, -- 'BUY', 'SELL'
    order_method VARCHAR(10), -- 'LIMIT', 'MARKET'
    
    -- 주문 수량/가격
    quantity INTEGER NOT NULL,
    order_price DECIMAL(12,2),
    executed_quantity INTEGER DEFAULT 0,
    executed_price DECIMAL(12,2),
    
    -- 상태
    status VARCHAR(20) DEFAULT 'PENDING',
    -- 'PENDING', 'PARTIAL', 'EXECUTED', 'CANCELLED', 'FAILED'
    
    -- 시간
    order_time TIMESTAMPTZ DEFAULT NOW(),
    executed_time TIMESTAMPTZ,
    
    -- API 응답
    api_response JSONB,
    error_message TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 포지션 (현재 보유 종목)
CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    strategy_id UUID REFERENCES strategies(id),
    
    -- 종목 정보
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    
    -- 수량/가격
    quantity INTEGER NOT NULL,
    avg_price DECIMAL(12,2) NOT NULL,
    current_price DECIMAL(12,2),
    
    -- 손익
    unrealized_pnl DECIMAL(15,2),
    unrealized_pnl_rate DECIMAL(7,2),
    
    -- 진입 정보
    entry_signal_id UUID REFERENCES trading_signals(id),
    entry_time TIMESTAMPTZ DEFAULT NOW(),
    
    -- 청산 계획
    target_price DECIMAL(12,2),
    stop_loss_price DECIMAL(12,2),
    
    -- 상태
    is_active BOOLEAN DEFAULT true,
    exit_time TIMESTAMPTZ,
    exit_price DECIMAL(12,2),
    realized_pnl DECIMAL(15,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. 시장 데이터 캐시 (API 호출 최소화)
CREATE TABLE IF NOT EXISTS market_data_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_code VARCHAR(10) NOT NULL,
    
    -- 가격 정보
    current_price DECIMAL(12,2),
    prev_close DECIMAL(12,2),
    open_price DECIMAL(12,2),
    high_price DECIMAL(12,2),
    low_price DECIMAL(12,2),
    
    -- 거래량
    volume BIGINT,
    volume_amount DECIMAL(15,2),
    
    -- 기술적 지표
    indicators JSONB,
    
    -- 캐시 관리
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '1 minute'
);

-- ==================== 인덱스 생성 ====================

-- 전략 인덱스
CREATE INDEX idx_strategies_user_active ON strategies(user_id, is_active);
CREATE INDEX idx_strategies_updated ON strategies(updated_at DESC);

-- 신호 인덱스
CREATE INDEX idx_signals_strategy ON trading_signals(strategy_id);
CREATE INDEX idx_signals_stock ON trading_signals(stock_code);
CREATE INDEX idx_signals_created ON trading_signals(created_at DESC);

-- 주문 인덱스
CREATE INDEX idx_orders_strategy ON orders(strategy_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_stock ON orders(stock_code);

-- 포지션 인덱스
CREATE INDEX idx_positions_active ON positions(is_active);
CREATE INDEX idx_positions_strategy ON positions(strategy_id);
CREATE INDEX idx_positions_user ON positions(user_id);

-- 시장 데이터 캐시 인덱스
CREATE INDEX idx_market_cache_stock ON market_data_cache(stock_code);
CREATE INDEX idx_market_cache_expires ON market_data_cache(expires_at);

-- ==================== RLS (Row Level Security) ====================

-- 전략 테이블 RLS
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own strategies" ON strategies
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own strategies" ON strategies
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own strategies" ON strategies
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own strategies" ON strategies
    FOR DELETE USING (auth.uid() = user_id);

-- 포지션 테이블 RLS
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own positions" ON positions
    FOR SELECT USING (auth.uid() = user_id);

-- ==================== 트리거 함수 ====================

-- updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성
CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== 유용한 뷰 생성 ====================

-- 활성 전략 대시보드 뷰
CREATE OR REPLACE VIEW v_active_strategies AS
SELECT 
    s.id,
    s.name,
    s.user_id,
    s.is_active,
    s.total_trades,
    s.win_rate,
    s.total_profit,
    COUNT(DISTINCT p.id) as active_positions,
    MAX(se.execution_time) as last_execution
FROM strategies s
LEFT JOIN positions p ON s.id = p.strategy_id AND p.is_active = true
LEFT JOIN strategy_executions se ON s.id = se.strategy_id
WHERE s.is_active = true
GROUP BY s.id;

-- 오늘의 거래 현황
CREATE OR REPLACE VIEW v_todays_trades AS
SELECT 
    o.strategy_id,
    s.name as strategy_name,
    COUNT(*) as trade_count,
    SUM(CASE WHEN o.order_type = 'BUY' THEN 1 ELSE 0 END) as buy_count,
    SUM(CASE WHEN o.order_type = 'SELL' THEN 1 ELSE 0 END) as sell_count,
    COUNT(DISTINCT o.stock_code) as unique_stocks
FROM orders o
JOIN strategies s ON o.strategy_id = s.id
WHERE DATE(o.order_time) = CURRENT_DATE
GROUP BY o.strategy_id, s.name;

COMMENT ON TABLE strategies IS '자동매매 전략 정의';
COMMENT ON TABLE strategy_executions IS '전략 실행 로그';
COMMENT ON TABLE trading_signals IS '매매 신호 기록';
COMMENT ON TABLE orders IS '실제 주문 내역';
COMMENT ON TABLE positions IS '현재 보유 포지션';
COMMENT ON TABLE market_data_cache IS '시장 데이터 캐시';