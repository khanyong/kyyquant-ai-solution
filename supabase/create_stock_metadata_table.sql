-- stock_metadata 테이블 생성
-- 모든 종목의 기본 정보를 저장하는 테이블

CREATE TABLE IF NOT EXISTS public.stock_metadata (
    stock_code VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    market VARCHAR(20) NOT NULL CHECK (market IN ('KOSPI', 'KOSDAQ', 'KONEX', 'ETF')),
    sector VARCHAR(100),
    industry VARCHAR(100),
    listing_date DATE,
    is_active BOOLEAN DEFAULT true,
    is_etf BOOLEAN DEFAULT false,
    is_spac BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_stock_metadata_market ON public.stock_metadata(market);
CREATE INDEX IF NOT EXISTS idx_stock_metadata_name ON public.stock_metadata(stock_name);
CREATE INDEX IF NOT EXISTS idx_stock_metadata_active ON public.stock_metadata(is_active);

-- 코멘트 추가
COMMENT ON TABLE public.stock_metadata IS '주식 종목 메타데이터';
COMMENT ON COLUMN public.stock_metadata.stock_code IS '종목코드 (6자리)';
COMMENT ON COLUMN public.stock_metadata.stock_name IS '종목명';
COMMENT ON COLUMN public.stock_metadata.market IS '시장구분 (KOSPI/KOSDAQ/KONEX/ETF)';
COMMENT ON COLUMN public.stock_metadata.sector IS '업종 대분류';
COMMENT ON COLUMN public.stock_metadata.industry IS '업종 소분류';
COMMENT ON COLUMN public.stock_metadata.listing_date IS '상장일';
COMMENT ON COLUMN public.stock_metadata.is_active IS '거래 가능 여부';
COMMENT ON COLUMN public.stock_metadata.is_etf IS 'ETF 여부';
COMMENT ON COLUMN public.stock_metadata.is_spac IS 'SPAC 여부';

-- RLS (Row Level Security) 활성화
ALTER TABLE public.stock_metadata ENABLE ROW LEVEL SECURITY;

-- 읽기 권한 정책 (모든 사용자)
CREATE POLICY "stock_metadata_read_all" ON public.stock_metadata
    FOR SELECT USING (true);

-- 쓰기 권한 정책 (인증된 사용자만)
CREATE POLICY "stock_metadata_write_auth" ON public.stock_metadata
    FOR ALL USING (auth.role() = 'authenticated');

-- 함수: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성
CREATE TRIGGER update_stock_metadata_updated_at
    BEFORE UPDATE ON public.stock_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();