-- RLS 정책 수정 - 모든 사용자가 읽기/쓰기 가능하도록 변경

-- 기존 정책 삭제
DROP POLICY IF EXISTS "stock_metadata_read_all" ON public.stock_metadata;
DROP POLICY IF EXISTS "stock_metadata_write_auth" ON public.stock_metadata;

-- 새로운 정책 생성 (모든 사용자 허용)
CREATE POLICY "stock_metadata_allow_all" ON public.stock_metadata
    FOR ALL USING (true) WITH CHECK (true);

-- 또는 RLS 비활성화 (더 간단한 방법)
-- ALTER TABLE public.stock_metadata DISABLE ROW LEVEL SECURITY;