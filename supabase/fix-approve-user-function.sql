-- Fix for approve_user function
-- This script creates or replaces the approve_user function with the correct parameter order

-- First, drop the existing function if it exists (with various parameter combinations)
DROP FUNCTION IF EXISTS public.approve_user(UUID, UUID, VARCHAR, TEXT);
DROP FUNCTION IF EXISTS public.approve_user(UUID, VARCHAR, TEXT, UUID);

-- Create the approve_user function with correct parameter order
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
    
    -- Insert into approval_logs if the table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'approval_logs') THEN
        INSERT INTO approval_logs (user_id, admin_id, action, reason, created_at)
        VALUES (p_user_id, p_admin_id, p_approval_status, p_reason, CURRENT_TIMESTAMP);
    END IF;
    
    RETURN true;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error in approve_user: %', SQLERRM;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.approve_user(UUID, UUID, VARCHAR, TEXT) TO authenticated;

-- Verify the function exists
SELECT 
    proname AS function_name,
    pg_get_function_identity_arguments(oid) AS arguments
FROM pg_proc 
WHERE proname = 'approve_user' 
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');