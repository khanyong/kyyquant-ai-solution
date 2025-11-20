-- 키움 계좌 정보 설정
-- 실행: Supabase SQL Editor

-- 1. profiles 테이블에 키움 계좌번호 설정
-- ⚠️ '귀하의_계좌번호'를 실제 키움 모의투자 계좌번호로 변경하세요
UPDATE profiles
SET kiwoom_account = '귀하의_계좌번호'  -- 예: '50000000-01'
WHERE id = auth.uid();

-- 2. 설정 확인
SELECT
  id,
  kiwoom_account,
  created_at
FROM profiles
WHERE id = auth.uid();
