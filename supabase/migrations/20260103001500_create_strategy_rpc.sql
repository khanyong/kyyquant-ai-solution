-- Migration: Create/Update RPC for Strategy Execution Engine
-- file: supabase/migrations/20260103001500_create_strategy_rpc.sql

-- Drop existing function first to allow return type changes
DROP FUNCTION IF EXISTS get_active_strategies_with_universe();

CREATE OR REPLACE FUNCTION get_active_strategies_with_universe()
RETURNS TABLE (
    strategy_id UUID,
    strategy_name TEXT,
    config JSONB,
    entry_conditions JSONB,
    exit_conditions JSONB,
    allocated_capital NUMERIC,
    allocated_percent NUMERIC,
    universes JSONB,
    filtered_stocks JSONB -- Legacy field
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id::UUID AS strategy_id,
        s.name::TEXT AS strategy_name,
        s.config::JSONB,
        s.entry_conditions::JSONB,
        s.exit_conditions::JSONB,
        COALESCE(s.allocated_capital, 0)::NUMERIC AS allocated_capital,
        COALESCE(s.allocated_percent, 0)::NUMERIC AS allocated_percent,
        COALESCE(
            (
                SELECT jsonb_agg(
                    jsonb_build_object(
                        'universe_id', su.investment_filter_id,
                        'universe_name', f.name,
                        'filtered_stocks', f.filtered_stocks
                    )
                )
                FROM strategy_universes su
                JOIN kw_investment_filters f ON su.investment_filter_id = f.id
                WHERE su.strategy_id = s.id AND su.is_active = true
            ),
            '[]'::jsonb
        )::JSONB AS universes,
        '[]'::jsonb AS filtered_stocks
    FROM strategies s
    WHERE s.is_active = true;
END;
$$ LANGUAGE plpgsql;
