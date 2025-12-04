-- =============================================================================
-- Function: get_buy_candidates
-- Description: Returns buy candidates that meet condition score AND have sufficient capital.
-- Updated: To join with strategy_capital_status and return available budget.
-- =============================================================================

-- Drop the existing function first because we are changing the return type
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
  available_for_next_order numeric -- [NEW] Available budget for this trade
)
LANGUAGE sql
SECURITY DEFINER
AS $function$
  SELECT 
    sm.strategy_id,
    sm.stock_code,
    sm.stock_name,
    sm.current_price,
    sm.condition_match_score,
    s.name as strategy_name,
    s.position_size,
    s.entry_conditions,
    sm.conditions_met,
    scs.available_for_next_order -- [NEW] Return calculated available amount
  FROM strategy_monitoring sm
  JOIN strategies s ON s.id = sm.strategy_id
  JOIN strategy_capital_status scs ON scs.strategy_id = sm.strategy_id
  WHERE sm.condition_match_score >= min_score
  AND sm.is_near_entry = true
  -- [NEW] Capital Check: Must have enough budget to buy at least 1 share (approx check)
  -- We use a loose check (> 0) here, and precise check in n8n
  AND scs.available_for_next_order > 0 
  AND NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.strategy_id = sm.strategy_id
    AND o.stock_code = sm.stock_code
    AND o.status IN ('PENDING', 'PARTIAL', 'FILLED')
    AND o.created_at > NOW() - INTERVAL '1 day'
  );
$function$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.get_buy_candidates(integer) TO service_role;
GRANT EXECUTE ON FUNCTION public.get_buy_candidates(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_buy_candidates(integer) TO anon;
