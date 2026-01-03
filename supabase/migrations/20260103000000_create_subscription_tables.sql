-- Migration: Strategy Universes (Refined)

-- 1. Create strategy_universes table (If not exists)
-- Maps a Strategy to one or more Universes (Filters)
-- Verified: strategies table already has allocated_capital and allocated_percent columns.

CREATE TABLE IF NOT EXISTS strategy_universes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    investment_filter_id UUID NOT NULL REFERENCES kw_investment_filters(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(strategy_id, investment_filter_id)
);

-- RLS for strategy_universes
ALTER TABLE strategy_universes ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_policies 
        WHERE tablename = 'strategy_universes' 
        AND policyname = 'Users can manage their own strategy universes'
    ) THEN
        CREATE POLICY "Users can manage their own strategy universes"
            ON strategy_universes
            USING (
                strategy_id IN (SELECT id FROM strategies WHERE user_id = auth.uid())
            )
            WITH CHECK (
                strategy_id IN (SELECT id FROM strategies WHERE user_id = auth.uid())
            );
    END IF;
END $$;
