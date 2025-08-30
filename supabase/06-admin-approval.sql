-- Step 6: 관리자 승인 시스템 추가

-- profiles 테이블에 승인 관련 필드 추가
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS approval_status VARCHAR(20) DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected')),
ADD COLUMN IF NOT EXISTS approved_by UUID,
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS rejection_reason TEXT,
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE;

-- 승인 로그 테이블 생성
CREATE TABLE IF NOT EXISTS approval_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    admin_id UUID REFERENCES profiles(id),
    action VARCHAR(20) CHECK (action IN ('approve', 'reject', 'pending')),
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 관리자 확인 함수
CREATE OR REPLACE FUNCTION is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM profiles 
        WHERE id = user_id AND is_admin = true
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 사용자 승인 함수
CREATE OR REPLACE FUNCTION approve_user(
    p_user_id UUID,
    p_admin_id UUID,
    p_approval_status VARCHAR(20),
    p_reason TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_is_admin BOOLEAN;
BEGIN
    -- 관리자 권한 확인
    SELECT is_admin INTO v_is_admin FROM profiles WHERE id = p_admin_id;
    
    IF NOT v_is_admin THEN
        RAISE EXCEPTION 'Only administrators can approve users';
    END IF;
    
    -- 프로필 업데이트
    UPDATE profiles 
    SET 
        is_approved = CASE WHEN p_approval_status = 'approved' THEN true ELSE false END,
        approval_status = p_approval_status,
        approved_by = p_admin_id,
        approved_at = CURRENT_TIMESTAMP,
        rejection_reason = CASE WHEN p_approval_status = 'rejected' THEN p_reason ELSE NULL END
    WHERE id = p_user_id;
    
    -- 승인 로그 추가
    INSERT INTO approval_logs (user_id, admin_id, action, reason)
    VALUES (p_user_id, p_admin_id, p_approval_status, p_reason);
    
    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 이메일 인증 확인 트리거
CREATE OR REPLACE FUNCTION handle_email_verification()
RETURNS TRIGGER AS $$
BEGIN
    -- Supabase auth의 이메일 인증이 완료되면 profiles 업데이트
    UPDATE profiles 
    SET 
        email_verified = true,
        email_verified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id AND NEW.email_confirmed_at IS NOT NULL;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- auth.users 테이블의 변경 감지 트리거
CREATE TRIGGER on_auth_user_verified
    AFTER UPDATE ON auth.users
    FOR EACH ROW 
    WHEN (OLD.email_confirmed_at IS NULL AND NEW.email_confirmed_at IS NOT NULL)
    EXECUTE FUNCTION handle_email_verification();

-- RLS 정책 업데이트
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;

-- 승인된 사용자만 자신의 프로필 조회 가능
CREATE POLICY "Approved users can view own profile" ON profiles
    FOR SELECT USING (
        auth.uid() = id 
        OR EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_admin = true)
    );

-- 승인된 사용자만 자신의 프로필 수정 가능
CREATE POLICY "Approved users can update own profile" ON profiles
    FOR UPDATE USING (
        auth.uid() = id AND is_approved = true
    );

-- 관리자는 모든 프로필 조회 가능
CREATE POLICY "Admins can view all profiles" ON profiles
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_admin = true)
    );

-- 관리자는 모든 프로필 수정 가능
CREATE POLICY "Admins can update all profiles" ON profiles
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_admin = true)
    );

-- 승인 로그 RLS
ALTER TABLE approval_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can view approval logs" ON approval_logs
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_admin = true)
    );

CREATE POLICY "Users can view own approval logs" ON approval_logs
    FOR SELECT USING (auth.uid() = user_id);

-- 기본 관리자 계정 생성 (이메일은 실제 관리자 이메일로 변경)
INSERT INTO profiles (id, email, name, is_admin, is_approved, approval_status)
VALUES (
    gen_random_uuid(),
    'admin@kyyquant.ai',
    'System Administrator',
    true,
    true,
    'approved'
) ON CONFLICT (email) DO UPDATE SET is_admin = true, is_approved = true;

-- 대기 중인 사용자 조회 뷰
CREATE OR REPLACE VIEW pending_users AS
SELECT 
    p.id,
    p.email,
    p.name,
    p.kiwoom_account,
    p.created_at,
    p.email_verified,
    p.approval_status
FROM profiles p
WHERE p.approval_status = 'pending'
ORDER BY p.created_at DESC;