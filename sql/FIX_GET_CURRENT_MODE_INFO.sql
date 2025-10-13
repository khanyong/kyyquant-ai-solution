-- Fix get_current_mode_info function to work without user_profiles_extended table
-- This function should default to 'test' mode if the table doesn't exist or has no data

DROP FUNCTION IF EXISTS public.get_current_mode_info(UUID) CASCADE;

CREATE OR REPLACE FUNCTION public.get_current_mode_info(p_user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_current_mode VARCHAR(20);
  v_test_ready BOOLEAN;
  v_live_ready BOOLEAN;
  v_result JSON;
BEGIN
  -- Check if user_profiles_extended table exists and get mode, default to 'test'
  BEGIN
    SELECT current_trading_mode INTO v_current_mode
    FROM user_profiles_extended
    WHERE user_id = p_user_id;

    IF v_current_mode IS NULL THEN
      v_current_mode := 'test';
    END IF;
  EXCEPTION WHEN OTHERS THEN
    -- If table doesn't exist or any error, default to test mode
    v_current_mode := 'test';
  END;

  -- Check if test mode keys exist
  SELECT EXISTS (
    SELECT 1 FROM user_api_keys
    WHERE user_id = p_user_id
      AND is_test_mode = true
      AND is_active = true
      AND provider = 'kiwoom'
  ) INTO v_test_ready;

  -- Check if live mode keys exist
  SELECT EXISTS (
    SELECT 1 FROM user_api_keys
    WHERE user_id = p_user_id
      AND is_test_mode = false
      AND is_active = true
      AND provider = 'kiwoom'
  ) INTO v_live_ready;

  -- Build result JSON
  v_result := json_build_object(
    'current_mode', v_current_mode,
    'test_ready', v_test_ready,
    'live_ready', v_live_ready,
    'can_switch_to_live', v_live_ready
  );

  RETURN v_result;
END;
$$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.get_current_mode_info TO authenticated, anon;

-- Test the function
SELECT get_current_mode_info(auth.uid());
