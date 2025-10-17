-- 새 키움 계좌번호로 업데이트

-- 1. 현재 설정된 계좌번호 확인
SELECT
  id,
  kiwoom_account,
  updated_at
FROM profiles
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 2. 새 계좌번호로 업데이트 (81126101-01)
UPDATE profiles
SET
  kiwoom_account = '81126101-01',
  updated_at = NOW()
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 3. 업데이트 확인
SELECT
  id,
  kiwoom_account,
  updated_at
FROM profiles
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
