-- email_verified_at 타임스탬프 문제 해결

-- 1. profiles 테이블에 필요한 컬럼 확인 및 추가
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE;

-- 2. auth.users의 email_confirmed_at을 profiles에 동기화하는 함수
CREATE OR REPLACE FUNCTION sync_email_verification()
RETURNS TRIGGER AS $$
BEGIN
    -- 이메일 인증이 완료되면 profiles 업데이트
    IF NEW.email_confirmed_at IS NOT NULL THEN
        UPDATE profiles 
        SET 
            email_verified = true,
            email_verified_at = NEW.email_confirmed_at,
            updated_at = NOW()
        WHERE id = NEW.id;
        
        RAISE NOTICE 'Email verified for user %: %', NEW.id, NEW.email;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. 기존 트리거 삭제
DROP TRIGGER IF EXISTS sync_email_verification_trigger ON auth.users;

-- 4. 새 트리거 생성
CREATE TRIGGER sync_email_verification_trigger
    AFTER INSERT OR UPDATE OF email_confirmed_at ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION sync_email_verification();

-- 5. 기존 사용자들의 email_verified_at 업데이트 (이미 인증된 사용자)
UPDATE profiles p
SET 
    email_verified = true,
    email_verified_at = u.email_confirmed_at
FROM auth.users u
WHERE p.id = u.id 
    AND u.email_confirmed_at IS NOT NULL 
    AND p.email_verified_at IS NULL;

-- 6. 디버깅용: 현재 상태 확인 쿼리
SELECT 
    p.id,
    p.email,
    p.email_verified,
    p.email_verified_at,
    u.email_confirmed_at as auth_confirmed_at,
    CASE 
        WHEN u.email_confirmed_at IS NOT NULL THEN 'Auth Confirmed'
        WHEN p.email_verified = true THEN 'Profile Verified'
        ELSE 'Not Verified'
    END as verification_status
FROM profiles p
JOIN auth.users u ON p.id = u.id
ORDER BY p.created_at DESC;