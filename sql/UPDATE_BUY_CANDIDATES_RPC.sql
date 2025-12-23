-- =============================================================================
-- Function: get_buy_candidates
-- Description: Returns buy candidates with Equal Distribution Logic.
--              1. Counts total candidates for the strategy.
--              2. Calculates budget per stock = Available / Count.
--              3. Sets position_size = MIN(Strategy Fixed Size, Budget per Stock).
--              4. Sorts by Volume DESC to prioritize liquid stocks.
-- =============================================================================

DROP FUNCTION IF EXISTS public.get_buy_candidates(integer);

CREATE OR REPLACE FUNCTION public.get_buy_candidates(min_score integer DEFAULT 100)
RETURNS TABLE(
  strategy_id uuid,
  stock_code text,
  stock_name text,
  current_price numeric,
  condition_match_score numeric,
  strategy_name text,
  position_size numeric,
  entry_conditions jsonb,
  conditions_met jsonb,
  available_for_next_order numeric,
  candidate_count bigint -- Debug info
)
LANGUAGE sql
SECURITY DEFINER
AS $function$
  WITH candidate_list AS (
    SELECT 
      sm.strategy_id,
      sm.stock_code,
      sm.stock_name,
      sm.current_price,
      sm.condition_match_score,
      sm.conditions_met,
      s.name as strategy_name,
      s.position_size as fixed_position_size,
      s.entry_conditions,
      scs.available_for_next_order as total_available_budget,
      COALESCE(kpc.volume, 0) as volume
    FROM strategy_monitoring sm
    JOIN strategies s ON s.id = sm.strategy_id
    JOIN strategy_capital_status scs ON scs.strategy_id = sm.strategy_id
    LEFT JOIN kw_price_current kpc ON kpc.stock_code = sm.stock_code
    WHERE sm.condition_match_score >= min_score
    AND sm.is_near_entry = true
    AND scs.available_for_next_order > 0 
    AND NOT EXISTS (
      SELECT 1 FROM orders o
      WHERE o.strategy_id = sm.strategy_id
      AND o.stock_code = sm.stock_code
      AND o.status IN ('PENDING', 'PARTIAL', 'FILLED')
      AND o.created_at > NOW() - INTERVAL '1 day'
    )
  ),
  counts AS (
    SELECT strategy_id, COUNT(*) as total_candidates 
    FROM candidate_list 
    GROUP BY strategy_id
  )
  SELECT 
    c.strategy_id,
    c.stock_code,
    c.stock_name,
    c.current_price,
    c.condition_match_score,
    c.strategy_name,
    -- Logic: LEAST(Fixed Size, Total Available / Count)
    -- We assume minimum trade amount (e.g. 10000 KRW) to avoid tiny dust orders? 
    -- For now, simple division. 
    LEAST(
        c.fixed_position_size, 
        FLOOR(c.total_available_budget / GREATEST(cnt.total_candidates, 1))
    ) as position_size,
    c.entry_conditions,
    c.conditions_met,
    c.total_available_budget,
    cnt.total_candidates
  FROM candidate_list c
  JOIN counts cnt ON cnt.strategy_id = c.strategy_id
  ORDER BY 
    c.condition_match_score DESC, -- 1. High score first (though usually all 100)
    c.volume DESC,                -- 2. High volume first (Liquidity)
    c.stock_code ASC;             -- 3. Deterministic tie-breaker
$function$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.get_buy_candidates(integer) TO service_role;
GRANT EXECUTE ON FUNCTION public.get_buy_candidates(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_buy_candidates(integer) TO anon;
