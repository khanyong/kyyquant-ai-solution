-- kw_price_current 테이블 생성 (존재하지 않는 경우)
CREATE TABLE IF NOT EXISTS public.kw_price_current (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL UNIQUE,
    current_price NUMERIC(15, 2),
    change_price NUMERIC(15, 2) DEFAULT 0,
    change_rate NUMERIC(10, 4) DEFAULT 0,
    volume BIGINT DEFAULT 0,
    high_52w NUMERIC(15, 2) DEFAULT 0,
    low_52w NUMERIC(15, 2) DEFAULT 0,
    market_cap BIGINT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_kw_price_current_stock_code ON public.kw_price_current(stock_code);
CREATE INDEX IF NOT EXISTS idx_kw_price_current_updated_at ON public.kw_price_current(updated_at DESC);

-- RLS 활성화
ALTER TABLE public.kw_price_current ENABLE ROW LEVEL SECURITY;

-- 기존 정책 삭제 (있다면)
DROP POLICY IF EXISTS "Allow anonymous read access" ON public.kw_price_current;
DROP POLICY IF EXISTS "Allow anonymous insert/update" ON public.kw_price_current;
DROP POLICY IF EXISTS "Allow all operations" ON public.kw_price_current;

-- 모든 사용자가 읽기 가능
CREATE POLICY "Allow public read access"
ON public.kw_price_current
FOR SELECT
TO public
USING (true);

-- anon 역할이 INSERT/UPDATE 가능 (n8n에서 사용)
CREATE POLICY "Allow anon insert/update"
ON public.kw_price_current
FOR INSERT
TO anon
WITH CHECK (true);

CREATE POLICY "Allow anon update"
ON public.kw_price_current
FOR UPDATE
TO anon
USING (true)
WITH CHECK (true);

-- GRANT 권한 설정
GRANT SELECT ON public.kw_price_current TO anon;
GRANT INSERT ON public.kw_price_current TO anon;
GRANT UPDATE ON public.kw_price_current TO anon;
GRANT SELECT ON public.kw_price_current TO authenticated;

-- 시퀀스 권한
GRANT USAGE, SELECT ON SEQUENCE public.kw_price_current_id_seq TO anon;

-- 확인
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'kw_price_current';
