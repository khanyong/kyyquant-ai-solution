-- Supabase RPC Function: 자동매매 활성화된 전략과 투자유니버스 조회
CREATE OR REPLACE FUNCTION get_active_strategies_with_universe()
RETURNS TABLE (
    strategy_id uuid,
    strategy_name text,
    entry_conditions jsonb,
    exit_conditions jsonb,
    filter_id uuid,
    filter_name text,
    filtered_stocks jsonb,
    allocated_capital numeric,
    allocated_percent numeric
)
LANGUAGE sql
SECURITY DEFINER
AS $$
    SELECT
        s.id as strategy_id,
        s.name as strategy_name,
        s.entry_conditions,
        s.exit_conditions,
        kif.id as filter_id,
        kif.name as filter_name,
        kif.filtered_stocks,
        s.allocated_capital,
        s.allocated_percent
    FROM strategies s
    INNER JOIN strategy_universes su ON s.id = su.strategy_id
    INNER JOIN kw_investment_filters kif ON su.investment_filter_id = kif.id
    WHERE s.auto_execute = true
        AND s.is_active = true
        AND su.is_active = true
        AND kif.is_active = true;
$$;

-- 테스트 쿼리
SELECT * FROM get_active_strategies_with_universe();
