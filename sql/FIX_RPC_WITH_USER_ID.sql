-- RPC 함수 수정: user_id 포함하여 반환 (n8n 워크플로우 호환성 수정)

DROP FUNCTION IF EXISTS public.get_active_strategies_with_universe();

CREATE OR REPLACE FUNCTION public.get_active_strategies_with_universe()
RETURNS TABLE (
  strategy_id uuid,
  user_id uuid,          -- [NEW] Added user_id
  strategy_name text,
  entry_conditions jsonb,
  exit_conditions jsonb,
  filter_id uuid,
  filter_name text,
  stock_count int,
  filtered_stocks jsonb,
  allocated_capital numeric,
  allocated_percent numeric
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN QUERY
  SELECT
    s.id as strategy_id,
    s.user_id,           -- [NEW] Select user_id
    s.name::text as strategy_name,
    s.entry_conditions,
    s.exit_conditions,
    kif.id as filter_id,
    kif.name::text as filter_name,
    kif.filtered_stocks_count as stock_count,
    kif.filtered_stocks as filtered_stocks,
    s.allocated_capital,
    s.allocated_percent
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

-- 권한 부여
GRANT EXECUTE ON FUNCTION public.get_active_strategies_with_universe() TO anon;
GRANT EXECUTE ON FUNCTION public.get_active_strategies_with_universe() TO authenticated;
