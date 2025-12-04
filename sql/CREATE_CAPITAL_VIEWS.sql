-- =============================================================================
-- Drop existing views to avoid column mismatch errors
-- =============================================================================
DROP VIEW IF EXISTS strategy_capital_status CASCADE;
DROP VIEW IF EXISTS strategy_net_positions CASCADE;

-- =============================================================================
-- View: strategy_net_positions
-- Description: Calculates the net number of shares held by each strategy based on order history.
-- =============================================================================
CREATE OR REPLACE VIEW strategy_net_positions AS
SELECT
    o.strategy_id,
    o.stock_code,
    SUM(CASE WHEN o.order_type = 'BUY' THEN COALESCE(o.executed_quantity, 0) ELSE 0 END) -
    SUM(CASE WHEN o.order_type = 'SELL' THEN COALESCE(o.executed_quantity, 0) ELSE 0 END) as net_qty
FROM orders o
WHERE o.status IN ('FILLED', 'PARTIAL')
  AND o.strategy_id IS NOT NULL
GROUP BY o.strategy_id, o.stock_code
HAVING SUM(CASE WHEN o.order_type = 'BUY' THEN COALESCE(o.executed_quantity, 0) ELSE 0 END) -
       SUM(CASE WHEN o.order_type = 'SELL' THEN COALESCE(o.executed_quantity, 0) ELSE 0 END) > 0;

-- =============================================================================
-- View: strategy_capital_status
-- Description: Real-time capital status per strategy (Allocated, Used, Remaining).
-- =============================================================================
CREATE OR REPLACE VIEW strategy_capital_status AS
WITH strategy_config AS (
    SELECT
        id,
        name,
        is_active,
        allocated_capital,
        allocated_percent,
        -- Use the new column if available, otherwise fallback to calculation
        max_investment_per_stock,
        -- Extract maxPositions from config JSON, default to 10 if missing
        COALESCE((config->'riskManagement'->>'maxPositions')::int, 10) as max_positions,
        user_id
    FROM strategies
),
strategy_holdings AS (
    -- Calculate value of stocks held by each strategy
    SELECT
        snp.strategy_id,
        SUM(snp.net_qty * COALESCE(kpc.current_price, 0)) as stock_value,
        COUNT(DISTINCT snp.stock_code) as position_count
    FROM strategy_net_positions snp
    JOIN strategy_config s ON s.id = snp.strategy_id
    LEFT JOIN kw_price_current kpc ON kpc.stock_code = snp.stock_code
    GROUP BY snp.strategy_id
),
pending_orders AS (
    -- Calculate value of pending buy orders
    SELECT
        o.strategy_id,
        SUM(o.quantity * o.order_price) as pending_amount,
        COUNT(DISTINCT o.stock_code) as pending_count
    FROM orders o
    WHERE o.status IN ('PENDING', 'SUBMITTED')
      AND o.order_type = 'BUY'
      AND o.strategy_id IS NOT NULL
    GROUP BY o.strategy_id
)
SELECT
    s.id as strategy_id,
    s.name as strategy_name,
    s.is_active,
    
    -- 1. Allocated Capital
    COALESCE(s.allocated_capital, 0) as allocated_amount,
    
    -- 2. Used Capital
    COALESCE(sh.stock_value, 0) as used_stock_value,
    COALESCE(po.pending_amount, 0) as used_pending_amount,
    (COALESCE(sh.stock_value, 0) + COALESCE(po.pending_amount, 0)) as total_used_amount,
    
    -- 3. Remaining Budget
    (COALESCE(s.allocated_capital, 0) - (COALESCE(sh.stock_value, 0) + COALESCE(po.pending_amount, 0))) as remaining_budget,
    
    -- 4. Position Counts
    COALESCE(sh.position_count, 0) as current_positions,
    COALESCE(po.pending_count, 0) as pending_positions,
    (COALESCE(sh.position_count, 0) + COALESCE(po.pending_count, 0)) as total_positions,
    s.max_positions,
    
    -- 5. Next Order Availability
    -- Logic: Min(Remaining Budget, Max Investment Per Stock)
    CASE 
        WHEN (COALESCE(sh.position_count, 0) + COALESCE(po.pending_count, 0)) >= s.max_positions THEN 0
        ELSE 
            LEAST(
                -- Remaining Budget
                (COALESCE(s.allocated_capital, 0) - (COALESCE(sh.stock_value, 0) + COALESCE(po.pending_amount, 0))),
                -- Max Investment Per Stock (Explicit column OR Calculated)
                COALESCE(
                    s.max_investment_per_stock, 
                    CASE 
                        WHEN s.max_positions > 0 THEN (COALESCE(s.allocated_capital, 0) / s.max_positions)
                        ELSE COALESCE(s.allocated_capital, 0)
                    END
                )
            )
    END as available_for_next_order

FROM strategy_config s
LEFT JOIN strategy_holdings sh ON sh.strategy_id = s.id
LEFT JOIN pending_orders po ON po.strategy_id = s.id;

-- Grant permissions
GRANT SELECT ON strategy_net_positions TO authenticated, service_role;
GRANT SELECT ON strategy_capital_status TO authenticated, service_role;
