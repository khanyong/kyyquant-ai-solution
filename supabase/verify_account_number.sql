-- 계좌번호 확인

SELECT
  '프로필 계좌번호' as source,
  kiwoom_account,
  email
FROM profiles
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
