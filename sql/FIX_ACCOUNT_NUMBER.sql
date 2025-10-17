-- 올바른 키움 계좌번호로 수정
-- 실제 계좌번호: 81126100 (키움 포털에서 확인)
-- 계좌번호 형식: 81126100-01 (계좌번호-계좌상품코드)

-- 현재 설정된 계좌번호 확인
SELECT
  id,
  email,
  kiwoom_account as current_account,
  '81126100-01' as correct_account
FROM profiles
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 올바른 계좌번호로 업데이트
UPDATE profiles
SET
  kiwoom_account = '81126100-01',
  updated_at = NOW()
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 업데이트 확인
SELECT
  id,
  email,
  kiwoom_account,
  updated_at,
  '✅ 계좌번호 수정 완료' as status
FROM profiles
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
