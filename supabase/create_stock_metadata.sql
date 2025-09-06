-- 종목 메타데이터 테이블 생성
CREATE TABLE IF NOT EXISTS stock_metadata (
    stock_code VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    market VARCHAR(20) NOT NULL, -- KOSPI, KOSDAQ
    sector VARCHAR(50),
    industry VARCHAR(100),
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_stock_market ON stock_metadata(market);
CREATE INDEX IF NOT EXISTS idx_stock_name ON stock_metadata(stock_name);
CREATE INDEX IF NOT EXISTS idx_stock_sector ON stock_metadata(sector);

-- price_data 테이블 인덱스 최적화
CREATE INDEX IF NOT EXISTS idx_price_stock_date ON price_data(stock_code, date DESC);
CREATE INDEX IF NOT EXISTS idx_price_date ON price_data(date DESC);

-- 데이터 다운로드 진행 상황 테이블
CREATE TABLE IF NOT EXISTS download_progress (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10),
    status VARCHAR(20), -- pending, downloading, completed, failed
    records_count INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 통계 뷰 생성 (종목별 데이터 개수)
CREATE OR REPLACE VIEW stock_data_stats AS
SELECT 
    sm.stock_code,
    sm.stock_name,
    sm.market,
    COUNT(pd.id) as record_count,
    MIN(pd.date) as first_date,
    MAX(pd.date) as last_date,
    sm.last_updated
FROM stock_metadata sm
LEFT JOIN price_data pd ON sm.stock_code = pd.stock_code
GROUP BY sm.stock_code, sm.stock_name, sm.market, sm.last_updated
ORDER BY sm.market, sm.stock_code;

-- RLS 정책 설정
ALTER TABLE stock_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE download_progress ENABLE ROW LEVEL SECURITY;

-- 읽기 권한 (모든 사용자)
CREATE POLICY "stock_metadata_read_all" ON stock_metadata
    FOR SELECT USING (true);

CREATE POLICY "download_progress_read_all" ON download_progress
    FOR SELECT USING (true);

-- 쓰기 권한 (인증된 사용자)
CREATE POLICY "stock_metadata_write_auth" ON stock_metadata
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "download_progress_write_auth" ON download_progress
    FOR ALL USING (auth.role() = 'authenticated');

-- 함수: 종목별 데이터 통계
CREATE OR REPLACE FUNCTION get_stock_data_summary()
RETURNS TABLE (
    total_stocks INTEGER,
    kospi_stocks INTEGER,
    kosdaq_stocks INTEGER,
    total_records BIGINT,
    avg_records_per_stock NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT sm.stock_code)::INTEGER as total_stocks,
        COUNT(DISTINCT CASE WHEN sm.market = 'KOSPI' THEN sm.stock_code END)::INTEGER as kospi_stocks,
        COUNT(DISTINCT CASE WHEN sm.market = 'KOSDAQ' THEN sm.stock_code END)::INTEGER as kosdaq_stocks,
        COUNT(pd.id)::BIGINT as total_records,
        ROUND(AVG(sub.cnt), 2) as avg_records_per_stock
    FROM stock_metadata sm
    LEFT JOIN price_data pd ON sm.stock_code = pd.stock_code
    LEFT JOIN (
        SELECT stock_code, COUNT(*) as cnt
        FROM price_data
        GROUP BY stock_code
    ) sub ON sm.stock_code = sub.stock_code;
END;
$$ LANGUAGE plpgsql;

-- 샘플 데이터 (테스트용)
INSERT INTO stock_metadata (stock_code, stock_name, market, sector)
VALUES 
    ('005930', '삼성전자', 'KOSPI', '전기전자'),
    ('000660', 'SK하이닉스', 'KOSPI', '전기전자'),
    ('035720', '카카오', 'KOSPI', 'IT'),
    ('035420', '네이버', 'KOSPI', 'IT'),
    ('005380', '현대차', 'KOSPI', '자동차')
ON CONFLICT (stock_code) DO UPDATE
SET last_updated = NOW();