-- ====================================================================
-- strategies 테이블에 is_public 컬럼 추가
-- 목적: 전략 공유 기능을 위한 컬럼 추가
-- ====================================================================

-- 1. is_public 컬럼 추가 (boolean, 기본값은 false)
ALTER TABLE strategies
ADD COLUMN IF NOT EXISTS is_public BOOLEAN NOT NULL DEFAULT false;

-- 2. 컬럼 추가 확인
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'strategies'
AND column_name = 'is_public';

-- 3. 인덱스 추가 (공개 전략 조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_strategies_is_public
ON strategies (is_public)
WHERE is_public = true;

-- 4. RLS 정책 추가 - 공개 전략은 모든 사용자가 조회 가능
DROP POLICY IF EXISTS "Public strategies are viewable by everyone" ON strategies;

CREATE POLICY "Public strategies are viewable by everyone" ON strategies
    FOR SELECT
    USING (is_public = true);

-- 5. 현재 RLS 정책 확인
SELECT
    '=== Updated RLS Policies ===' as info;

SELECT
    policyname,
    cmd as operation,
    CASE
        WHEN 'authenticated' = ANY(roles) THEN 'FOR_AUTHENTICATED_USERS'
        WHEN roles IS NULL THEN 'FOR_ALL_USERS'
        ELSE 'FOR_SPECIFIC_ROLES: ' || array_to_string(roles, ', ')
    END as target_users,
    qual as condition_check
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'strategies'
ORDER BY cmd, policyname;

-- 완료 메시지
SELECT 'strategies 테이블에 is_public 컬럼 및 공개 전략 조회 정책 추가 완료' as status;