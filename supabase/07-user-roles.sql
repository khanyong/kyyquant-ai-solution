-- Step 7: 사용자 역할(Role) 시스템 추가

-- profiles 테이블에 role 필드 추가
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user',
ADD COLUMN IF NOT EXISTS permissions JSONB DEFAULT '{}';

-- 역할 정의 테이블
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}',
    level INTEGER DEFAULT 0, -- 권한 레벨 (높을수록 권한이 많음)
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 기본 역할 추가
INSERT INTO roles (name, display_name, description, permissions, level) VALUES
    ('super_admin', '최고 관리자', '모든 권한을 가진 최고 관리자', 
     '{"all": true, "manage_users": true, "manage_roles": true, "manage_system": true, "trading": true, "premium_features": true}', 
     100),
    
    ('admin', '관리자', '사용자 관리 및 시스템 관리 권한', 
     '{"manage_users": true, "view_all_users": true, "approve_users": true, "trading": true, "premium_features": true}', 
     80),
    
    ('moderator', '운영자', '사용자 승인 및 기본 관리 권한', 
     '{"approve_users": true, "view_pending_users": true, "trading": true, "premium_features": true}', 
     60),
    
    ('premium', '프리미엄 회원', '프리미엄 기능 사용 가능', 
     '{"trading": true, "premium_features": true, "advanced_analytics": true, "unlimited_strategies": true, "api_access": true}', 
     40),
    
    ('standard', '일반 회원', '기본 기능 사용 가능', 
     '{"trading": true, "basic_features": true, "limited_strategies": true, "max_strategies": 5}', 
     20),
    
    ('trial', '체험 회원', '제한된 기능 체험 가능', 
     '{"trading": false, "demo_mode": true, "basic_features": true, "max_strategies": 2}', 
     10),
    
    ('suspended', '정지', '계정 정지 상태', 
     '{"trading": false, "view_only": true}', 
     0)
ON CONFLICT (name) DO NOTHING;

-- 사용자-역할 매핑 테이블 (다중 역할 지원)
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES profiles(id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE, -- 역할 만료 시간 (옵션)
    is_active BOOLEAN DEFAULT true,
    UNIQUE(user_id, role_id)
);

-- 역할 권한 확인 함수
CREATE OR REPLACE FUNCTION check_user_permission(
    p_user_id UUID,
    p_permission VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    v_has_permission BOOLEAN := false;
BEGIN
    -- 사용자의 모든 활성 역할에서 권한 확인
    SELECT EXISTS (
        SELECT 1
        FROM profiles p
        JOIN user_roles ur ON p.id = ur.user_id
        JOIN roles r ON ur.role_id = r.id
        WHERE 
            p.id = p_user_id
            AND ur.is_active = true
            AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
            AND r.is_active = true
            AND (
                r.permissions->>'all' = 'true' 
                OR r.permissions->>p_permission = 'true'
                OR p.permissions->>p_permission = 'true'
            )
    ) INTO v_has_permission;
    
    RETURN v_has_permission;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 사용자 역할 할당 함수
CREATE OR REPLACE FUNCTION assign_role_to_user(
    p_user_id UUID,
    p_role_name VARCHAR,
    p_assigned_by UUID,
    p_expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_role_id UUID;
    v_can_assign BOOLEAN;
BEGIN
    -- 할당하는 사람이 권한이 있는지 확인
    SELECT check_user_permission(p_assigned_by, 'manage_roles') INTO v_can_assign;
    
    IF NOT v_can_assign THEN
        RAISE EXCEPTION 'You do not have permission to assign roles';
    END IF;
    
    -- 역할 ID 가져오기
    SELECT id INTO v_role_id FROM roles WHERE name = p_role_name AND is_active = true;
    
    IF v_role_id IS NULL THEN
        RAISE EXCEPTION 'Role not found or inactive';
    END IF;
    
    -- 역할 할당
    INSERT INTO user_roles (user_id, role_id, assigned_by, expires_at)
    VALUES (p_user_id, v_role_id, p_assigned_by, p_expires_at)
    ON CONFLICT (user_id, role_id) 
    DO UPDATE SET 
        assigned_by = p_assigned_by,
        assigned_at = CURRENT_TIMESTAMP,
        expires_at = p_expires_at,
        is_active = true;
    
    -- profiles 테이블의 role 필드도 업데이트 (가장 높은 레벨의 역할)
    UPDATE profiles p
    SET role = (
        SELECT r.name
        FROM user_roles ur
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.user_id = p.id 
            AND ur.is_active = true
            AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
        ORDER BY r.level DESC
        LIMIT 1
    )
    WHERE p.id = p_user_id;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 사용자 생성 시 기본 역할 할당 트리거
CREATE OR REPLACE FUNCTION assign_default_role()
RETURNS TRIGGER AS $$
DECLARE
    v_default_role_id UUID;
BEGIN
    -- 기본 역할 (trial) 가져오기
    SELECT id INTO v_default_role_id FROM roles WHERE name = 'trial';
    
    -- 기본 역할 할당
    INSERT INTO user_roles (user_id, role_id, assigned_by)
    VALUES (NEW.id, v_default_role_id, NEW.id);
    
    -- profiles 테이블 업데이트
    UPDATE profiles SET role = 'trial' WHERE id = NEW.id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성
CREATE TRIGGER assign_default_role_on_signup
    AFTER INSERT ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION assign_default_role();

-- 역할 기반 RLS 정책 추가
CREATE POLICY "Users with manage_users can view all profiles" ON profiles
    FOR SELECT USING (
        check_user_permission(auth.uid(), 'manage_users')
    );

CREATE POLICY "Users with manage_users can update profiles" ON profiles
    FOR UPDATE USING (
        check_user_permission(auth.uid(), 'manage_users')
    );

-- 역할 테이블 RLS
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view active roles" ON roles
    FOR SELECT USING (is_active = true);

CREATE POLICY "Only admins can manage roles" ON roles
    FOR ALL USING (
        check_user_permission(auth.uid(), 'manage_roles')
    );

CREATE POLICY "Users can view own role assignments" ON user_roles
    FOR SELECT USING (
        user_id = auth.uid() 
        OR check_user_permission(auth.uid(), 'view_all_users')
    );

CREATE POLICY "Only authorized users can manage role assignments" ON user_roles
    FOR ALL USING (
        check_user_permission(auth.uid(), 'manage_roles')
    );

-- 역할별 기능 제한 뷰
CREATE OR REPLACE VIEW user_permissions AS
SELECT DISTINCT
    p.id as user_id,
    p.email,
    p.name,
    r.name as role_name,
    r.display_name as role_display_name,
    r.level as role_level,
    jsonb_object_agg(
        COALESCE(key, 'none'), 
        COALESCE(value, 'false')
    ) OVER (PARTITION BY p.id) as all_permissions
FROM profiles p
LEFT JOIN user_roles ur ON p.id = ur.user_id AND ur.is_active = true
LEFT JOIN roles r ON ur.role_id = r.id AND r.is_active = true
LEFT JOIN LATERAL jsonb_each(
    COALESCE(r.permissions, '{}') || COALESCE(p.permissions, '{}')
) AS permissions(key, value) ON true
WHERE ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP;

-- 관리자 대시보드용 사용자 통계 뷰
CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    COUNT(*) FILTER (WHERE approval_status = 'pending') as pending_users,
    COUNT(*) FILTER (WHERE approval_status = 'approved') as approved_users,
    COUNT(*) FILTER (WHERE approval_status = 'rejected') as rejected_users,
    COUNT(*) FILTER (WHERE role = 'premium') as premium_users,
    COUNT(*) FILTER (WHERE role = 'standard') as standard_users,
    COUNT(*) FILTER (WHERE role = 'trial') as trial_users,
    COUNT(*) FILTER (WHERE email_verified = true) as verified_emails,
    COUNT(*) FILTER (WHERE created_at > CURRENT_DATE - INTERVAL '7 days') as new_users_week,
    COUNT(*) FILTER (WHERE created_at > CURRENT_DATE - INTERVAL '30 days') as new_users_month
FROM profiles;