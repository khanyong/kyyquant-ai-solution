-- Debug why test_ready is still false

-- 1. Check if keys were actually inserted
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
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 2. Check the exact condition used in get_current_mode_info
SELECT EXISTS (
  SELECT 1 FROM user_api_keys
  WHERE user_id = auth.uid()
    AND is_test_mode = true
    AND is_active = true
    AND provider = 'kiwoom'
) as test_ready_condition;

-- 3. Count keys by type
SELECT
  key_type,
  COUNT(*) as count,
  is_test_mode,
  is_active
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
GROUP BY key_type, is_test_mode, is_active
ORDER BY key_type;

-- 4. Check if there are ANY keys at all for this user
SELECT COUNT(*) as total_keys
FROM user_api_keys
WHERE user_id = auth.uid();

-- 5. Show current user
SELECT auth.uid() as current_user_id;
