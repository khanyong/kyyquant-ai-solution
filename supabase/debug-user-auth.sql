-- ====================================================================
-- 사용자 인증 상태 디버깅 스크립트
-- 목적: 일반 사용자가 전략 저장에 실패하는 원인 파악
-- ====================================================================

-- 1. 현재 세션 정보 확인
SELECT
    '=== 현재 세션 정보 ===' as section,
    auth.uid() as user_id,
    auth.role() as user_role,
    auth.jwt() as jwt_token,
    session_user as database_user,
    current_user as current_database_user;

-- 2. JWT 토큰 상세 분석
SELECT
    '=== JWT 토큰 상세 정보 ===' as section,
    auth.jwt() ->> 'aud' as audience,
    auth.jwt() ->> 'exp' as expires_at,
    auth.jwt() ->> 'sub' as subject,
    auth.jwt() ->> 'email' as email,
    auth.jwt() ->> 'role' as role,
    auth.jwt() ->> 'aal' as authentication_assurance_level;

-- 3. 인증된 사용자인지 확인
SELECT
    '=== 인증 상태 확인 ===' as section,
    CASE
        WHEN auth.uid() IS NULL THEN 'NOT_AUTHENTICATED'
        WHEN auth.role() = 'authenticated' THEN 'AUTHENTICATED'
        WHEN auth.role() = 'anon' THEN 'ANONYMOUS'
        ELSE 'UNKNOWN_ROLE: ' || auth.role()
    END as auth_status;

-- 4. profiles 테이블에서 사용자 정보 확인
SELECT
    '=== 프로필 정보 ===' as section,
    p.id,
    p.email,
    p.role,
    p.created_at,
    CASE
        WHEN p.id = auth.uid() THEN 'PROFILE_MATCH'
        WHEN p.id IS NULL THEN 'NO_PROFILE_FOUND'
        ELSE 'PROFILE_MISMATCH'
    END as profile_status
FROM profiles p
WHERE p.id = auth.uid()
UNION ALL
SELECT
    '=== 프로필 정보 ===' as section,
    NULL as id,
    'NO_PROFILE_EXISTS' as email,
    NULL as role,
    NULL as created_at,
    'NO_PROFILE_FOUND' as profile_status
WHERE NOT EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid());

-- 5. strategies 테이블에 대한 권한 테스트
SELECT
    '=== 전략 테이블 권한 테스트 ===' as section,
    'SELECT' as operation,
    CASE
        WHEN EXISTS (
            SELECT 1 FROM strategies
            WHERE user_id = auth.uid()
            LIMIT 1
        ) THEN 'CAN_SELECT_OWN_STRATEGIES'
        WHEN EXISTS (
            SELECT 1 FROM strategies
            LIMIT 1
        ) THEN 'CAN_SELECT_BUT_NO_OWN_STRATEGIES'
        ELSE 'NO_STRATEGIES_EXIST_OR_CANNOT_SELECT'
    END as result;

-- 6. INSERT 권한 테스트를 위한 준비 (실제 INSERT는 하지 않음)
SELECT
    '=== INSERT 권한 준비 상태 ===' as section,
    auth.uid() as would_use_user_id,
    CASE
        WHEN auth.uid() IS NULL THEN 'CANNOT_INSERT_NO_USER_ID'
        WHEN auth.role() != 'authenticated' THEN 'CANNOT_INSERT_NOT_AUTHENTICATED'
        ELSE 'READY_FOR_INSERT'
    END as insert_readiness;

-- 7. 현재 적용된 RLS 정책 확인
SELECT
    '=== 현재 RLS 정책 ===' as section,
    policyname,
    cmd as command,
    CASE
        WHEN 'authenticated' = ANY(roles) THEN 'FOR_AUTHENTICATED_USERS'
        WHEN roles IS NULL THEN 'FOR_ALL_ROLES'
        ELSE 'FOR_SPECIFIC_ROLES: ' || array_to_string(roles, ', ')
    END as target_roles,
    qual as using_condition,
    with_check as with_check_condition
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'strategies'
ORDER BY cmd, policyname;

-- 8. 문제 해결 제안
SELECT
    '=== 문제 해결 제안 ===' as section,
    CASE
        WHEN auth.uid() IS NULL THEN
            '1. 사용자가 로그인되어 있지 않습니다. 프론트엔드에서 Supabase.auth.signIn() 확인 필요'
        WHEN auth.role() != 'authenticated' THEN
            '2. 사용자가 인증되지 않았습니다. JWT 토큰 상태 확인 필요'
        WHEN NOT EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid()) THEN
            '3. profiles 테이블에 사용자 정보가 없습니다. 회원가입 과정 확인 필요'
        ELSE
            '4. 인증 상태는 정상입니다. RLS 정책 또는 애플리케이션 로직 확인 필요'
    END as recommendation;

-- 9. 애플리케이션에서 확인해야 할 사항들
SELECT
    '=== 프론트엔드 체크리스트 ===' as section,
    '체크 항목' as item,
    '확인 방법' as check_method
UNION ALL
SELECT
    '',
    '1. 사용자 로그인 상태',
    'console.log(supabase.auth.getUser())'
UNION ALL
SELECT
    '',
    '2. JWT 토큰 존재',
    'console.log(supabase.auth.getSession())'
UNION ALL
SELECT
    '',
    '3. API 요청 헤더',
    'Network 탭에서 Authorization 헤더 확인'
UNION ALL
SELECT
    '',
    '4. 전략 저장 시 user_id',
    'INSERT 쿼리에 user_id 포함 여부 확인'
UNION ALL
SELECT
    '',
    '5. 에러 메시지',
    'Supabase 콘솔에서 상세 오류 로그 확인';