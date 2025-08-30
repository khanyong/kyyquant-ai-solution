-- Enhanced email verification timestamp synchronization
-- This script ensures email_verified_at is properly synced between auth.users and profiles

-- 1. First ensure the columns exist
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE;

-- 2. Create or replace the profile creation trigger to handle initial state
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profiles (
        id, 
        email, 
        name,
        email_verified,
        email_verified_at,
        created_at,
        updated_at
    )
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
        CASE WHEN NEW.email_confirmed_at IS NOT NULL THEN true ELSE false END,
        NEW.email_confirmed_at,
        NOW(),
        NOW()
    )
    ON CONFLICT (id) DO UPDATE
    SET 
        email = EXCLUDED.email,
        email_verified = CASE WHEN NEW.email_confirmed_at IS NOT NULL THEN true ELSE false END,
        email_verified_at = NEW.email_confirmed_at,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Recreate the trigger for new users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();

-- 4. Create a specific function for email verification updates
CREATE OR REPLACE FUNCTION sync_email_verification_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update if email_confirmed_at changed from NULL to a timestamp
    IF OLD.email_confirmed_at IS NULL AND NEW.email_confirmed_at IS NOT NULL THEN
        UPDATE profiles 
        SET 
            email_verified = true,
            email_verified_at = NEW.email_confirmed_at,
            updated_at = NOW()
        WHERE id = NEW.id;
        
        RAISE LOG 'Email verification synced for user %', NEW.id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. Create trigger for email verification updates
DROP TRIGGER IF EXISTS on_email_verification ON auth.users;
CREATE TRIGGER on_email_verification
    AFTER UPDATE OF email_confirmed_at ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION sync_email_verification_status();

-- 6. Fix any existing mismatched data
UPDATE profiles p
SET 
    email_verified = true,
    email_verified_at = u.email_confirmed_at,
    updated_at = NOW()
FROM auth.users u
WHERE p.id = u.id 
    AND u.email_confirmed_at IS NOT NULL 
    AND (p.email_verified_at IS NULL OR p.email_verified = false);

-- 7. Create a function to manually sync a specific user (for testing)
CREATE OR REPLACE FUNCTION manual_sync_email_verification(user_id UUID)
RETURNS void AS $$
DECLARE
    auth_confirmed_at TIMESTAMP WITH TIME ZONE;
BEGIN
    SELECT email_confirmed_at INTO auth_confirmed_at
    FROM auth.users
    WHERE id = user_id;
    
    IF auth_confirmed_at IS NOT NULL THEN
        UPDATE profiles
        SET 
            email_verified = true,
            email_verified_at = auth_confirmed_at,
            updated_at = NOW()
        WHERE id = user_id;
        
        RAISE NOTICE 'Manually synced email verification for user %', user_id;
    ELSE
        RAISE NOTICE 'User % has not confirmed email yet', user_id;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. Verification check query
SELECT 
    p.id,
    p.email,
    p.email_verified as profile_verified,
    p.email_verified_at as profile_verified_at,
    u.email_confirmed_at as auth_confirmed_at,
    CASE 
        WHEN u.email_confirmed_at IS NOT NULL AND p.email_verified_at IS NOT NULL THEN '✓ Fully Synced'
        WHEN u.email_confirmed_at IS NOT NULL AND p.email_verified_at IS NULL THEN '⚠ Needs Sync'
        WHEN u.email_confirmed_at IS NULL THEN '✗ Not Verified'
        ELSE '? Unknown'
    END as sync_status
FROM profiles p
JOIN auth.users u ON p.id = u.id
ORDER BY p.created_at DESC;