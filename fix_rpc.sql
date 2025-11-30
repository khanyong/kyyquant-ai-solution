
-- Fix RPC Function for Auto Trading Dashboard
-- Run this in Supabase Dashboard -> SQL Editor

DROP FUNCTION IF EXISTS public.get_active_strategies_with_universe();

CREATE OR REPLACE FUNCTION public.get_active_strategies_with_universe()
RETURNS TABLE(
  strategy_id uuid,
  strategy_name text,
  entry_conditions jsonb,
  exit_conditions jsonb,
  allocated_capital numeric,
  allocated_percent numeric,
  filter_id uuid,
  filter_name text,
  user_id uuid,
  universe jsonb,
  filtered_stocks jsonb
)
LANGUAGE sql
SECURITY DEFINER
AS $function$
  SELECT
    s.id AS strategy_id,
    s.name AS strategy_name,
    s.entry_conditions,
    s.exit_conditions,
    COALESCE(scs.allocated_capital, s.allocated_capital, 0) AS allocated_capital,
    COALESCE(scs.allocated_percent, s.allocated_percent, 0) AS allocated_percent,
    f.id AS filter_id,
    f.name AS filter_name,
    s.user_id,
    -- Use strategy universe (cast to jsonb) if available, otherwise use filter's filtered_stocks (already jsonb)
    COALESCE(to_jsonb(s.universe), f.filtered_stocks) AS universe,
    COALESCE(to_jsonb(s.universe), f.filtered_stocks) AS filtered_stocks
  FROM
    strategies s
    JOIN strategy_capital_status scs ON s.id = scs.strategy_id
    LEFT JOIN strategy_universes su ON s.id = su.strategy_id AND su.is_active = true
    LEFT JOIN kw_investment_filters f ON su.investment_filter_id = f.id
  WHERE
    s.is_active = true -- Strategy definition exists
    AND scs.is_active = true -- My instance is active
    AND s.auto_trade_enabled = true -- Strategy allows auto trading
    AND s.auto_execute = true -- Strategy allows auto execution
    AND (
      -- Case 1: Service Role (n8n/Admin) - See ALL active strategies
      (current_setting('request.jwt.claim.role', true) = 'service_role')
      OR
      (current_setting('role', true) = 'service_role')
      OR
      -- Case 2: Authenticated User - See ONLY my strategies
      (s.user_id = auth.uid())
    );
$function$;

GRANT EXECUTE ON FUNCTION public.get_active_strategies_with_universe() TO service_role;
GRANT EXECUTE ON FUNCTION public.get_active_strategies_with_universe() TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_active_strategies_with_universe() TO anon;
