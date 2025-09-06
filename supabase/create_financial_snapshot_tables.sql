-- ============================================
-- 투자설정 관련 시계열 데이터 테이블
-- 데이터를 누적 저장하여 이력 관리
-- ============================================

-- 재무지표 스냅샷 (시계열 데이터)
CREATE TABLE IF NOT EXISTS kw_financial_snapshot (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    market VARCHAR(20),
    snapshot_date DATE NOT NULL,  -- 수집 날짜
    snapshot_time TIME,           -- 수집 시간
    
    -- 시가총액 (억원)
    market_cap BIGINT,
    shares_outstanding BIGINT,   -- 발행주식수
    
    -- 가치평가 지표
    per DECIMAL(10,2),
    pbr DECIMAL(10,2),
    eps INTEGER,
    bps INTEGER,
    
    -- 수익성 지표
    roe DECIMAL(10,2),
    
    -- 가격 정보
    current_price INTEGER,
    change_rate DECIMAL(5,2),
    high_52w INTEGER,
    low_52w INTEGER,
    
    -- 거래 정보
    volume BIGINT,
    trading_value BIGINT,
    foreign_ratio DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- 복합 인덱스: 종목별 최신 데이터 빠른 조회
    INDEX idx_stock_snapshot (stock_code, snapshot_date DESC)
);

-- 재무제표 이력
CREATE TABLE IF NOT EXISTS kw_financial_statements_history (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    snapshot_date DATE NOT NULL,
    fiscal_year VARCHAR(10),
    fiscal_quarter VARCHAR(10),
    
    -- 손익계산서 (억원)
    revenue BIGINT,
    operating_profit BIGINT,
    net_profit BIGINT,
    operating_margin DECIMAL(10,2),
    net_margin DECIMAL(10,2),
    
    -- 재무상태표 (억원)
    total_assets BIGINT,
    total_liabilities BIGINT,
    total_equity BIGINT,
    
    -- 안정성 지표
    debt_ratio DECIMAL(10,2),
    current_ratio DECIMAL(10,2),
    quick_ratio DECIMAL(10,2),
    
    -- 추가 지표
    roa DECIMAL(10,2),
    dividend_yield DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_financial_history (stock_code, snapshot_date DESC)
);

-- 데이터 수집 로그
CREATE TABLE IF NOT EXISTS kw_collection_log (
    id BIGSERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    snapshot_time TIME,
    total_stocks INTEGER,
    success_count INTEGER,
    fail_count INTEGER,
    collection_type VARCHAR(50), -- 'full', 'incremental', 'retry'
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 종목별 최신 데이터 뷰 (가장 최근 스냅샷만 조회)
CREATE OR REPLACE VIEW kw_latest_financial AS
WITH latest_snapshot AS (
    SELECT 
        stock_code,
        MAX(snapshot_date) as latest_date
    FROM kw_financial_snapshot
    GROUP BY stock_code
)
SELECT 
    fs.*,
    CASE 
        WHEN fs.snapshot_date = CURRENT_DATE THEN '최신'
        WHEN fs.snapshot_date >= CURRENT_DATE - INTERVAL '7 days' THEN '1주일 이내'
        WHEN fs.snapshot_date >= CURRENT_DATE - INTERVAL '30 days' THEN '1개월 이내'
        ELSE '1개월 이상'
    END as data_freshness
FROM kw_financial_snapshot fs
INNER JOIN latest_snapshot ls 
    ON fs.stock_code = ls.stock_code 
    AND fs.snapshot_date = ls.latest_date;

-- 데이터 신선도 체크 함수
CREATE OR REPLACE FUNCTION get_data_freshness()
RETURNS TABLE (
    total_stocks INTEGER,
    fresh_stocks INTEGER,  -- 7일 이내
    stale_stocks INTEGER,  -- 30일 이상
    last_update DATE,
    days_old INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT stock_code)::INTEGER as total_stocks,
        COUNT(DISTINCT CASE 
            WHEN snapshot_date >= CURRENT_DATE - INTERVAL '7 days' 
            THEN stock_code 
        END)::INTEGER as fresh_stocks,
        COUNT(DISTINCT CASE 
            WHEN snapshot_date < CURRENT_DATE - INTERVAL '30 days' 
            THEN stock_code 
        END)::INTEGER as stale_stocks,
        MAX(snapshot_date) as last_update,
        (CURRENT_DATE - MAX(snapshot_date))::INTEGER as days_old
    FROM kw_financial_snapshot;
END;
$$ LANGUAGE plpgsql;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_snapshot_date ON kw_financial_snapshot(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_stock_code ON kw_financial_snapshot(stock_code);
CREATE INDEX IF NOT EXISTS idx_market_cap ON kw_financial_snapshot(market_cap DESC);
CREATE INDEX IF NOT EXISTS idx_per ON kw_financial_snapshot(per) WHERE per > 0;
CREATE INDEX IF NOT EXISTS idx_pbr ON kw_financial_snapshot(pbr) WHERE pbr > 0;
CREATE INDEX IF NOT EXISTS idx_roe ON kw_financial_snapshot(roe) WHERE roe > 0;