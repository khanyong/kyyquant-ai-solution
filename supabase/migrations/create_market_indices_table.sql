-- 시장 지수 데이터 테이블 (KOSPI, KOSDAQ, 환율 등)
CREATE TABLE IF NOT EXISTS market_indices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 지수 구분
    index_code VARCHAR(20) NOT NULL, -- 'KOSPI', 'KOSDAQ', 'USD_KRW'
    index_name VARCHAR(50) NOT NULL,

    -- 지수 데이터
    current_value NUMERIC(12, 2) NOT NULL,
    change_value NUMERIC(12, 2) DEFAULT 0,
    change_rate NUMERIC(7, 2) DEFAULT 0,

    -- 추가 정보
    open_value NUMERIC(12, 2),
    high_value NUMERIC(12, 2),
    low_value NUMERIC(12, 2),
    volume BIGINT,

    -- 타임스탬프
    trading_date DATE DEFAULT CURRENT_DATE,
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 유니크 제약: 같은 날짜에 같은 지수는 하나만
    UNIQUE(index_code, trading_date)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_market_indices_code
ON market_indices(index_code);

CREATE INDEX IF NOT EXISTS idx_market_indices_date
ON market_indices(trading_date DESC);

CREATE INDEX IF NOT EXISTS idx_market_indices_updated
ON market_indices(updated_at DESC);

-- 최신 지수 조회 뷰
CREATE OR REPLACE VIEW latest_market_indices AS
SELECT DISTINCT ON (index_code)
    index_code,
    index_name,
    current_value,
    change_value,
    change_rate,
    open_value,
    high_value,
    low_value,
    volume,
    trading_date,
    updated_at
FROM market_indices
ORDER BY index_code, updated_at DESC;

COMMENT ON TABLE market_indices IS '시장 지수 데이터 (KOSPI, KOSDAQ, 환율 등)';
COMMENT ON VIEW latest_market_indices IS '각 지수의 최신 데이터만 조회';

-- 샘플 데이터 삽입 (초기 테스트용)
INSERT INTO market_indices (index_code, index_name, current_value, change_value, change_rate)
VALUES
    ('KOSPI', 'KOSPI 지수', 2500.00, 0, 0),
    ('KOSDAQ', 'KOSDAQ 지수', 850.00, 0, 0),
    ('USD_KRW', '원/달러 환율', 1320.00, 0, 0)
ON CONFLICT (index_code, trading_date) DO NOTHING;

-- 테스트 쿼리
SELECT * FROM latest_market_indices;
