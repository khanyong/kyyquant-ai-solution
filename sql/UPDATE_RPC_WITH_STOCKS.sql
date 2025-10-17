-- RPC 함수 수정: filtered_stocks 포함하여 반환

CREATE OR REPLACE FUNCTION public.get_active_strategies_with_universe()
RETURNS TABLE (
  strategy_id uuid,
  strategy_name text,
  entry_conditions jsonb,
  exit_conditions jsonb,
  filter_id uuid,
  filter_name text,
  stock_count int,
  filtered_stocks text[]  -- 종목 코드 배열 추가
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
    s.entry_conditions,
    s.exit_conditions,
    kif.id as filter_id,
    kif.name as filter_name,
    kif.filtered_stocks_count as stock_count,
    kif.filtered_stocks as filtered_stocks  -- 종목 코드 배열
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
