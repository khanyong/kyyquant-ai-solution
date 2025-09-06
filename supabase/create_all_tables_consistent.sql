-- ============================================
-- 키움 OpenAPI+ 전체 데이터 테이블 (일관된 명명 규칙)
-- 명명 규칙: kw_카테고리_세부내용
-- 모든 테이블에 'kw_' 접두사 사용 (Kiwoom)
-- ============================================

-- ============================
-- 1. STOCK (종목) 카테고리
-- ============================

-- 종목 마스터
CREATE TABLE IF NOT EXISTS kw_stock_master (
    stock_code VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    market VARCHAR(20) NOT NULL,
    sector_name VARCHAR(100),
    listing_date DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 종목-업종 매핑
CREATE TABLE IF NOT EXISTS kw_stock_sector (
    stock_code VARCHAR(10),
    sector_code VARCHAR(20),
    PRIMARY KEY(stock_code, sector_code)
);

-- 종목-테마 매핑
CREATE TABLE IF NOT EXISTS kw_stock_theme (
    stock_code VARCHAR(10),
    theme_code VARCHAR(20),
    PRIMARY KEY(stock_code, theme_code)
);

-- ============================
-- 2. PRICE (가격) 카테고리
-- ============================

-- 일봉
CREATE TABLE IF NOT EXISTS kw_price_daily (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(12,2),
    high DECIMAL(12,2),
    low DECIMAL(12,2),
    close DECIMAL(12,2),
    volume BIGINT,
    trading_value BIGINT,
    UNIQUE(stock_code, trade_date)
);

-- 주봉
CREATE TABLE IF NOT EXISTS kw_price_weekly (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    week_date DATE NOT NULL,
    open DECIMAL(12,2),
    high DECIMAL(12,2),
    low DECIMAL(12,2),
    close DECIMAL(12,2),
    volume BIGINT,
    UNIQUE(stock_code, week_date)
);

-- 월봉
CREATE TABLE IF NOT EXISTS kw_price_monthly (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    month_date DATE NOT NULL,
    open DECIMAL(12,2),
    high DECIMAL(12,2),
    low DECIMAL(12,2),
    close DECIMAL(12,2),
    volume BIGINT,
    UNIQUE(stock_code, month_date)
);

-- 분봉
CREATE TABLE IF NOT EXISTS kw_price_minute (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_time TIMESTAMP NOT NULL,
    interval_min INTEGER NOT NULL,
    open DECIMAL(12,2),
    high DECIMAL(12,2),
    low DECIMAL(12,2),
    close DECIMAL(12,2),
    volume BIGINT,
    UNIQUE(stock_code, trade_time, interval_min)
);

-- 현재가
CREATE TABLE IF NOT EXISTS kw_price_current (
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
    foreign_ratio DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 호가
CREATE TABLE IF NOT EXISTS kw_price_orderbook (
    stock_code VARCHAR(10) PRIMARY KEY,
    ask_price1 DECIMAL(12,2),
    ask_volume1 BIGINT,
    bid_price1 DECIMAL(12,2),
    bid_volume1 BIGINT,
    ask_price2 DECIMAL(12,2),
    ask_volume2 BIGINT,
    bid_price2 DECIMAL(12,2),
    bid_volume2 BIGINT,
    ask_price3 DECIMAL(12,2),
    ask_volume3 BIGINT,
    bid_price3 DECIMAL(12,2),
    bid_volume3 BIGINT,
    ask_price4 DECIMAL(12,2),
    ask_volume4 BIGINT,
    bid_price4 DECIMAL(12,2),
    bid_volume4 BIGINT,
    ask_price5 DECIMAL(12,2),
    ask_volume5 BIGINT,
    bid_price5 DECIMAL(12,2),
    bid_volume5 BIGINT,
    ask_price6 DECIMAL(12,2),
    ask_volume6 BIGINT,
    bid_price6 DECIMAL(12,2),
    bid_volume6 BIGINT,
    ask_price7 DECIMAL(12,2),
    ask_volume7 BIGINT,
    bid_price7 DECIMAL(12,2),
    bid_volume7 BIGINT,
    ask_price8 DECIMAL(12,2),
    ask_volume8 BIGINT,
    bid_price8 DECIMAL(12,2),
    bid_volume8 BIGINT,
    ask_price9 DECIMAL(12,2),
    ask_volume9 BIGINT,
    bid_price9 DECIMAL(12,2),
    bid_volume9 BIGINT,
    ask_price10 DECIMAL(12,2),
    ask_volume10 BIGINT,
    bid_price10 DECIMAL(12,2),
    bid_volume10 BIGINT,
    total_ask_volume BIGINT,
    total_bid_volume BIGINT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- 3. FINANCIAL (재무) 카테고리
-- ============================

-- 재무제표
CREATE TABLE IF NOT EXISTS kw_financial_statement (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    fiscal_year VARCHAR(10),
    fiscal_quarter VARCHAR(10),
    revenue BIGINT,
    operating_profit BIGINT,
    net_profit BIGINT,
    total_assets BIGINT,
    total_liabilities BIGINT,
    total_equity BIGINT,
    operating_cash_flow BIGINT,
    investing_cash_flow BIGINT,
    financing_cash_flow BIGINT,
    UNIQUE(stock_code, fiscal_year, fiscal_quarter)
);

-- 재무비율
CREATE TABLE IF NOT EXISTS kw_financial_ratio (
    stock_code VARCHAR(10) PRIMARY KEY,
    per DECIMAL(10,2),
    pbr DECIMAL(10,2),
    pcr DECIMAL(10,2),
    psr DECIMAL(10,2),
    peg DECIMAL(10,2),
    eps INTEGER,
    bps INTEGER,
    dps INTEGER,
    roe DECIMAL(10,2),
    roa DECIMAL(10,2),
    debt_ratio DECIMAL(10,2),
    current_ratio DECIMAL(10,2),
    quick_ratio DECIMAL(10,2),
    dividend_yield DECIMAL(5,2),
    dividend_payout DECIMAL(10,2),
    revenue_growth DECIMAL(10,2),
    profit_growth DECIMAL(10,2),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- 4. INVESTOR (투자자) 카테고리
-- ============================

-- 투자자별 매매
CREATE TABLE IF NOT EXISTS kw_investor_trade (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    individual_buy BIGINT,
    individual_sell BIGINT,
    individual_net BIGINT,
    foreign_buy BIGINT,
    foreign_sell BIGINT,
    foreign_net BIGINT,
    institution_buy BIGINT,
    institution_sell BIGINT,
    institution_net BIGINT,
    pension_buy BIGINT,
    pension_sell BIGINT,
    pension_net BIGINT,
    UNIQUE(stock_code, trade_date)
);

-- 투자자 보유현황
CREATE TABLE IF NOT EXISTS kw_investor_holding (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    record_date DATE NOT NULL,
    foreign_shares BIGINT,
    foreign_ratio DECIMAL(5,2),
    institution_shares BIGINT,
    institution_ratio DECIMAL(5,2),
    individual_shares BIGINT,
    individual_ratio DECIMAL(5,2),
    UNIQUE(stock_code, record_date)
);

-- ============================
-- 5. INFO (정보) 카테고리
-- ============================

-- 공시
CREATE TABLE IF NOT EXISTS kw_info_disclosure (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    disclosure_date DATE NOT NULL,
    disclosure_time TIME,
    title TEXT,
    content TEXT,
    disclosure_type VARCHAR(100),
    url VARCHAR(500)
);

-- 뉴스
CREATE TABLE IF NOT EXISTS kw_info_news (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    news_datetime TIMESTAMP NOT NULL,
    title TEXT,
    content TEXT,
    source VARCHAR(100),
    url VARCHAR(500)
);

-- 애널리스트 리포트
CREATE TABLE IF NOT EXISTS kw_info_report (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    securities_firm VARCHAR(100),
    analyst_name VARCHAR(100),
    rating VARCHAR(20),
    target_price INTEGER,
    title TEXT,
    summary TEXT
);

-- ============================
-- 6. MARKET (시장) 카테고리
-- ============================

-- 업종 정보
CREATE TABLE IF NOT EXISTS kw_market_sector (
    sector_code VARCHAR(20) PRIMARY KEY,
    sector_name VARCHAR(100),
    market VARCHAR(20),
    sector_index DECIMAL(10,2),
    index_change DECIMAL(10,2),
    index_change_rate DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 테마 정보
CREATE TABLE IF NOT EXISTS kw_market_theme (
    theme_code VARCHAR(20) PRIMARY KEY,
    theme_name VARCHAR(100),
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 프로그램 매매
CREATE TABLE IF NOT EXISTS kw_market_program (
    id BIGSERIAL PRIMARY KEY,
    trade_date DATE NOT NULL,
    kospi_buy BIGINT,
    kospi_sell BIGINT,
    kospi_net BIGINT,
    kosdaq_buy BIGINT,
    kosdaq_sell BIGINT,
    kosdaq_net BIGINT,
    UNIQUE(trade_date)
);

-- ============================
-- 7. INDICATOR (지표) 카테고리
-- ============================

-- 기술적 지표
CREATE TABLE IF NOT EXISTS kw_indicator_technical (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    calc_date DATE NOT NULL,
    -- 이동평균
    ma5 DECIMAL(12,2),
    ma20 DECIMAL(12,2),
    ma60 DECIMAL(12,2),
    ma120 DECIMAL(12,2),
    -- 볼린저밴드
    bb_upper DECIMAL(12,2),
    bb_middle DECIMAL(12,2),
    bb_lower DECIMAL(12,2),
    -- 기타 지표
    rsi14 DECIMAL(5,2),
    macd DECIMAL(12,2),
    macd_signal DECIMAL(12,2),
    stoch_k DECIMAL(5,2),
    stoch_d DECIMAL(5,2),
    cci DECIMAL(10,2),
    adx DECIMAL(5,2),
    obv BIGINT,
    UNIQUE(stock_code, calc_date)
);

-- ============================
-- 8. TRADE (거래) 카테고리
-- ============================

-- 체결 데이터
CREATE TABLE IF NOT EXISTS kw_trade_execution (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_datetime TIMESTAMP NOT NULL,
    trade_price DECIMAL(12,2),
    trade_volume BIGINT,
    trade_type VARCHAR(10) -- 매수/매도
);

-- ============================
-- 인덱스 생성
-- ============================

-- PRICE 인덱스
CREATE INDEX idx_kw_price_daily_stock ON kw_price_daily(stock_code);
CREATE INDEX idx_kw_price_daily_date ON kw_price_daily(trade_date DESC);
CREATE INDEX idx_kw_price_weekly_stock ON kw_price_weekly(stock_code);
CREATE INDEX idx_kw_price_monthly_stock ON kw_price_monthly(stock_code);
CREATE INDEX idx_kw_price_minute_stock ON kw_price_minute(stock_code);

-- INVESTOR 인덱스
CREATE INDEX idx_kw_investor_trade_stock ON kw_investor_trade(stock_code);
CREATE INDEX idx_kw_investor_trade_date ON kw_investor_trade(trade_date DESC);
CREATE INDEX idx_kw_investor_holding_stock ON kw_investor_holding(stock_code);

-- INFO 인덱스
CREATE INDEX idx_kw_info_disclosure_stock ON kw_info_disclosure(stock_code);
CREATE INDEX idx_kw_info_disclosure_date ON kw_info_disclosure(disclosure_date DESC);
CREATE INDEX idx_kw_info_news_stock ON kw_info_news(stock_code);
CREATE INDEX idx_kw_info_news_date ON kw_info_news(news_datetime DESC);
CREATE INDEX idx_kw_info_report_stock ON kw_info_report(stock_code);

-- INDICATOR 인덱스
CREATE INDEX idx_kw_indicator_technical_stock ON kw_indicator_technical(stock_code);
CREATE INDEX idx_kw_indicator_technical_date ON kw_indicator_technical(calc_date DESC);

-- ============================
-- 초기 데이터
-- ============================

INSERT INTO kw_stock_master (stock_code, stock_name, market, sector_name) 
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

-- ============================
-- 확인
-- ============================

SELECT 'Tables created with consistent naming!' as status;

-- 카테고리별 테이블 개수 확인
SELECT 
    CASE 
        WHEN tablename LIKE 'kw_stock_%' THEN 'STOCK'
        WHEN tablename LIKE 'kw_price_%' THEN 'PRICE'
        WHEN tablename LIKE 'kw_financial_%' THEN 'FINANCIAL'
        WHEN tablename LIKE 'kw_investor_%' THEN 'INVESTOR'
        WHEN tablename LIKE 'kw_info_%' THEN 'INFO'
        WHEN tablename LIKE 'kw_market_%' THEN 'MARKET'
        WHEN tablename LIKE 'kw_indicator_%' THEN 'INDICATOR'
        WHEN tablename LIKE 'kw_trade_%' THEN 'TRADE'
    END as category,
    COUNT(*) as table_count
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename LIKE ANY(ARRAY['kw_stock_%', 'kw_price_%', 'kw_financial_%', 'kw_investor_%', 'kw_info_%', 'kw_market_%', 'kw_indicator_%', 'kw_trade_%'])
GROUP BY category
ORDER BY category;