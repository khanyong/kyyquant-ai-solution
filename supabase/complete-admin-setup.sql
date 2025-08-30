-- Complete Admin Approval System Setup
-- Run this script in Supabase SQL Editor to set up the complete admin approval system

-- Step 1: Ensure profiles table has all necessary columns
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS approval_status VARCHAR(20) DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected')),
ADD COLUMN IF NOT EXISTS approved_by UUID,
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS rejection_reason TEXT,
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE;

-- Step 2: Create approval_logs table if it doesn't exist
CREATE TABLE IF NOT EXISTS approval_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    admin_id UUID REFERENCES profiles(id),
    action VARCHAR(20) CHECK (action IN ('approve', 'reject', 'pending')),
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Step 3: Drop existing function versions
DROP FUNCTION IF EXISTS public.approve_user(UUID, UUID, VARCHAR, TEXT);
DROP FUNCTION IF EXISTS public.approve_user(UUID, VARCHAR, TEXT, UUID);

-- Step 4: Create the approve_user function with correct parameter order
CREATE OR REPLACE FUNCTION public.approve_user(
    p_user_id UUID,
    p_admin_id UUID,
    p_approval_status VARCHAR(20),
    p_reason TEXT DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_is_admin BOOLEAN;
BEGIN
    -- Check if the admin user exists and has admin privileges
    SELECT is_admin INTO v_is_admin 
    FROM profiles 
    WHERE id = p_admin_id;
    
    IF v_is_admin IS NULL THEN
        RAISE EXCEPTION 'Admin user not found';
    END IF;
    
    IF NOT v_is_admin THEN
        RAISE EXCEPTION 'Only administrators can approve users';
    END IF;
    
    -- Update the user's profile
    UPDATE profiles 
    SET 
        is_approved = CASE WHEN p_approval_status = 'approved' THEN true ELSE false END,
        approval_status = p_approval_status,
        approved_by = p_admin_id,
        approved_at = CURRENT_TIMESTAMP,
        rejection_reason = CASE WHEN p_approval_status = 'rejected' THEN p_reason ELSE NULL END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_user_id;
    
    -- Check if update was successful
    IF NOT FOUND THEN
        RAISE EXCEPTION 'User not found';
    END IF;
    
    -- Insert into approval_logs
    INSERT INTO approval_logs (user_id, admin_id, action, reason, created_at)
    VALUES (p_user_id, p_admin_id, p_approval_status, p_reason, CURRENT_TIMESTAMP);
    
    RETURN true;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error in approve_user: %', SQLERRM;
END;
$$;

-- Step 5: Create is_admin helper function
CREATE OR REPLACE FUNCTION public.is_admin(user_id UUID)
RETURNS BOOLEAN 
LANGUAGE plpgsql 
SECURITY DEFINER
AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM profiles 
        WHERE id = user_id AND is_admin = true
    );
END;
$$;

-- Step 6: Grant necessary permissions
GRANT EXECUTE ON FUNCTION public.approve_user(UUID, UUID, VARCHAR, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.is_admin(UUID) TO authenticated;

-- Step 7: Enable RLS on approval_logs
ALTER TABLE approval_logs ENABLE ROW LEVEL SECURITY;

-- Step 8: Create RLS policies for approval_logs
DROP POLICY IF EXISTS "Admins can view approval logs" ON approval_logs;
CREATE POLICY "Admins can view approval logs" ON approval_logs
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_admin = true)
    );

DROP POLICY IF EXISTS "Users can view own approval logs" ON approval_logs;
CREATE POLICY "Users can view own approval logs" ON approval_logs
    FOR SELECT USING (auth.uid() = user_id);

-- Step 9: Create pending users view
CREATE OR REPLACE VIEW pending_users AS
SELECT 
    p.id,
    p.email,
    p.name,
    p.kiwoom_account,
    p.created_at,
    p.email_verified,
    p.approval_status
FROM profiles p
WHERE p.approval_status = 'pending'
ORDER BY p.created_at DESC;

-- Step 10: Grant access to the view
GRANT SELECT ON pending_users TO authenticated;

-- Step 11: Verify the setup
SELECT 
    'Function created' AS status,
    proname AS function_name,
    pg_get_function_identity_arguments(oid) AS arguments
FROM pg_proc 
WHERE proname = 'approve_user' 
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- Step 12: Show current admin users
SELECT 
    id,
    email,
    name,
    is_admin,
    approval_status,
    created_at
FROM profiles 
WHERE is_admin = true
ORDER BY created_at DESC;