-- RPC 함수 권한 확인 및 수정
-- get_active_strategies_with_universe 함수에 대한 권한 설정

-- 1. 현재 함수 정의 확인
SELECT
    routine_name,
    routine_definition,
    security_type
FROM information_schema.routines
WHERE routine_name = 'get_active_strategies_with_universe';

-- 2. 함수 재생성 (SECURITY DEFINER + 익명 사용자 권한 부여)
CREATE OR REPLACE FUNCTION public.get_active_strategies_with_universe()
RETURNS TABLE (
  strategy_id uuid,
  strategy_name text,
  filter_id uuid,
  filter_name text,
  stock_count int
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN QUERY
  SELECT
    s.id as strategy_id,
    s.name as strategy_name,
    kif.id as filter_id,
    kif.name as filter_name,
    kif.filtered_stocks_count as stock_count
  FROM strategies s
  INNER JOIN strategy_universes su ON s.id = su.strategy_id
  INNER JOIN kw_investment_filters kif ON su.investment_filter_id = kif.id
  WHERE
    s.auto_execute = true
    AND s.is_active = true
    AND su.is_active = true
    AND kif.is_active = true
  ORDER BY s.created_at DESC;
END;
$$;

-- 3. 익명 사용자에게 실행 권한 부여
GRANT EXECUTE ON FUNCTION public.get_active_strategies_with_universe() TO anon;
GRANT EXECUTE ON FUNCTION public.get_active_strategies_with_universe() TO authenticated;

-- 4. 확인
SELECT
    routine_name,
    security_type,
    grantee,
    privilege_type
FROM information_schema.routine_privileges
WHERE routine_name = 'get_active_strategies_with_universe';
