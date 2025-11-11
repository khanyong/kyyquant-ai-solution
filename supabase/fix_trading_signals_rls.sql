-- trading_signals 테이블의 RLS 정책 수정
-- n8n 워크플로우에서 anon 키로 INSERT 가능하도록 설정

-- 기존 INSERT 정책 삭제
DROP POLICY IF EXISTS "Authenticated users can insert trading signals" ON trading_signals;
DROP POLICY IF EXISTS "Users can insert their own trading signals" ON trading_signals;

-- 새로운 INSERT 정책: anon 키로도 삽입 가능
CREATE POLICY "Allow anon insert for trading signals" ON trading_signals
    FOR INSERT
    WITH CHECK (true);

-- 기존 SELECT 정책 확인 (이미 있으면 유지)
DROP POLICY IF EXISTS "Trading signals are viewable by all users" ON trading_signals;
CREATE POLICY "Trading signals are viewable by all" ON trading_signals
    FOR SELECT
    USING (true);

-- UPDATE 정책도 anon 허용
DROP POLICY IF EXISTS "Users can update their own trading signals" ON trading_signals;
CREATE POLICY "Allow anon update for trading signals" ON trading_signals
    FOR UPDATE
    USING (true)
    WITH CHECK (true);
