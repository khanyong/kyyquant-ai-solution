-- 회원가입 시 profiles 테이블에 데이터가 생성되지 않는 문제 해결

-- 1. 기존 문제있는 트리거와 함수 제거
DROP TRIGGER IF EXISTS assign_default_role_on_signup ON profiles;
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();
DROP FUNCTION IF EXISTS assign_default_role();

-- 2. user_roles 테이블의 제한적인 RLS 정책 임시 해제
DROP POLICY IF EXISTS "Only authorized users can manage role assignments" ON user_roles;

-- 3. 새로운 사용자 생성 핸들러 함수 (SECURITY DEFINER로 권한 문제 해결)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
DECLARE
    v_default_role_id uuid;
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
        NOW(),
        NOW()
    );

    -- 기본 역할 ID 가져오기
    SELECT id INTO v_default_role_id FROM roles WHERE name = 'trial';
    
    -- 역할이 존재하면 user_roles에도 추가
    IF v_default_role_id IS NOT NULL THEN
        INSERT INTO user_roles (user_id, role_id, assigned_by)
        VALUES (NEW.id, v_default_role_id, NEW.id);
    END IF;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- 오류 발생 시에도 사용자 생성은 계속되도록 함
        RAISE WARNING 'Profile creation failed for user %: %', NEW.id, SQLERRM;
        RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. auth.users 테이블에 트리거 생성
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- 5. user_roles 테이블에 대한 더 관대한 RLS 정책 생성
CREATE POLICY "Allow role assignment during signup" ON user_roles
    FOR INSERT 
    WITH CHECK (
        user_id = auth.uid() OR auth.uid() IS NULL
    );

CREATE POLICY "Users can view own roles" ON user_roles
    FOR SELECT USING (
        user_id = auth.uid() 
        OR check_user_permission(auth.uid(), 'view_all_users')
    );

CREATE POLICY "Only authorized can modify roles" ON user_roles
    FOR UPDATE USING (
        check_user_permission(auth.uid(), 'manage_roles')
    );

CREATE POLICY "Only authorized can delete roles" ON user_roles
    FOR DELETE USING (
        check_user_permission(auth.uid(), 'manage_roles')
    );

-- 6. profiles 테이블의 RLS 정책도 더 관대하게 수정
DROP POLICY IF EXISTS "Enable all for profiles based on user_id" ON profiles;

CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (
        id = auth.uid() 
        OR check_user_permission(auth.uid(), 'view_all_users')
    );

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (
        id = auth.uid() OR auth.uid() IS NULL
    );

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (
        id = auth.uid() 
        OR check_user_permission(auth.uid(), 'manage_users')
    );

-- 7. 기존에 생성된 사용자 중 profiles가 없는 사용자들을 위한 복구 스크립트
INSERT INTO profiles (
    id, 
    email, 
    name, 
    kiwoom_account,
    email_verified,
    email_verified_at,
    role,
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
    au.created_at,
    NOW()
FROM auth.users au
LEFT JOIN profiles p ON au.id = p.id
WHERE p.id IS NULL
ON CONFLICT (id) DO NOTHING;