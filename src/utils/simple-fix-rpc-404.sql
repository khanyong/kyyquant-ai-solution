-- SIMPLE FIX FOR RPC FUNCTION 404 ERROR
-- 가장 단순한 형태로 문제 해결

-- 1. 기존 함수 삭제
DROP FUNCTION IF EXISTS public.save_user_api_key CASCADE;

-- 2. 테이블 생성 (없으면)
CREATE TABLE IF NOT EXISTS public.user_api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  provider VARCHAR(50) NOT NULL,
  key_type VARCHAR(50) NOT NULL,
  key_name VARCHAR(100),
  encrypted_value TEXT NOT NULL,
  is_active BOOLEAN DEFAULT true,
  is_test_mode BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, provider, key_type, key_name)
);

-- 3. 가장 단순한 RPC 함수 생성
CREATE OR REPLACE FUNCTION public.save_user_api_key(
  p_user_id UUID,
  p_provider TEXT,
  p_key_type TEXT,
  p_key_name TEXT,
  p_key_value TEXT,
  p_is_test_mode BOOLEAN
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

-- 4. 권한 부여
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.save_user_api_key TO anon, authenticated, service_role;
GRANT ALL ON public.user_api_keys TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.user_api_keys TO anon;

-- 5. RLS 설정
ALTER TABLE public.user_api_keys ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own keys" ON public.user_api_keys;
CREATE POLICY "Users can manage own keys"
  ON public.user_api_keys
  FOR ALL
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- 6. 다른 필요한 함수들도 생성
CREATE OR REPLACE FUNCTION public.delete_user_api_key(
  p_user_id UUID,
  p_key_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
  DELETE FROM public.user_api_keys 
  WHERE id = p_key_id AND user_id = p_user_id;
  
  RETURN FOUND;
END;
$$;

CREATE OR REPLACE FUNCTION public.get_current_mode_info(p_user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
  v_result JSON;
BEGIN
  SELECT json_build_object(
    'current_mode', COALESCE(
      (SELECT current_trading_mode FROM user_profiles_extended WHERE user_id = p_user_id),
      'test'
    ),
    'test_ready', EXISTS (
      SELECT 1 FROM user_api_keys 
      WHERE user_id = p_user_id AND is_test_mode = true AND is_active = true
    ),
    'live_ready', EXISTS (
      SELECT 1 FROM user_api_keys 
      WHERE user_id = p_user_id AND is_test_mode = false AND is_active = true
    ),
    'can_switch_to_live', EXISTS (
      SELECT 1 FROM user_api_keys 
      WHERE user_id = p_user_id AND is_test_mode = false AND is_active = true
    )
  ) INTO v_result;
  
  RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION public.switch_trading_mode(
  p_user_id UUID,
  p_new_mode VARCHAR(20)
)
RETURNS VARCHAR
LANGUAGE plpgsql
AS $$
BEGIN
  -- 프로필이 없으면 생성
  INSERT INTO user_profiles_extended (user_id, current_trading_mode)
  VALUES (p_user_id, p_new_mode)
  ON CONFLICT (user_id) DO UPDATE
  SET current_trading_mode = p_new_mode,
      updated_at = NOW();
  
  RETURN 'Switched to ' || p_new_mode || ' mode';
END;
$$;

-- 권한 부여
GRANT EXECUTE ON FUNCTION public.delete_user_api_key TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_current_mode_info TO authenticated;
GRANT EXECUTE ON FUNCTION public.switch_trading_mode TO authenticated;

-- 7. 함수 확인
SELECT 
  proname as function_name,
  pronargs as arg_count
FROM pg_proc
WHERE proname IN ('save_user_api_key', 'delete_user_api_key', 'get_current_mode_info', 'switch_trading_mode')
  AND pronamespace = 'public'::regnamespace;

-- 8. 완료 메시지
DO $$
BEGIN
  RAISE NOTICE '✅ All RPC functions created successfully!';
  RAISE NOTICE '📌 Please check Supabase Dashboard to ensure functions are exposed via API';
END $$;