-- ============================================
-- 키움 OpenAPI+ 전체 데이터 저장 테이블 (단순 버전)
-- 모든 API 정보를 저장할 수 있는 완전한 구조
-- ============================================

-- ============================
-- 1. 기본 테이블
-- ============================

-- 종목 마스터
CREATE TABLE IF NOT EXISTS stock_master (
    stock_code VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    market VARCHAR(20) NOT NULL,
    sector_name VARCHAR(100),
    listing_date DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- 2. 가격 데이터 테이블
-- ============================

-- 일봉
CREATE TABLE IF NOT EXISTS price_daily (
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
CREATE TABLE IF NOT EXISTS price_weekly (
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
CREATE TABLE IF NOT EXISTS price_monthly (
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
CREATE TABLE IF NOT EXISTS price_minute (
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

-- ============================
-- 3. 현재가 및 실시간
-- ============================

-- 현재가
CREATE TABLE IF NOT EXISTS current_price (
    stock_code VARCHAR(10) PRIMARY KEY,
    current_price DECIMAL(12,2),
    change_price DECIMAL(12,2),
    change_rate DECIMAL(5,2),
    volume BIGINT,
    trading_value BIGINT,
    high_price DECIMAL(12,2),
    low_price DECIMAL(12,2),
    open_price DECIMAL(12,2),
    high_52w DECIMAL(12,2),
    low_52w DECIMAL(12,2),
    market_cap BIGINT,
    shares_outstanding BIGINT,
    foreign_ratio DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 호가
CREATE TABLE IF NOT EXISTS orderbook (
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
-- 4. 재무 데이터
-- ============================

-- 재무제표
CREATE TABLE IF NOT EXISTS financial_statement (
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
CREATE TABLE IF NOT EXISTS financial_ratio (
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
-- 5. 투자자 매매
-- ============================

-- 투자자별 매매
CREATE TABLE IF NOT EXISTS investor_trade (
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
    etc_buy BIGINT,
    etc_sell BIGINT,
    etc_net BIGINT,
    UNIQUE(stock_code, trade_date)
);

-- 외국인/기관 보유현황
CREATE TABLE IF NOT EXISTS holder_status (
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
-- 6. 공시/뉴스/리포트
-- ============================

-- 공시
CREATE TABLE IF NOT EXISTS disclosure (
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
CREATE TABLE IF NOT EXISTS news (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    news_datetime TIMESTAMP NOT NULL,
    title TEXT,
    content TEXT,
    source VARCHAR(100),
    url VARCHAR(500)
);

-- 애널리스트 리포트
CREATE TABLE IF NOT EXISTS analyst_report (
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
-- 7. 업종/테마
-- ============================

-- 업종 정보
CREATE TABLE IF NOT EXISTS sector_info (
    sector_code VARCHAR(20) PRIMARY KEY,
    sector_name VARCHAR(100),
    market VARCHAR(20),
    sector_index DECIMAL(10,2),
    index_change DECIMAL(10,2),
    index_change_rate DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 테마 정보
CREATE TABLE IF NOT EXISTS theme_info (
    theme_code VARCHAR(20) PRIMARY KEY,
    theme_name VARCHAR(100),
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 종목-업종 매핑
CREATE TABLE IF NOT EXISTS stock_sector (
    stock_code VARCHAR(10),
    sector_code VARCHAR(20),
    PRIMARY KEY(stock_code, sector_code)
);

-- 종목-테마 매핑
CREATE TABLE IF NOT EXISTS stock_theme (
    stock_code VARCHAR(10),
    theme_code VARCHAR(20),
    PRIMARY KEY(stock_code, theme_code)
);

-- ============================
-- 8. 기술적 지표 (계산값 저장)
-- ============================

CREATE TABLE IF NOT EXISTS technical_indicator (
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
-- 9. 거래 상세 (체결 데이터)
-- ============================

CREATE TABLE IF NOT EXISTS trade_detail (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_datetime TIMESTAMP NOT NULL,
    trade_price DECIMAL(12,2),
    trade_volume BIGINT,
    trade_type VARCHAR(10) -- 매수/매도
);

-- ============================
-- 10. 프로그램 매매
-- ============================

CREATE TABLE IF NOT EXISTS program_trade (
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
-- 인덱스 생성
-- ============================

CREATE INDEX idx_price_daily_stock ON price_daily(stock_code);
CREATE INDEX idx_price_daily_date ON price_daily(trade_date DESC);
CREATE INDEX idx_investor_trade_stock ON investor_trade(stock_code);
CREATE INDEX idx_investor_trade_date ON investor_trade(trade_date DESC);
CREATE INDEX idx_disclosure_stock ON disclosure(stock_code);
CREATE INDEX idx_disclosure_date ON disclosure(disclosure_date DESC);
CREATE INDEX idx_news_stock ON news(stock_code);
CREATE INDEX idx_news_date ON news(news_datetime DESC);

-- ============================
-- 초기 데이터
-- ============================

INSERT INTO stock_master (stock_code, stock_name, market, sector_name) 
VALUES 
    ('005930', '삼성전자', 'KOSPI', '전기전자'),
    ('000660', 'SK하이닉스', 'KOSPI', '전기전자'),
    ('035720', '카카오', 'KOSPI', 'IT서비스'),
    ('035420', '네이버', 'KOSPI', 'IT서비스'),
    ('005380', '현대차', 'KOSPI', '자동차')
ON CONFLICT (stock_code) DO NOTHING;

-- ============================
-- 확인
-- ============================

SELECT 'Tables created:' as status;
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public';