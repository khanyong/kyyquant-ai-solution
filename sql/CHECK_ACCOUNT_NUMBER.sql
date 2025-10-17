-- 현재 설정된 계좌번호 확인
SELECT
  id,
  email,
  kiwoom_account,
  LENGTH(kiwoom_account) as account_length,
  POSITION('-' IN kiwoom_account) as hyphen_position
FROM profiles
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
