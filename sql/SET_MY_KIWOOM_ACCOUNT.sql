-- 내 계좌번호 설정 (키움 모의투자 계좌번호 입력 필요)
-- 계좌번호 형식: 12345678-01 (8자리-2자리)

-- 현재 설정된 계좌번호 확인
SELECT
  id,
  email,
  kiwoom_account,
  CASE
    WHEN kiwoom_account IS NULL OR kiwoom_account = '' THEN '❌ 계좌번호 미설정'
    ELSE '✅ 계좌번호: ' || kiwoom_account
  END as status
FROM profiles
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 계좌번호 설정 (아래 계좌번호를 실제 키움 모의투자 계좌로 변경하세요)
UPDATE profiles
SET
  kiwoom_account = '81101350-01'
  updated_at = NOW()
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 설정 확인
SELECT
  id,
  email,
  kiwoom_account,
  updated_at,
  '✅ 계좌번호 설정 완료' as status
FROM profiles
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 최종 확인: 키와 계좌번호가 모두 있는지 체크
SELECT
  (SELECT COUNT(*) FROM user_api_keys WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND provider = 'kiwoom' AND key_type = 'app_key' AND is_active = true) as app_key_count,
  (SELECT COUNT(*) FROM user_api_keys WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND provider = 'kiwoom' AND key_type = 'app_secret' AND is_active = true) as app_secret_count,
  (SELECT kiwoom_account FROM profiles WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8') as kiwoom_account,
  CASE
    WHEN (SELECT COUNT(*) FROM user_api_keys WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND provider = 'kiwoom' AND key_type IN ('app_key', 'app_secret') AND is_active = true) >= 2
         AND (SELECT kiwoom_account FROM profiles WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8') IS NOT NULL
         AND (SELECT kiwoom_account FROM profiles WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8') != ''
    THEN '✅ 모든 설정 완료 - Edge Function 배포 가능'
    ELSE '⚠️ 설정 미완료 - 계좌번호 또는 API 키 확인 필요'
  END as ready_status;
