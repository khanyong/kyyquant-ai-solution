-- profiles 테이블에 누락된 avatar_url 컬럼 추가
-- Supabase SQL Editor에서 실행

-- 1. avatar_url 컬럼이 없다면 추가
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS avatar_url text;

-- 2. 컬럼이 제대로 추가되었는지 확인
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'profiles' 
AND column_name = 'avatar_url';

-- 3. 기존 사용자들의 avatar_url을 기본값으로 설정 (선택사항)
UPDATE profiles 
SET avatar_url = NULL 
WHERE avatar_url IS NULL;

-- 4. 성공 메시지
SELECT 'avatar_url column added successfully' as status;