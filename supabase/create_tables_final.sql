-- ============================================
-- 키움 OpenAPI+ 데이터 테이블 생성 (최종 버전)
-- 오류 없이 실행 가능
-- ============================================

-- ============================
-- STEP 1: 기본 테이블 생성
-- ============================

-- 종목 마스터 정보
CREATE TABLE IF NOT EXISTS stock_master (
    stock_code VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    market VARCHAR(20) NOT NULL,
    sector_code VARCHAR(20),
    sector_name VARCHAR(100),
    listing_date DATE,
    capital BIGINT,
    face_value INTEGER,
    is_active BOOLEAN DEFAULT true,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 일봉 데이터
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

-- 주봉 데이터
CREATE TABLE IF NOT EXISTS price_data_weekly (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    week_date DATE NOT NULL,
    open DECIMAL(12,2),
    high DECIMAL(12,2),
    low DECIMAL(12,2),
    close DECIMAL(12,2),
    volume BIGINT,
    trading_value BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, week_date)
);

-- 월봉 데이터
CREATE TABLE IF NOT EXISTS price_data_monthly (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    month_date DATE NOT NULL,
    open DECIMAL(12,2),
    high DECIMAL(12,2),
    low DECIMAL(12,2),
    close DECIMAL(12,2),
    volume BIGINT,
    trading_value BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, month_date)
);

-- 분봉 데이터
CREATE TABLE IF NOT EXISTS price_data_minute (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    interval_min INTEGER NOT NULL,
    open DECIMAL(12,2),
    high DECIMAL(12,2),
    low DECIMAL(12,2),
    close DECIMAL(12,2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, datetime, interval_min)
);

-- 실시간 가격
CREATE TABLE IF NOT EXISTS realtime_price (
    stock_code VARCHAR(10) PRIMARY KEY,
    current_price DECIMAL(12,2),
    change_price DECIMAL(12,2),
    change_rate DECIMAL(5,2),
    volume BIGINT,
    trading_value BIGINT,
    high_52w DECIMAL(12,2),
    low_52w DECIMAL(12,2),
    market_cap BIGINT,
    shares_outstanding BIGINT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 재무제표
CREATE TABLE IF NOT EXISTS financial_statements (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    fiscal_period VARCHAR(10),
    fiscal_date DATE,
    revenue BIGINT,
    operating_profit BIGINT,
    net_profit BIGINT,
    total_assets BIGINT,
    total_liabilities BIGINT,
    total_equity BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, fiscal_period)
);

-- 재무비율
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
    current_ratio DECIMAL(10,2),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 투자자별 매매
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

-- 기술적 지표
CREATE TABLE IF NOT EXISTS technical_indicators (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    indicator_date DATE NOT NULL,  -- date 대신 indicator_date 사용
    ma_5 DECIMAL(12,2),
    ma_20 DECIMAL(12,2),
    ma_60 DECIMAL(12,2),
    ma_120 DECIMAL(12,2),
    rsi_14 DECIMAL(5,2),
    macd DECIMAL(12,2),
    macd_signal DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, indicator_date)
);

-- ============================
-- STEP 2: 인덱스 생성
-- ============================

CREATE INDEX IF NOT EXISTS idx_price_stock_date 
    ON price_data(stock_code, date DESC);
CREATE INDEX IF NOT EXISTS idx_price_weekly_stock 
    ON price_data_weekly(stock_code, week_date DESC);
CREATE INDEX IF NOT EXISTS idx_price_monthly_stock 
    ON price_data_monthly(stock_code, month_date DESC);
CREATE INDEX IF NOT EXISTS idx_investor_stock_date 
    ON investor_trading(stock_code, trading_date DESC);
CREATE INDEX IF NOT EXISTS idx_tech_stock_date 
    ON technical_indicators(stock_code, indicator_date DESC);

-- ============================
-- STEP 3: 샘플 데이터 (주요 20개 종목)
-- ============================

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
    ('055550', '신한지주', 'KOSPI', '금융'),
    ('000270', '기아', 'KOSPI', '자동차'),
    ('068270', '셀트리온', 'KOSPI', '의약품'),
    ('012330', '현대모비스', 'KOSPI', '자동차부품'),
    ('066570', 'LG전자', 'KOSPI', '전기전자'),
    ('096770', 'SK이노베이션', 'KOSPI', '화학'),
    ('207940', '삼성바이오로직스', 'KOSPI', '의약품'),
    ('005490', 'POSCO홀딩스', 'KOSPI', '철강'),
    ('028260', '삼성물산', 'KOSPI', '유통'),
    ('032830', '삼성생명', 'KOSPI', '보험'),
    ('015760', '한국전력', 'KOSPI', '전기가스')
ON CONFLICT (stock_code) DO NOTHING;

-- ============================
-- STEP 4: 뷰 생성
-- ============================

-- 종목 현재 정보 뷰
CREATE OR REPLACE VIEW stock_current_info AS
SELECT 
    m.stock_code,
    m.stock_name,
    m.market,
    m.sector_name,
    r.current_price,
    r.change_rate,
    r.volume,
    f.per,
    f.pbr,
    f.roe
FROM stock_master m
LEFT JOIN realtime_price r ON m.stock_code = r.stock_code
LEFT JOIN financial_ratios f ON m.stock_code = f.stock_code;

-- 투자자 누적 뷰
CREATE OR REPLACE VIEW investor_cumulative AS
SELECT 
    stock_code,
    SUM(foreign_net) as foreign_total,
    SUM(institution_net) as institution_total,
    SUM(individual_net) as individual_total,
    MIN(trading_date) as start_date,
    MAX(trading_date) as end_date
FROM investor_trading
GROUP BY stock_code;

-- ============================
-- STEP 5: 테이블 확인
-- ============================

SELECT 'Tables created successfully!' as message;

-- 테이블 목록
SELECT tablename as table_name
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN (
    'stock_master', 
    'price_data', 
    'price_data_weekly', 
    'price_data_monthly',
    'price_data_minute',
    'financial_ratios', 
    'investor_trading',
    'technical_indicators', 
    'realtime_price'
  )
ORDER BY tablename;

-- 종목 마스터 데이터 확인
SELECT COUNT(*) as total_stocks FROM stock_master;