-- 사용자 역할 변경 스크립트

-- 1. 특정 사용자를 관리자로 변경
UPDATE profiles 
SET 
    role = 'admin',
    is_admin = true,
    updated_at = NOW()
WHERE email = 'your-email@example.com';  -- 여기에 실제 이메일 주소 입력

-- 2. 특정 사용자를 일반 회원으로 변경
UPDATE profiles 
SET 
    role = 'standard',
    updated_at = NOW()
WHERE id = 'user-uuid-here';  -- 여기에 사용자 ID 입력

-- 3. 승인된 모든 사용자를 일반 회원으로 변경
UPDATE profiles 
SET 
    role = 'standard',
    updated_at = NOW()
WHERE 
    approval_status = 'approved' 
    AND role = 'trial';

-- 4. 역할별 사용자 수 확인
SELECT 
    role, 
    COUNT(*) as user_count 
FROM profiles 
GROUP BY role 
ORDER BY role;

-- 5. 현재 사용자 목록 및 역할 확인
SELECT 
    id,
    email,
    name,
    role,
    is_admin,
    approval_status,
    created_at
FROM profiles
ORDER BY created_at DESC;