-- user_api_keys_view 생성
-- API 키 값을 마스킹하여 안전하게 표시

DROP VIEW IF EXISTS public.user_api_keys_view;

CREATE OR REPLACE VIEW public.user_api_keys_view AS
SELECT 
  id,
  user_id,
  provider,
  key_type,
  key_name,
  is_active,
  is_test_mode,
  last_used_at,
  expires_at,
  created_at,
  updated_at,
  -- 키 값을 마스킹
  CASE 
    WHEN key_type IN ('app_secret', 'cert_password', 'api_password') THEN '••••••••'
    ELSE SUBSTRING(encrypted_value, 1, 4) || '••••'
  END as masked_value
FROM public.user_api_keys;

-- 뷰에 대한 권한 부여
GRANT SELECT ON public.user_api_keys_view TO authenticated;
GRANT SELECT ON public.user_api_keys_view TO anon;

-- RLS 정책은 기본 테이블의 정책을 따름

-- 확인
SELECT COUNT(*) as view_count FROM public.user_api_keys_view;

DO $$
BEGIN
  RAISE NOTICE '✅ user_api_keys_view created successfully';
END $$;