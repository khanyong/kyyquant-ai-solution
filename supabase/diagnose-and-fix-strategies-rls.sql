-- ====================================================================
-- 전략 저장 RLS 권한 문제 진단 및 해결
-- 문제: 일반 사용자가 전략을 클라우드에 저장할 수 없음 (관리자는 가능)
-- ====================================================================

-- 1. 현재 RLS 정책 상태 확인
SELECT
    'Current RLS Policies for strategies table' as info;

SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'strategies'
ORDER BY policyname;

-- 2. 현재 사용자 정보 확인
SELECT
    'Current User Info' as info;

SELECT
    auth.uid() as current_user_id,
    auth.jwt() ->> 'email' as current_email,
    auth.jwt() ->> 'role' as current_role;

-- 3. strategies 테이블 구조 확인
SELECT
    'Strategies table structure' as info;

SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'strategies'
ORDER BY ordinal_position;

-- 4. 현재 strategies 데이터 확인 (관리자만 볼 수 있을 것)
SELECT
    'Current strategies data (first 5 rows)' as info;

SELECT
    id,
    user_id,
    name,
    created_at,
    updated_at,
    CASE
        WHEN user_id = auth.uid() THEN 'OWNED_BY_ME'
        ELSE 'OWNED_BY_OTHER'
    END as ownership_status
FROM strategies
ORDER BY created_at DESC
LIMIT 5;

-- 5. profiles 테이블 확인 (관리자 정책에서 사용)
SELECT
    'Profiles table check' as info;

SELECT
    id,
    role,
    email
FROM profiles
WHERE id = auth.uid()
OR role = 'admin'
LIMIT 10;

-- ====================================================================
-- 문제 해결: RLS 정책 재설정
-- ====================================================================

-- 6. 기존 정책들 삭제
DROP POLICY IF EXISTS "Enable all for strategies based on user_id" ON strategies;
DROP POLICY IF EXISTS "Users can view own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can create own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can update own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can delete own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can manage own strategies" ON strategies;
DROP POLICY IF EXISTS "Admins can view all strategies" ON strategies;
DROP POLICY IF EXISTS "Admins can manage all strategies" ON strategies;

-- 7. RLS 활성화 확인
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;

-- 8. 새로운 정책 생성 - 더 명확하고 강력한 정책

-- 8.1 일반 사용자 SELECT 정책
CREATE POLICY "authenticated_users_can_view_own_strategies" ON strategies
    FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

-- 8.2 일반 사용자 INSERT 정책 (중요: user_id가 자동으로 현재 사용자로 설정되도록)
CREATE POLICY "authenticated_users_can_create_own_strategies" ON strategies
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

-- 8.3 일반 사용자 UPDATE 정책
CREATE POLICY "authenticated_users_can_update_own_strategies" ON strategies
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 8.4 일반 사용자 DELETE 정책
CREATE POLICY "authenticated_users_can_delete_own_strategies" ON strategies
    FOR DELETE
    TO authenticated
    USING (auth.uid() = user_id);

-- 8.5 관리자 전체 접근 정책
CREATE POLICY "admins_can_manage_all_strategies" ON strategies
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'admin'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'admin'
        )
    );

-- 9. 트리거 생성: user_id 자동 설정
-- INSERT 시 user_id가 NULL이거나 현재 사용자와 다르면 자동으로 현재 사용자로 설정
CREATE OR REPLACE FUNCTION set_user_id_on_strategies_insert()
RETURNS TRIGGER AS $$
BEGIN
    -- user_id가 NULL이거나 현재 사용자와 다르면 현재 사용자로 설정
    IF NEW.user_id IS NULL OR NEW.user_id != auth.uid() THEN
        NEW.user_id := auth.uid();
    END IF;

    -- created_at과 updated_at 설정
    IF NEW.created_at IS NULL THEN
        NEW.created_at := NOW();
    END IF;

    NEW.updated_at := NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 기존 트리거 삭제 후 새로 생성
DROP TRIGGER IF EXISTS set_strategies_user_id_trigger ON strategies;
CREATE TRIGGER set_strategies_user_id_trigger
    BEFORE INSERT ON strategies
    FOR EACH ROW
    EXECUTE FUNCTION set_user_id_on_strategies_insert();

-- 10. UPDATE 트리거: updated_at 자동 설정
CREATE OR REPLACE FUNCTION set_updated_at_on_strategies()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_strategies_updated_at_trigger ON strategies;
CREATE TRIGGER set_strategies_updated_at_trigger
    BEFORE UPDATE ON strategies
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at_on_strategies();

-- ====================================================================
-- 검증 및 테스트
-- ====================================================================

-- 11. 새로 생성된 정책 확인
SELECT
    'Updated RLS Policies' as info;

SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'strategies'
ORDER BY policyname;

-- 12. 테스트 전략 생성 (실제로는 애플리케이션에서 테스트)
-- 주의: 이 쿼리는 실제 사용자가 로그인한 상태에서만 작동
/*
INSERT INTO strategies (name, description, config)
VALUES (
    'Test Strategy - ' || auth.jwt() ->> 'email',
    'RLS 권한 테스트용 전략',
    '{"type": "test", "created_by": "rls_fix_script"}'
);
*/

-- 13. 현재 사용자가 볼 수 있는 전략 확인
SELECT
    'Strategies visible to current user' as info;

SELECT
    id,
    name,
    user_id,
    created_at,
    CASE
        WHEN user_id = auth.uid() THEN 'MY_STRATEGY'
        ELSE 'OTHER_STRATEGY'
    END as ownership
FROM strategies
ORDER BY created_at DESC;

-- 완료 메시지
SELECT 'strategies 테이블 RLS 권한 문제 해결 완료' as status,
       'users can now create, read, update, delete their own strategies' as description;