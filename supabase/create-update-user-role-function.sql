-- 사용자 역할 변경 함수
-- 관리자가 사용자의 역할을 변경하는 기능

-- 기존 함수 삭제
DROP FUNCTION IF EXISTS public.update_user_role CASCADE;

-- update_user_role 함수 생성
CREATE OR REPLACE FUNCTION public.update_user_role(
    p_user_id UUID,
    p_admin_id UUID,
    p_new_role VARCHAR(50)
)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_is_admin BOOLEAN;
    v_admin_role VARCHAR(50);
    v_old_role VARCHAR(50);
BEGIN
    -- 관리자 권한 확인
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
    
    -- 관리자 권한 확인
    IF NOT v_is_admin AND v_admin_role NOT IN ('admin', 'super_admin') THEN
        RETURN json_build_object(
            'success', false,
            'error', 'Only administrators can change user roles'
        );
    END IF;
    
    -- 현재 역할 가져오기
    SELECT role INTO v_old_role 
    FROM profiles 
    WHERE id = p_user_id;
    
    IF v_old_role IS NULL THEN
        RETURN json_build_object(
            'success', false,
            'error', 'User not found'
        );
    END IF;
    
    -- 역할 변경
    UPDATE profiles 
    SET 
        role = p_new_role,
        -- admin 역할인 경우 is_admin도 업데이트
        is_admin = CASE 
            WHEN p_new_role IN ('admin', 'super_admin') THEN true 
            ELSE false 
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_user_id;
    
    -- 성공 응답
    RETURN json_build_object(
        'success', true,
        'message', 'User role updated successfully',
        'user_id', p_user_id,
        'old_role', v_old_role,
        'new_role', p_new_role
    );
    
EXCEPTION
    WHEN OTHERS THEN
        RETURN json_build_object(
            'success', false,
            'error', 'Database error: ' || SQLERRM
        );
END;
$$;

-- 권한 부여
GRANT EXECUTE ON FUNCTION public.update_user_role(UUID, UUID, VARCHAR) TO authenticated;

-- 함수 설명 추가
COMMENT ON FUNCTION public.update_user_role(UUID, UUID, VARCHAR) IS 
'관리자가 사용자의 역할을 변경하는 함수.
Parameters:
- p_user_id: 역할을 변경할 사용자 ID
- p_admin_id: 관리자 ID
- p_new_role: 새로운 역할 (trial, standard, premium, admin, super_admin)';

-- 함수 확인
SELECT 
    proname AS function_name,
    pg_get_function_identity_arguments(oid) AS arguments
FROM pg_proc 
WHERE proname = 'update_user_role' 
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');