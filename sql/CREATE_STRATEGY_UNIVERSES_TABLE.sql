-- Strategy ↔ investment filter mapping table (single source of truth)
-- Removes the need for strategies.target_stocks: universes live here + kw_investment_filters

CREATE TABLE IF NOT EXISTS strategy_universes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id uuid NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    investment_filter_id uuid NOT NULL REFERENCES kw_investment_filters(id) ON DELETE CASCADE,
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    -- Prevent duplicate mappings
    UNIQUE(strategy_id, investment_filter_id)
);

CREATE INDEX IF NOT EXISTS idx_strategy_universes_strategy
    ON strategy_universes(strategy_id);

CREATE INDEX IF NOT EXISTS idx_strategy_universes_filter
    ON strategy_universes(investment_filter_id);

CREATE INDEX IF NOT EXISTS idx_strategy_universes_active
    ON strategy_universes(is_active) WHERE is_active = true;

-- Auto-update updated_at on change
CREATE OR REPLACE FUNCTION update_strategy_universes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_strategy_universes_updated_at ON strategy_universes;
CREATE TRIGGER trg_strategy_universes_updated_at
BEFORE UPDATE ON strategy_universes
FOR EACH ROW
EXECUTE FUNCTION update_strategy_universes_updated_at();

-- Sample read query: active strategies mapped to active filters
SELECT
    s.id AS strategy_id,
    s.name AS strategy_name,
    s.auto_execute,
    s.auto_trade_enabled,
    kif.id AS filter_id,
    kif.name AS filter_name,
    kif.filtered_stocks_count,
    jsonb_array_length(kif.filtered_stocks) AS actual_stock_count,
    kif.filtered_stocks -> 0 AS first_stock,
    kif.filtered_stocks -> 1 AS second_stock,
    kif.filtered_stocks -> 2 AS third_stock
FROM strategies s
INNER JOIN strategy_universes su ON s.id = su.strategy_id
INNER JOIN kw_investment_filters kif ON su.investment_filter_id = kif.id
WHERE s.auto_execute = true
  AND s.is_active = true
  AND su.is_active = true
  AND kif.is_active = true;
