-- ============================================
-- kw_financial_snapshot 테이블 생성
-- 투자설정 데이터 수집용 시계열 테이블
-- ============================================

-- 기존 테이블이 있으면 삭제 (주의: 데이터가 삭제됨)
-- DROP TABLE IF EXISTS kw_financial_snapshot CASCADE;

-- 재무지표 스냅샷 테이블 생성
CREATE TABLE IF NOT EXISTS kw_financial_snapshot (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    market VARCHAR(20),
    snapshot_date DATE NOT NULL,
    snapshot_time TIME,
    
    -- 시가총액 (억원)
    market_cap BIGINT,
    shares_outstanding BIGINT,
    
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
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성 (빠른 조회를 위해)
CREATE INDEX IF NOT EXISTS idx_kw_snapshot_stock 
ON kw_financial_snapshot(stock_code, snapshot_date DESC);

CREATE INDEX IF NOT EXISTS idx_kw_snapshot_date 
ON kw_financial_snapshot(snapshot_date DESC);

CREATE INDEX IF NOT EXISTS idx_kw_snapshot_market_cap 
ON kw_financial_snapshot(market_cap DESC);

-- 테이블 권한 설정
GRANT ALL ON kw_financial_snapshot TO anon;
GRANT ALL ON kw_financial_snapshot TO authenticated;
GRANT ALL ON kw_financial_snapshot TO service_role;

-- 테이블 생성 확인
SELECT 
    'kw_financial_snapshot 테이블이 생성되었습니다.' as message,
    COUNT(*) as row_count
FROM kw_financial_snapshot;