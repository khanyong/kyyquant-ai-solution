-- 특정 사용자를 관리자로 설정하는 스크립트
-- 사용법: 아래 이메일 주소를 실제 관리자 이메일로 변경하고 실행

-- 1. 이메일로 사용자를 관리자로 설정
UPDATE profiles 
SET 
    is_admin = true,
    is_approved = true,
    approval_status = 'approved',
    approved_at = CURRENT_TIMESTAMP
WHERE email = 'your-email@example.com';  -- 여기에 관리자로 만들 이메일 주소 입력

-- 2. 또는 사용자 ID로 관리자 설정 (Supabase Auth 테이블에서 ID 확인 후)
-- UPDATE profiles 
-- SET 
--     is_admin = true,
--     is_approved = true,
--     approval_status = 'approved',
--     approved_at = CURRENT_TIMESTAMP
-- WHERE id = 'user-uuid-here';  -- 여기에 사용자 UUID 입력

-- 3. 현재 관리자 목록 확인
SELECT 
    id,
    email,
    name,
    is_admin,
    approval_status,
    created_at
FROM profiles 
WHERE is_admin = true
ORDER BY created_at DESC;

-- 4. 관리자 권한 제거 (필요 시)
-- UPDATE profiles 
-- SET is_admin = false
-- WHERE email = 'remove-admin@example.com';