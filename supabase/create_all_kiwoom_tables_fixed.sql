-- ============================================
-- 키움 OpenAPI+ 전체 데이터 저장용 테이블
-- 순서대로 실행 가능한 수정 버전
-- ============================================

-- 기존 테이블 삭제 (필요시)
-- DROP TABLE IF EXISTS technical_indicators CASCADE;
-- DROP TABLE IF EXISTS stock_themes CASCADE;
-- DROP TABLE IF EXISTS theme_groups CASCADE;
-- DROP TABLE IF EXISTS sector_comparison CASCADE;
-- DROP TABLE IF EXISTS sector_data CASCADE;
-- DROP TABLE IF EXISTS analyst_reports CASCADE;
-- DROP TABLE IF EXISTS news CASCADE;
-- DROP TABLE IF EXISTS disclosures CASCADE;
-- DROP TABLE IF EXISTS investor_trading CASCADE;
-- DROP TABLE IF EXISTS financial_ratios CASCADE;
-- DROP TABLE IF EXISTS financial_statements CASCADE;
-- DROP TABLE IF EXISTS realtime_price CASCADE;
-- DROP TABLE IF EXISTS price_data_minute CASCADE;
-- DROP TABLE IF EXISTS price_data_monthly CASCADE;
-- DROP TABLE IF EXISTS price_data_weekly CASCADE;
-- DROP TABLE IF EXISTS price_data CASCADE;
-- DROP TABLE IF EXISTS stock_master CASCADE;

-- ============================================
-- 1. 종목 마스터 정보 (기본 테이블)
-- ============================================
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

-- ============================================
-- 2. 가격 데이터 테이블들
-- ============================================

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

-- ============================================
-- 3. 실시간 및 현재가 데이터
-- ============================================

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
    
    -- 호가 정보
    ask_price_1 DECIMAL(12,2),
    ask_volume_1 BIGINT,
    bid_price_1 DECIMAL(12,2),
    bid_volume_1 BIGINT,
    ask_price_2 DECIMAL(12,2),
    ask_volume_2 BIGINT,
    bid_price_2 DECIMAL(12,2),
    bid_volume_2 BIGINT,
    ask_price_3 DECIMAL(12,2),
    ask_volume_3 BIGINT,
    bid_price_3 DECIMAL(12,2),
    bid_volume_3 BIGINT,
    ask_price_4 DECIMAL(12,2),
    ask_volume_4 BIGINT,
    bid_price_4 DECIMAL(12,2),
    bid_volume_4 BIGINT,
    ask_price_5 DECIMAL(12,2),
    ask_volume_5 BIGINT,
    bid_price_5 DECIMAL(12,2),
    bid_volume_5 BIGINT,
    
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 4. 재무 데이터
-- ============================================

-- 재무제표
CREATE TABLE IF NOT EXISTS financial_statements (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    fiscal_period VARCHAR(10),
    fiscal_date DATE,
    
    -- 손익계산서
    revenue BIGINT,
    cost_of_sales BIGINT,
    gross_profit BIGINT,
    operating_expenses BIGINT,
    operating_profit BIGINT,
    financial_income BIGINT,
    financial_expenses BIGINT,
    profit_before_tax BIGINT,
    income_tax BIGINT,
    net_profit BIGINT,
    
    -- 재무상태표
    current_assets BIGINT,
    non_current_assets BIGINT,
    total_assets BIGINT,
    current_liabilities BIGINT,
    non_current_liabilities BIGINT,
    total_liabilities BIGINT,
    capital_stock BIGINT,
    retained_earnings BIGINT,
    total_equity BIGINT,
    
    -- 현금흐름표
    operating_cash_flow BIGINT,
    investing_cash_flow BIGINT,
    financing_cash_flow BIGINT,
    cash_beginning BIGINT,
    cash_ending BIGINT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, fiscal_period)
);

-- 재무비율
CREATE TABLE IF NOT EXISTS financial_ratios (
    stock_code VARCHAR(10) PRIMARY KEY,
    
    -- 가치평가 지표
    per DECIMAL(10,2),
    pbr DECIMAL(10,2),
    pcr DECIMAL(10,2),
    psr DECIMAL(10,2),
    peg DECIMAL(10,2),
    ev_ebitda DECIMAL(10,2),
    
    -- 수익성 지표
    roe DECIMAL(10,2),
    roa DECIMAL(10,2),
    roic DECIMAL(10,2),
    gross_margin DECIMAL(10,2),
    operating_margin DECIMAL(10,2),
    net_margin DECIMAL(10,2),
    
    -- 안정성 지표
    debt_ratio DECIMAL(10,2),
    current_ratio DECIMAL(10,2),
    quick_ratio DECIMAL(10,2),
    interest_coverage DECIMAL(10,2),
    
    -- 성장성 지표
    revenue_growth_yoy DECIMAL(10,2),
    profit_growth_yoy DECIMAL(10,2),
    
    -- 주당지표
    eps INTEGER,
    bps INTEGER,
    dps INTEGER,
    
    -- 배당
    dividend_yield DECIMAL(5,2),
    payout_ratio DECIMAL(10,2),
    
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 5. 투자자 및 거래 데이터
-- ============================================

CREATE TABLE IF NOT EXISTS investor_trading (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trading_date DATE NOT NULL,
    
    -- 개인
    individual_buy BIGINT,
    individual_sell BIGINT,
    individual_net BIGINT,
    
    -- 외국인
    foreign_buy BIGINT,
    foreign_sell BIGINT,
    foreign_net BIGINT,
    foreign_ownership DECIMAL(5,2),
    
    -- 기관
    institution_buy BIGINT,
    institution_sell BIGINT,
    institution_net BIGINT,
    institution_ownership DECIMAL(5,2),
    
    -- 연기금/국가
    pension_buy BIGINT,
    pension_sell BIGINT,
    pension_net BIGINT,
    
    -- 기타
    other_buy BIGINT,
    other_sell BIGINT,
    other_net BIGINT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, trading_date)
);

-- ============================================
-- 6. 공시 및 뉴스
-- ============================================

CREATE TABLE IF NOT EXISTS disclosures (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    disclosure_date DATE NOT NULL,
    disclosure_time TIME,
    title VARCHAR(500),
    content TEXT,
    disclosure_type VARCHAR(100),
    report_name VARCHAR(200),
    submitter VARCHAR(100),
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS news (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    news_date TIMESTAMP NOT NULL,
    title VARCHAR(500),
    content TEXT,
    summary TEXT,
    source VARCHAR(100),
    author VARCHAR(100),
    url VARCHAR(500),
    sentiment DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 7. 애널리스트 및 업종
-- ============================================

CREATE TABLE IF NOT EXISTS analyst_reports (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    securities_firm VARCHAR(100),
    analyst_name VARCHAR(100),
    
    rating VARCHAR(20),
    rating_change VARCHAR(20),
    previous_rating VARCHAR(20),
    
    target_price INTEGER,
    previous_target_price INTEGER,
    upside_potential DECIMAL(5,2),
    
    revenue_estimate BIGINT,
    operating_profit_estimate BIGINT,
    net_profit_estimate BIGINT,
    eps_estimate INTEGER,
    
    report_title VARCHAR(500),
    key_points TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sector_data (
    sector_code VARCHAR(20) PRIMARY KEY,
    sector_name VARCHAR(100),
    market VARCHAR(20),
    
    sector_index DECIMAL(10,2),
    index_change DECIMAL(10,2),
    index_change_rate DECIMAL(5,2),
    
    avg_per DECIMAL(10,2),
    avg_pbr DECIMAL(10,2),
    avg_roe DECIMAL(10,2),
    avg_dividend_yield DECIMAL(5,2),
    
    stock_count INTEGER,
    market_cap_total BIGINT,
    
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sector_comparison (
    stock_code VARCHAR(10) PRIMARY KEY,
    sector_code VARCHAR(20),
    
    market_cap_rank INTEGER,
    revenue_rank INTEGER,
    profit_rank INTEGER,
    per_rank INTEGER,
    roe_rank INTEGER,
    
    per_vs_sector DECIMAL(10,2),
    pbr_vs_sector DECIMAL(10,2),
    roe_vs_sector DECIMAL(10,2),
    margin_vs_sector DECIMAL(10,2),
    
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 8. 테마 및 기술적 지표
-- ============================================

CREATE TABLE IF NOT EXISTS theme_groups (
    id BIGSERIAL PRIMARY KEY,
    theme_code VARCHAR(20) UNIQUE NOT NULL,
    theme_name VARCHAR(100),
    description TEXT,
    stock_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stock_themes (
    stock_code VARCHAR(10) NOT NULL,
    theme_code VARCHAR(20) NOT NULL,
    relevance_score DECIMAL(3,2),
    PRIMARY KEY(stock_code, theme_code)
);

CREATE TABLE IF NOT EXISTS technical_indicators (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    
    -- 이동평균
    ma_5 DECIMAL(12,2),
    ma_20 DECIMAL(12,2),
    ma_60 DECIMAL(12,2),
    ma_120 DECIMAL(12,2),
    ma_200 DECIMAL(12,2),
    
    -- 지수이동평균
    ema_12 DECIMAL(12,2),
    ema_26 DECIMAL(12,2),
    
    -- 볼린저밴드
    bb_upper DECIMAL(12,2),
    bb_middle DECIMAL(12,2),
    bb_lower DECIMAL(12,2),
    bb_width DECIMAL(12,2),
    
    -- 모멘텀 지표
    rsi_14 DECIMAL(5,2),
    macd DECIMAL(12,2),
    macd_signal DECIMAL(12,2),
    macd_histogram DECIMAL(12,2),
    stochastic_k DECIMAL(5,2),
    stochastic_d DECIMAL(5,2),
    
    -- 거래량 지표
    obv BIGINT,
    vwap DECIMAL(12,2),
    
    -- 변동성 지표
    atr_14 DECIMAL(12,2),
    
    -- 추세 지표
    adx DECIMAL(5,2),
    plus_di DECIMAL(5,2),
    minus_di DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, date)
);

-- ============================================
-- 9. 외래키 제약조건 추가 (테이블 생성 후)
-- ============================================

-- price_data 테이블들
ALTER TABLE price_data 
    ADD CONSTRAINT fk_price_data_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

ALTER TABLE price_data_weekly 
    ADD CONSTRAINT fk_price_weekly_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

ALTER TABLE price_data_monthly 
    ADD CONSTRAINT fk_price_monthly_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

ALTER TABLE price_data_minute 
    ADD CONSTRAINT fk_price_minute_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

-- realtime_price
ALTER TABLE realtime_price 
    ADD CONSTRAINT fk_realtime_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

-- financial 테이블들
ALTER TABLE financial_statements 
    ADD CONSTRAINT fk_financial_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

ALTER TABLE financial_ratios 
    ADD CONSTRAINT fk_ratios_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

-- 기타 테이블들
ALTER TABLE investor_trading 
    ADD CONSTRAINT fk_investor_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

ALTER TABLE disclosures 
    ADD CONSTRAINT fk_disclosure_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

ALTER TABLE news 
    ADD CONSTRAINT fk_news_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

ALTER TABLE analyst_reports 
    ADD CONSTRAINT fk_analyst_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

ALTER TABLE sector_comparison 
    ADD CONSTRAINT fk_comparison_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

ALTER TABLE sector_comparison 
    ADD CONSTRAINT fk_comparison_sector 
    FOREIGN KEY (sector_code) 
    REFERENCES sector_data(sector_code) 
    ON DELETE SET NULL;

ALTER TABLE stock_themes 
    ADD CONSTRAINT fk_themes_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

ALTER TABLE technical_indicators 
    ADD CONSTRAINT fk_tech_stock 
    FOREIGN KEY (stock_code) 
    REFERENCES stock_master(stock_code) 
    ON DELETE CASCADE;

-- ============================================
-- 10. 인덱스 생성 (성능 최적화)
-- ============================================

-- 가격 데이터 인덱스
CREATE INDEX IF NOT EXISTS idx_price_stock_date 
    ON price_data(stock_code, date DESC);
CREATE INDEX IF NOT EXISTS idx_price_date 
    ON price_data(date DESC);
CREATE INDEX IF NOT EXISTS idx_price_weekly_stock 
    ON price_data_weekly(stock_code, week_date DESC);
CREATE INDEX IF NOT EXISTS idx_price_monthly_stock 
    ON price_data_monthly(stock_code, month_date DESC);
CREATE INDEX IF NOT EXISTS idx_price_minute_stock 
    ON price_data_minute(stock_code, datetime DESC);

-- 재무 데이터 인덱스
CREATE INDEX IF NOT EXISTS idx_financial_stock_period 
    ON financial_statements(stock_code, fiscal_period);
CREATE INDEX IF NOT EXISTS idx_investor_stock_date 
    ON investor_trading(stock_code, trading_date DESC);

-- 공시/뉴스 인덱스
CREATE INDEX IF NOT EXISTS idx_disclosure_stock_date 
    ON disclosures(stock_code, disclosure_date DESC);
CREATE INDEX IF NOT EXISTS idx_news_stock_date 
    ON news(stock_code, news_date DESC);

-- 기술적 지표 인덱스
CREATE INDEX IF NOT EXISTS idx_tech_stock_date 
    ON technical_indicators(stock_code, date DESC);

-- ============================================
-- 11. 뷰 생성 (자주 사용하는 쿼리)
-- ============================================

-- 종목별 최신 정보 뷰
CREATE OR REPLACE VIEW stock_current_info AS
SELECT 
    m.stock_code,
    m.stock_name,
    m.market,
    m.sector_name,
    r.current_price,
    r.change_rate,
    r.volume,
    r.market_cap,
    f.per,
    f.pbr,
    f.roe,
    f.dividend_yield
FROM stock_master m
LEFT JOIN realtime_price r ON m.stock_code = r.stock_code
LEFT JOIN financial_ratios f ON m.stock_code = f.stock_code;

-- 투자자별 순매수 누적 뷰
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

-- ============================================
-- 12. 데이터 완전성 체크 함수
-- ============================================

CREATE OR REPLACE FUNCTION check_data_completeness(p_stock_code VARCHAR)
RETURNS TABLE (
    data_type VARCHAR,
    record_count BIGINT,
    first_date DATE,
    last_date DATE,
    is_complete BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'price_daily'::VARCHAR, 
           COUNT(*)::BIGINT,
           MIN(date), 
           MAX(date),
           (COUNT(*) > 200)::BOOLEAN
    FROM price_data WHERE stock_code = p_stock_code
    
    UNION ALL
    
    SELECT 'financial'::VARCHAR,
           COUNT(*)::BIGINT,
           MIN(fiscal_date),
           MAX(fiscal_date),
           (COUNT(*) > 4)::BOOLEAN
    FROM financial_statements WHERE stock_code = p_stock_code
    
    UNION ALL
    
    SELECT 'investor'::VARCHAR,
           COUNT(*)::BIGINT,
           MIN(trading_date),
           MAX(trading_date),
           (COUNT(*) > 20)::BOOLEAN
    FROM investor_trading WHERE stock_code = p_stock_code;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 실행 완료 메시지
-- ============================================
-- 모든 테이블이 생성되었습니다.
-- 확인: SELECT tablename FROM pg_tables WHERE schemaname = 'public';