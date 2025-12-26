-- =============================================================================
-- Patch: Secure Halt Logic
-- Description: Adds strict `is_active = true` check to `get_buy_candidates`.
--              This ensures that even if valid signals exist in `strategy_monitoring`,
--              they are IGNORED if the strategy has been halted by the Emergency Button.
-- =============================================================================

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
  candidate_count bigint
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
    AND s.is_active = true  -- [PATCH] Critical Safety Check
    AND s.auto_trade_enabled = true -- [PATCH] Double Safety
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
    c.condition_match_score DESC,
    c.volume DESC,
    c.stock_code ASC;
$function$;
