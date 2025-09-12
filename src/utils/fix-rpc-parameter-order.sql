-- RPC 함수 파라미터 순서 문제 해결
-- Supabase는 파라미터를 알파벳 순으로 정렬하는 것으로 보임

-- 1. 기존 함수 삭제
DROP FUNCTION IF EXISTS public.save_user_api_key CASCADE;

-- 2. 알파벳 순서대로 파라미터를 가진 함수 생성
CREATE OR REPLACE FUNCTION public.save_user_api_key(
  p_is_test_mode BOOLEAN,
  p_key_name TEXT,
  p_key_type TEXT,
  p_key_value TEXT,
  p_provider TEXT,
  p_user_id UUID
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
  v_key_id UUID;
BEGIN
  INSERT INTO public.user_api_keys (
    user_id,
    provider,
    key_type,
    key_name,
    encrypted_value,
    is_test_mode,
    is_active
  ) VALUES (
    p_user_id,
    p_provider,
    p_key_type,
    p_key_name,
    encode(p_key_value::bytea, 'base64'),
    p_is_test_mode,
    true
  )
  ON CONFLICT (user_id, provider, key_type, key_name) 
  DO UPDATE SET
    encrypted_value = encode(p_key_value::bytea, 'base64'),
    is_test_mode = EXCLUDED.is_test_mode,
    updated_at = NOW()
  RETURNING id INTO v_key_id;
  
  RETURN v_key_id;
END;
$$;

-- 3. 권한 부여
GRANT EXECUTE ON FUNCTION public.save_user_api_key TO anon, authenticated, service_role;

-- 4. 확인
SELECT 
  proname as function_name,
  proargtypes::regtype[] as arg_types,
  proargnames as arg_names
FROM pg_proc
WHERE proname = 'save_user_api_key'
  AND pronamespace = 'public'::regnamespace;

DO $$
BEGIN
  RAISE NOTICE '✅ Function recreated with alphabetical parameter order';
  RAISE NOTICE '📌 Parameters: p_is_test_mode, p_key_name, p_key_type, p_key_value, p_provider, p_user_id';
END $$;