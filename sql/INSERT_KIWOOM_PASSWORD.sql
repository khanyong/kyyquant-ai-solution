-- =============================================================================
-- Insert Kiwoom Account Password (Auto-User Detection)
-- Description: Stores the account password in the user_api_keys table.
-- usage: Replace 'YOUR_PASSWORD_HERE' with your actual 4-digit password (e.g. '1234')
-- =============================================================================

INSERT INTO user_api_keys (user_id, provider, key_type, key_name, encrypted_value, is_active)
SELECT 
    id as user_id,                  -- Automatically picks the first found User ID
    'kiwoom'::varchar as provider,
    'account_password'::varchar as key_type,
    'kiwoom_account_password'::varchar as key_name,
    'YOUR_PASSWORD_HERE',           -- <=== 여기에 실제 비밀번호 4자리를 입력하세요!
    true
FROM auth.users
LIMIT 1                             -- Assume single user system
ON CONFLICT (user_id, provider, key_type, key_name)
DO UPDATE SET
    encrypted_value = EXCLUDED.encrypted_value,
    updated_at = NOW();

-- Verification
SELECT provider, key_type, key_name, encrypted_value FROM user_api_keys WHERE key_type = 'account_password';
