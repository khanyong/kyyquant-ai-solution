-- 거래 신호 테이블 생성
CREATE TABLE IF NOT EXISTS trading_signals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    signal_type VARCHAR(10) CHECK (signal_type IN ('buy', 'sell')) NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
    flow_type VARCHAR(20) CHECK (flow_type IN ('filter_first', 'strategy_first')),
    
    -- 필터 검증 결과
    passed_filters BOOLEAN DEFAULT false,
    filter_results JSONB DEFAULT '{}',
    
    -- 신호 상세 정보
    confidence INTEGER CHECK (confidence >= 0 AND confidence <= 100),
    price DECIMAL(10, 2),
    volume BIGINT,
    indicators JSONB DEFAULT '{}',
    
    -- 실행 상태
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'executed', 'cancelled', 'expired')),
    executed_at TIMESTAMP WITH TIME ZONE,
    execution_price DECIMAL(10, 2),
    execution_volume INTEGER,
    
    -- 메타 정보
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id UUID DEFAULT 'f912da32-897f-4dbb-9242-3a438e9733a8'
);

-- 인덱스 생성
CREATE INDEX idx_trading_signals_stock_code ON trading_signals(stock_code);
CREATE INDEX idx_trading_signals_signal_type ON trading_signals(signal_type);
CREATE INDEX idx_trading_signals_status ON trading_signals(status);
CREATE INDEX idx_trading_signals_created_at ON trading_signals(created_at DESC);
CREATE INDEX idx_trading_signals_flow_type ON trading_signals(flow_type);
CREATE INDEX idx_trading_signals_passed_filters ON trading_signals(passed_filters);

-- 업데이트 시간 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_trading_signals_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_trading_signals_updated_at
    BEFORE UPDATE ON trading_signals
    FOR EACH ROW
    EXECUTE FUNCTION update_trading_signals_updated_at();

-- RLS 정책
ALTER TABLE trading_signals ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능
CREATE POLICY "Trading signals are viewable by all users" ON trading_signals
    FOR SELECT USING (true);

-- 인증된 사용자만 삽입 가능
CREATE POLICY "Authenticated users can insert trading signals" ON trading_signals
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- 자신의 신호만 수정 가능
CREATE POLICY "Users can update their own trading signals" ON trading_signals
    FOR UPDATE USING (user_id = auth.uid());

-- 샘플 데이터 삽입 (선택사항)
INSERT INTO trading_signals (stock_code, stock_name, signal_type, strategy_name, flow_type, passed_filters, confidence, price, filter_results)
VALUES 
    ('005930', '삼성전자', 'buy', 'RSI 과매도 전략', 'filter_first', true, 85, 72000, 
     '{"marketCap": true, "per": true, "pbr": true, "roe": true, "debtRatio": true, "sector": true}'),
    ('000660', 'SK하이닉스', 'buy', '골든크로스 전략', 'strategy_first', true, 75, 132000,
     '{"marketCap": true, "per": true, "pbr": false, "roe": true, "debtRatio": true, "sector": true}'),
    ('035720', '카카오', 'sell', '볼린저밴드 전략', 'filter_first', false, 60, 55000,
     '{"marketCap": true, "per": false, "pbr": false, "roe": false, "debtRatio": true, "sector": true}');