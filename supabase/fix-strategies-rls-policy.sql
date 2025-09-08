-- ====================================================================
-- strategies 테이블의 RLS 정책 수정
-- 문제: 현재 모든 사용자가 strategies 테이블에 접근 가능
-- 해결: 사용자가 자신의 전략만 CRUD 할 수 있도록 정책 수정
-- ====================================================================

-- 1. 기존 정책 삭제
DROP POLICY IF EXISTS "Enable all for strategies based on user_id" ON strategies;
DROP POLICY IF EXISTS "Users can view own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can create own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can update own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can delete own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can manage own strategies" ON strategies;

-- 2. RLS 활성화 확인
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;

-- 3. 새로운 정책 생성 (사용자별 접근 제한)
-- 3.1 SELECT: 자신의 전략만 조회 가능
CREATE POLICY "Users can view own strategies" ON strategies
    FOR SELECT 
    USING (auth.uid() = user_id);

-- 3.2 INSERT: 자신의 user_id로만 생성 가능
CREATE POLICY "Users can create own strategies" ON strategies
    FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

-- 3.3 UPDATE: 자신의 전략만 수정 가능
CREATE POLICY "Users can update own strategies" ON strategies
    FOR UPDATE 
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 3.4 DELETE: 자신의 전략만 삭제 가능
CREATE POLICY "Users can delete own strategies" ON strategies
    FOR DELETE 
    USING (auth.uid() = user_id);

-- 4. 관리자용 정책 추가 (선택사항)
-- admin 역할을 가진 사용자는 모든 전략에 접근 가능
CREATE POLICY "Admins can view all strategies" ON strategies
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Admins can manage all strategies" ON strategies
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'admin'
        )
    );

-- 5. 정책 적용 확인
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies
WHERE schemaname = 'public' 
AND tablename = 'strategies'
ORDER BY policyname;

-- 6. 현재 사용자의 strategies 테이블 접근 테스트
-- 테스트: 자신의 전략만 보이는지 확인
SELECT 
    COUNT(*) as total_strategies,
    COUNT(CASE WHEN user_id = auth.uid() THEN 1 END) as my_strategies
FROM strategies;

-- 완료 메시지
SELECT 'strategies 테이블 RLS 정책 수정 완료' as status;