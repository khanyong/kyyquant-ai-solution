-- ====================================================================
-- 사용자별 전략 저장 플로우 디버깅
-- 목적: 외부 사이트에서 로그인한 사용자의 전략 저장 문제 진단
-- ====================================================================

-- 1. 현재 인증된 사용자 정보
SELECT
    '=== 현재 사용자 인증 상태 ===' as info;

SELECT
    auth.uid() as current_user_id,
    auth.role() as user_role,
    auth.jwt() ->> 'email' as user_email,
    auth.jwt() ->> 'aud' as audience,
    auth.jwt() ->> 'exp' as expires_at,
    CASE
        WHEN auth.uid() IS NULL THEN '❌ 로그인되지 않음'
        WHEN auth.role() = 'authenticated' THEN '✅ 인증된 사용자'
        ELSE '⚠️ 알 수 없는 상태: ' || auth.role()
    END as auth_status;

-- 2. 프로필 테이블에서 사용자 확인
SELECT
    '=== 사용자 프로필 정보 ===' as info;

SELECT
    p.id,
    p.email,
    p.role,
    p.created_at,
    CASE
        WHEN p.id = auth.uid() THEN '✅ 프로필 일치'
        WHEN p.id IS NULL THEN '❌ 프로필 없음'
        ELSE '⚠️ 프로필 불일치'
    END as profile_status
FROM profiles p
WHERE p.id = auth.uid()
UNION ALL
SELECT
    'NO_PROFILE' as id,
    'NOT_FOUND' as email,
    NULL as role,
    NULL as created_at,
    '❌ 프로필이 존재하지 않음' as profile_status
WHERE NOT EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid());

-- 3. 현재 사용자의 전략 조회 (RLS 정책 테스트)
SELECT
    '=== 현재 사용자의 전략 ===' as info;

SELECT
    COUNT(*) as my_strategy_count,
    MAX(created_at) as latest_strategy_date
FROM strategies
WHERE user_id = auth.uid();

-- 전략 상세 정보
SELECT
    id,
    name,
    user_id,
    created_at,
    updated_at
FROM strategies
WHERE user_id = auth.uid()
ORDER BY created_at DESC
LIMIT 5;

-- 4. 전체 전략 개수 (관리자만 볼 수 있음)
SELECT
    '=== 전체 전략 통계 (관리자만) ===' as info;

SELECT
    COUNT(*) as total_strategies,
    COUNT(DISTINCT user_id) as unique_users,
    MAX(created_at) as latest_created
FROM strategies;

-- 5. 전략 저장 테스트 준비 상태
SELECT
    '=== 전략 저장 가능 여부 ===' as info;

SELECT
    CASE
        WHEN auth.uid() IS NULL THEN
            '❌ 불가능: 사용자가 로그인되어 있지 않습니다'
        WHEN auth.role() != 'authenticated' THEN
            '❌ 불가능: 사용자가 인증되지 않았습니다'
        WHEN NOT EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid()) THEN
            '⚠️ 주의: 프로필이 없습니다 (회원가입 과정 확인 필요)'
        ELSE
            '✅ 가능: 전략 저장이 가능한 상태입니다'
    END as save_status,
    auth.uid() as would_save_with_user_id;

-- 6. RLS 정책 상태 확인
SELECT
    '=== 현재 적용된 RLS 정책 ===' as info;

SELECT
    policyname,
    cmd as operation,
    CASE
        WHEN 'authenticated' = ANY(roles) THEN '✅ 인증 사용자용'
        WHEN roles IS NULL THEN '⚠️ 모든 역할'
        ELSE '❓ 특정 역할: ' || array_to_string(roles, ', ')
    END as target_users,
    qual as condition_check
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'strategies'
ORDER BY cmd, policyname;

-- 7. 문제 해결 가이드
SELECT
    '=== 문제 해결 가이드 ===' as info;

SELECT
    CASE
        WHEN auth.uid() IS NULL THEN
            '1. 프론트엔드에서 사용자 로그인 상태를 확인하세요: supabase.auth.getUser()'
        WHEN auth.role() != 'authenticated' THEN
            '2. JWT 토큰이 유효한지 확인하세요: supabase.auth.getSession()'
        WHEN NOT EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid()) THEN
            '3. 회원가입 과정에서 profiles 테이블에 사용자 정보가 생성되는지 확인하세요'
        ELSE
            '4. 프론트엔드에서 전략 저장 시 API 요청 헤더에 Authorization 토큰이 포함되는지 확인하세요'
    END as next_step;

-- 8. 프론트엔드 체크리스트
SELECT
    '=== 프론트엔드 확인사항 ===' as info,
    '확인 항목' as check_item,
    '확인 방법' as how_to_check
UNION ALL
SELECT
    '', '1. 사용자 로그인 상태', 'const { data: user } = await supabase.auth.getUser()'
UNION ALL
SELECT
    '', '2. 세션 토큰 존재', 'const { data: session } = await supabase.auth.getSession()'
UNION ALL
SELECT
    '', '3. API 요청 헤더', 'Network 탭에서 Authorization: Bearer <token> 확인'
UNION ALL
SELECT
    '', '4. 전략 저장 요청', 'POST 요청에 user_id가 자동 설정되는지 확인'
UNION ALL
SELECT
    '', '5. 에러 응답 확인', 'Console에서 상세한 에러 메시지 확인';

-- 완료 메시지
SELECT '사용자별 전략 저장 디버깅 완료' as status;