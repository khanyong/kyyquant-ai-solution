-- Insert Kiwoom API keys with explicit user ID
-- Replace 'YOUR_USER_ID' with your actual user ID

-- IMPORTANT: Replace this with your actual user ID!
-- Based on the logs, your user ID is: f912da32-897f-4dbb-9242-3a438e9733a8

DO $$
DECLARE
  v_user_id UUID := 'f912da32-897f-4dbb-9242-3a438e9733a8'; -- ⬅️ Your user ID
BEGIN
  -- Delete any existing Kiwoom keys for this user
  DELETE FROM user_api_keys
  WHERE user_id = v_user_id
    AND provider = 'kiwoom';

  RAISE NOTICE 'Deleted existing keys';

  -- Insert App Key (test mode)
  INSERT INTO user_api_keys (
    user_id,
    provider,
    key_type,
    key_name,
    encrypted_value,
    is_test_mode,
    is_active
  ) VALUES (
    v_user_id,
    'kiwoom',
    'app_key',
    'Kiwoom App Key',
    encode('iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk'::bytea, 'base64'),
    true,
    true
  );

  RAISE NOTICE 'Inserted app_key';

  -- Insert App Secret (test mode)
  INSERT INTO user_api_keys (
    user_id,
    provider,
    key_type,
    key_name,
    encrypted_value,
    is_test_mode,
    is_active
  ) VALUES (
    v_user_id,
    'kiwoom',
    'app_secret',
    'Kiwoom App Secret',
    encode('9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA'::bytea, 'base64'),
    true,
    true
  );

  RAISE NOTICE 'Inserted app_secret';

  -- Insert Account Number (test mode)
  INSERT INTO user_api_keys (
    user_id,
    provider,
    key_type,
    key_name,
    encrypted_value,
    is_test_mode,
    is_active
  ) VALUES (
    v_user_id,
    'kiwoom',
    'account_number',
    'Kiwoom Account Number',
    encode('81101350-01'::bytea, 'base64'),
    true,
    true
  );

  RAISE NOTICE 'Inserted account_number';
  RAISE NOTICE '✅ All keys inserted successfully!';
END $$;

-- Verify the keys were inserted
SELECT
  id,
  user_id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  is_active,
  LENGTH(encrypted_value) as encrypted_length,
  created_at
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
ORDER BY key_type;

-- Check get_current_mode_info
SELECT get_current_mode_info('f912da32-897f-4dbb-9242-3a438e9733a8'::uuid);

-- Test the condition directly
SELECT EXISTS (
  SELECT 1 FROM user_api_keys
  WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    AND is_test_mode = true
    AND is_active = true
    AND provider = 'kiwoom'
) as test_ready_should_be_true;
