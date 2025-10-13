-- Insert Kiwoom API keys from .env file into user_api_keys table
-- This will resolve the "키움API 초기화 중" error

-- First, check current user ID
SELECT auth.uid() as current_user_id;

-- Delete any existing Kiwoom keys for this user (optional - clean slate)
DELETE FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom';

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
  auth.uid(),
  'kiwoom',
  'app_key',
  'Kiwoom App Key',
  encode('iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk'::bytea, 'base64'),
  true,  -- is_test_mode = true (모의투자)
  true
)
ON CONFLICT (user_id, provider, key_type, key_name)
DO UPDATE SET
  encrypted_value = encode('iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk'::bytea, 'base64'),
  is_test_mode = true,
  is_active = true,
  updated_at = NOW();

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
  auth.uid(),
  'kiwoom',
  'app_secret',
  'Kiwoom App Secret',
  encode('9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA'::bytea, 'base64'),
  true,  -- is_test_mode = true (모의투자)
  true
)
ON CONFLICT (user_id, provider, key_type, key_name)
DO UPDATE SET
  encrypted_value = encode('9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA'::bytea, 'base64'),
  is_test_mode = true,
  is_active = true,
  updated_at = NOW();

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
  auth.uid(),
  'kiwoom',
  'account_number',
  'Kiwoom Account Number',
  encode('81101350-01'::bytea, 'base64'),
  true,  -- is_test_mode = true (모의투자)
  true
)
ON CONFLICT (user_id, provider, key_type, key_name)
DO UPDATE SET
  encrypted_value = encode('81101350-01'::bytea, 'base64'),
  is_test_mode = true,
  is_active = true,
  updated_at = NOW();

-- Verify the keys were inserted
SELECT
  id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  is_active,
  created_at
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- Check get_current_mode_info again
SELECT get_current_mode_info(auth.uid());
