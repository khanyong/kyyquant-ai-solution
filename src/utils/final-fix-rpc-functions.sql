-- RPC 함수 404 오류 최종 해결
-- Supabase는 public 스키마의 함수만 RPC로 노출합니다

-- 1. 함수가 public 스키마에 있는지 확인
SELECT 
  n.nspname as schema_name,
  p.proname as function_name,
  pg_get_function_arguments(p.oid) as arguments
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE p.proname IN ('save_user_api_key', 'delete_user_api_key', 'get_current_mode_info')
ORDER BY n.nspname, p.proname;

-- 2. 기존 함수 모두 삭제
DROP FUNCTION IF EXISTS public.save_user_api_key CASCADE;
DROP FUNCTION IF EXISTS save_user_api_key CASCADE;

-- 3. public 스키마에 명시적으로 함수 생성
CREATE OR REPLACE FUNCTION public.save_user_api_key(
  p_user_id UUID,
  p_provider VARCHAR(50),
  p_key_type VARCHAR(50),
  p_key_name VARCHAR(100),
  p_key_value TEXT,
  p_is_test_mode BOOLEAN DEFAULT false
) 
RETURNS UUID 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_key_id UUID;
BEGIN
  -- API 키 저장
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

-- 4. 권한 설정
GRANT EXECUTE ON FUNCTION public.save_user_api_key TO anon;
GRANT EXECUTE ON FUNCTION public.save_user_api_key TO authenticated;
GRANT EXECUTE ON FUNCTION public.save_user_api_key TO service_role;

-- 5. 함수 소유자 변경 (중요!)
ALTER FUNCTION public.save_user_api_key OWNER TO postgres;

-- 6. API에서 함수 노출 확인
DO $$
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '========================================';
  RAISE NOTICE 'RPC 함수 상태 확인';
  RAISE NOTICE '========================================';
  
  -- 함수 존재 확인
  IF EXISTS (
    SELECT 1 FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public' AND p.proname = 'save_user_api_key'
  ) THEN
    RAISE NOTICE '✅ save_user_api_key 함수가 public 스키마에 있습니다';
  ELSE
    RAISE NOTICE '❌ save_user_api_key 함수가 public 스키마에 없습니다';
  END IF;
  
  RAISE NOTICE '';
  RAISE NOTICE '다음 단계:';
  RAISE NOTICE '1. Supabase 대시보드 → Database → Functions 확인';
  RAISE NOTICE '2. save_user_api_key 함수가 보이는지 확인';
  RAISE NOTICE '3. 함수 우측의 "..." → "View Details" 클릭';
  RAISE NOTICE '4. "Exposed via API" 가 활성화되어 있는지 확인';
  RAISE NOTICE '========================================';
END $$;

-- 7. 테스트 쿼리
-- 아래 쿼리로 직접 테스트
SELECT public.save_user_api_key(
  auth.uid(),
  'test',
  'test_key',
  'direct_test',
  'TEST_VALUE_123',
  true
) as test_result;

-- 8. 저장된 데이터 확인
SELECT 
  id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  created_at
FROM user_api_keys
WHERE user_id = auth.uid()
ORDER BY created_at DESC
LIMIT 5;