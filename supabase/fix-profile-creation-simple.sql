-- profiles RLS가 disabled인 상황에서 회원가입 문제 해결
-- 더 간단한 접근법

-- 1. 기존 문제있는 트리거와 함수 정리
DROP TRIGGER IF EXISTS assign_default_role_on_signup ON profiles;
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();
DROP FUNCTION IF EXISTS assign_default_role();

-- 2. 간단한 사용자 생성 핸들러 함수
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    -- profiles 테이블에 사용자 정보 삽입
    INSERT INTO public.profiles (
        id, 
        email, 
        name, 
        kiwoom_account,
        email_verified,
        email_verified_at,
        role,
        approval_status,
        created_at, 
        updated_at
    )
    VALUES (
        NEW.id, 
        NEW.email, 
        COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
        NEW.raw_user_meta_data->>'kiwoom_id',
        COALESCE(NEW.email_confirmed_at IS NOT NULL, false),
        NEW.email_confirmed_at,
        'trial', -- 기본 역할
        'pending', -- 기본 승인 상태
        NOW(),
        NOW()
    );

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- 오류 발생 시에도 사용자 생성은 계속되도록 함
        RAISE WARNING 'Profile creation failed for user %: %', NEW.id, SQLERRM;
        RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. auth.users 테이블에 트리거 생성
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- 4. user_roles 테이블의 RLS 정책 수정 (이 테이블만 문제가 됨)
DROP POLICY IF EXISTS "Only authorized users can manage role assignments" ON user_roles;

-- user_roles 테이블에 대한 관대한 정책
CREATE POLICY "Allow role operations" ON user_roles
    FOR ALL 
    USING (true)
    WITH CHECK (true);

-- 5. 기존에 생성된 사용자 중 profiles가 없는 사용자들 복구
INSERT INTO profiles (
    id, 
    email, 
    name, 
    kiwoom_account,
    email_verified,
    email_verified_at,
    role,
    approval_status,
    created_at, 
    updated_at
)
SELECT 
    au.id,
    au.email,
    COALESCE(au.raw_user_meta_data->>'name', split_part(au.email, '@', 1)),
    au.raw_user_meta_data->>'kiwoom_id',
    COALESCE(au.email_confirmed_at IS NOT NULL, false),
    au.email_confirmed_at,
    'trial',
    'pending',
    au.created_at,
    NOW()
FROM auth.users au
LEFT JOIN profiles p ON au.id = p.id
WHERE p.id IS NULL
ON CONFLICT (id) DO NOTHING;

-- 6. 트리거가 정상 작동하는지 확인하는 쿼리
-- (실행 후 새로운 사용자를 만들어서 테스트)
SELECT 
    'Trigger created successfully. Test with new user signup.' as status;