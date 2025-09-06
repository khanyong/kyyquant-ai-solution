-- ============================================
-- 키움 OpenAPI+ 데이터 테이블 생성 (심플 버전)
-- 최소한의 필수 테이블만 생성
-- ============================================

-- 1. 종목 마스터
CREATE TABLE IF NOT EXISTS stock_master (
    stock_code VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    market VARCHAR(20) NOT NULL,
    sector_name VARCHAR(100),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. 일봉 데이터
CREATE TABLE IF NOT EXISTS price_data (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(12,2),
    high DECIMAL(12,2),
    low DECIMAL(12,2),
    close DECIMAL(12,2),
    volume BIGINT,
    trading_value BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, date)
);

-- 3. 재무비율
CREATE TABLE IF NOT EXISTS financial_ratios (
    stock_code VARCHAR(10) PRIMARY KEY,
    per DECIMAL(10,2),
    pbr DECIMAL(10,2),
    roe DECIMAL(10,2),
    roa DECIMAL(10,2),
    eps INTEGER,
    bps INTEGER,
    dividend_yield DECIMAL(5,2),
    debt_ratio DECIMAL(10,2),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. 투자자 매매
CREATE TABLE IF NOT EXISTS investor_trading (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trading_date DATE NOT NULL,
    individual_net BIGINT,
    foreign_net BIGINT,
    institution_net BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, trading_date)
);

-- 5. 실시간 가격
CREATE TABLE IF NOT EXISTS realtime_price (
    stock_code VARCHAR(10) PRIMARY KEY,
    current_price DECIMAL(12,2),
    change_price DECIMAL(12,2),
    change_rate DECIMAL(5,2),
    volume BIGINT,
    high_52w DECIMAL(12,2),
    low_52w DECIMAL(12,2),
    market_cap BIGINT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_price_stock ON price_data(stock_code);
CREATE INDEX IF NOT EXISTS idx_price_date ON price_data(date DESC);
CREATE INDEX IF NOT EXISTS idx_investor_stock ON investor_trading(stock_code);
CREATE INDEX IF NOT EXISTS idx_investor_date ON investor_trading(trading_date DESC);

-- 주요 종목 데이터 삽입
INSERT INTO stock_master (stock_code, stock_name, market, sector_name) 
VALUES 
    ('005930', '삼성전자', 'KOSPI', '전기전자'),
    ('000660', 'SK하이닉스', 'KOSPI', '전기전자'),
    ('035720', '카카오', 'KOSPI', 'IT서비스'),
    ('035420', '네이버', 'KOSPI', 'IT서비스'),
    ('005380', '현대차', 'KOSPI', '자동차'),
    ('051910', 'LG화학', 'KOSPI', '화학'),
    ('006400', '삼성SDI', 'KOSPI', '전기전자'),
    ('003550', 'LG', 'KOSPI', '지주회사'),
    ('105560', 'KB금융', 'KOSPI', '금융'),
    ('055550', '신한지주', 'KOSPI', '금융')
ON CONFLICT (stock_code) DO NOTHING;

-- 확인
SELECT 'Tables created successfully!' as status;
SELECT COUNT(*) as total_stocks FROM stock_master;