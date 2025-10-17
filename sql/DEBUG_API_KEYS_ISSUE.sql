-- Debugging API Keys Insertion Issue
-- Run each section separately and check the output

-- 1. Check current user authentication
SELECT
  auth.uid() as current_user_id,
  CASE
    WHEN auth.uid() IS NULL THEN '❌ Not authenticated'
    ELSE '✅ Authenticated'
  END as auth_status;

-- 2. Check RLS policies on user_api_keys table
SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE tablename = 'user_api_keys';

-- 3. Test a simple INSERT with explicit user ID
-- First, let's see if we can insert with current user
DO $$
DECLARE
  v_user_id uuid;
  v_inserted_id uuid;
BEGIN
  v_user_id := auth.uid();

  IF v_user_id IS NULL THEN
    RAISE NOTICE '❌ auth.uid() returned NULL - you are not logged in!';
  ELSE
    RAISE NOTICE '✅ Current user ID: %', v_user_id;

    -- Try to insert a test record
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
      'test',
      'test_key',
      'Test Key',
      encode('test_value'::bytea, 'base64'),
      true,
      true
    )
    ON CONFLICT (user_id, provider, key_type, key_name)
    DO UPDATE SET
      encrypted_value = encode('test_value_updated'::bytea, 'base64'),
      updated_at = NOW()
    RETURNING id INTO v_inserted_id;

    RAISE NOTICE '✅ Test insert successful, ID: %', v_inserted_id;
  END IF;
END $$;

-- 4. Check if test insert worked
SELECT
  id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  is_active
FROM user_api_keys
WHERE provider = 'test';

-- 5. If test insert worked, delete it and try the real Kiwoom keys
DELETE FROM user_api_keys WHERE provider = 'test';

-- 6. Check if RLS is enabled on the table
SELECT
  schemaname,
  tablename,
  rowsecurity
FROM pg_tables
WHERE tablename = 'user_api_keys';

-- 7. Temporarily disable RLS for testing (ONLY FOR DEBUGGING)
-- Run this if you suspect RLS is blocking INSERTs
-- ALTER TABLE user_api_keys DISABLE ROW LEVEL SECURITY;

-- 8. Try inserting Kiwoom App Key with more detailed error handling
DO $$
DECLARE
  v_user_id uuid;
  v_result uuid;
BEGIN
  v_user_id := auth.uid();

  IF v_user_id IS NULL THEN
    RAISE EXCEPTION 'Not authenticated. Please log in first.';
  END IF;

  RAISE NOTICE 'Attempting to insert Kiwoom App Key for user: %', v_user_id;

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
    encode('S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU'::bytea, 'base64'),
    true,
    true
  )
  ON CONFLICT (user_id, provider, key_type, key_name)
  DO UPDATE SET
    encrypted_value = encode('S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU'::bytea, 'base64'),
    is_test_mode = true,
    is_active = true,
    updated_at = NOW()
  RETURNING id INTO v_result;

  RAISE NOTICE '✅ App Key inserted/updated successfully, ID: %', v_result;

  -- Insert App Secret
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
    encode('tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA'::bytea, 'base64'),
    true,
    true
  )
  ON CONFLICT (user_id, provider, key_type, key_name)
  DO UPDATE SET
    encrypted_value = encode('tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA'::bytea, 'base64'),
    is_test_mode = true,
    is_active = true,
    updated_at = NOW()
  RETURNING id INTO v_result;

  RAISE NOTICE '✅ App Secret inserted/updated successfully, ID: %', v_result;

EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE '❌ Error: %', SQLERRM;
    RAISE;
END $$;

-- 9. Final verification
SELECT
  id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  is_active,
  created_at,
  updated_at
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 10. Count check
SELECT
  'API Keys' as type,
  COUNT(*) as count
FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom' AND is_active = true;
