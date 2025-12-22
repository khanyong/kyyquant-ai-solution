-- Function: get_buy_candidates
-- Updated: Added ORDER BY to prioritize high-scoring candidates
-- This ensures that when multiple signals exist, the best ones are bought first
-- AND we try to respect budget by processing the "best" opportunities before budget runs out.

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
  available_for_next_order numeric
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
    scs.available_for_next_order
  FROM strategy_monitoring sm
  JOIN strategies s ON s.id = sm.strategy_id
  JOIN strategy_capital_status scs ON scs.strategy_id = sm.strategy_id
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
  ORDER BY sm.condition_match_score DESC, scs.available_for_next_order DESC;
$function$;

-- Grant permissions (just in case)
GRANT EXECUTE ON FUNCTION public.get_buy_candidates(integer) TO service_role;
GRANT EXECUTE ON FUNCTION public.get_buy_candidates(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_buy_candidates(integer) TO anon;
