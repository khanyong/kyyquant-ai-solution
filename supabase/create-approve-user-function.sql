-- approve_user 함수 생성
-- 관리자가 사용자를 승인/거부하는 기능

-- 기존 함수가 있으면 삭제
DROP FUNCTION IF EXISTS public.approve_user CASCADE;

-- approve_user 함수 생성
CREATE OR REPLACE FUNCTION public.approve_user(
    p_user_id UUID,
    p_admin_id UUID,
    p_approval_status VARCHAR(20),
    p_reason TEXT DEFAULT NULL
)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_is_admin BOOLEAN;
    v_admin_role VARCHAR(50);
    v_result json;
BEGIN
    -- 관리자 권한 확인 (is_admin 또는 role이 admin/super_admin인지)
    SELECT 
        COALESCE(is_admin, false),
        role
    INTO 
        v_is_admin,
        v_admin_role
    FROM profiles 
    WHERE id = p_admin_id;
    
    -- 관리자 존재 여부 확인
    IF v_admin_role IS NULL THEN
        RETURN json_build_object(
            'success', false,
            'error', 'Admin user not found'
        );
    END IF;
    
    -- 관리자 권한 확인 (is_admin이 true이거나 role이 admin/super_admin)
    IF NOT v_is_admin AND v_admin_role NOT IN ('admin', 'super_admin') THEN
        RETURN json_build_object(
            'success', false,
            'error', 'Only administrators can approve users'
        );
    END IF;
    
    -- 사용자 프로필 업데이트
    UPDATE profiles 
    SET 
        is_approved = CASE WHEN p_approval_status = 'approved' THEN true ELSE false END,
        approval_status = p_approval_status,
        approved_by = p_admin_id,
        approved_at = CURRENT_TIMESTAMP,
        rejection_reason = CASE WHEN p_approval_status = 'rejected' THEN p_reason ELSE NULL END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_user_id;
    
    -- 업데이트 성공 여부 확인
    IF NOT FOUND THEN
        RETURN json_build_object(
            'success', false,
            'error', 'User not found'
        );
    END IF;
    
    -- 승인 로그 테이블이 있으면 로그 기록
    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'approval_logs'
    ) THEN
        INSERT INTO approval_logs (user_id, admin_id, action, reason, created_at)
        VALUES (p_user_id, p_admin_id, p_approval_status, p_reason, CURRENT_TIMESTAMP);
    END IF;
    
    -- 성공 응답 반환
    RETURN json_build_object(
        'success', true,
        'message', 'User ' || p_approval_status || ' successfully',
        'user_id', p_user_id,
        'status', p_approval_status
    );
    
EXCEPTION
    WHEN OTHERS THEN
        -- 오류 발생 시 오류 정보 반환
        RETURN json_build_object(
            'success', false,
            'error', 'Database error: ' || SQLERRM
        );
END;
$$;

-- 함수에 대한 권한 부여
GRANT EXECUTE ON FUNCTION public.approve_user(UUID, UUID, VARCHAR, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.approve_user(UUID, UUID, VARCHAR, TEXT) TO anon;

-- 함수에 대한 설명 추가
COMMENT ON FUNCTION public.approve_user(UUID, UUID, VARCHAR, TEXT) IS 
'관리자가 사용자를 승인하거나 거부하는 함수. 
Parameters:
- p_user_id: 승인/거부할 사용자 ID
- p_admin_id: 관리자 ID
- p_approval_status: approved 또는 rejected
- p_reason: 거부 사유 (선택사항)';

-- 함수가 제대로 생성되었는지 확인
SELECT 
    proname AS function_name,
    pg_get_function_identity_arguments(oid) AS arguments,
    obj_description(oid, 'pg_proc') AS description
FROM pg_proc 
WHERE proname = 'approve_user' 
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');