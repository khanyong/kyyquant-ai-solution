
-- Strategy Market & Multi-Account System Schema (Finalized)

-- [Reused Tables]
-- using: strategies (id, name, type, config, user_id)
-- using: users (id, name, email)

-- 1. user_trading_accounts (Multi-Account Support)
-- Stores individual brokerage accounts. Replaces/Augments the simple 'kiwoom_account' column in 'users'.
CREATE TABLE IF NOT EXISTS user_trading_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    account_type VARCHAR(20) CHECK (account_type IN ('mock', 'real')),
    account_number VARCHAR(20) NOT NULL,
    account_name VARCHAR(100),
    broker VARCHAR(20) DEFAULT 'kiwoom',
    
    -- OAuth / Security
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_active BOOLEAN DEFAULT false,
    is_connected BOOLEAN DEFAULT false,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    
    -- Balance Info (Synced from Broker)
    initial_balance DECIMAL(15, 2),
    current_balance DECIMAL(15, 2),
    available_balance DECIMAL(15, 2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, account_number)
);

-- 2. strategy_marketplace (App Store Listing)
-- Decouples "Business Info" from "Execution Logic" (strategies table).
CREATE TABLE IF NOT EXISTS strategy_marketplace (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES strategies(id), -- Points to the existing logic table
    creator_id UUID REFERENCES auth.users(id),
    
    -- Storefront Data
    title VARCHAR(100) NOT NULL, -- Marketing Title (might differ from internal name)
    description TEXT,
    tags TEXT[], 
    logo_url TEXT,
    
    -- Business Model
    fee_type VARCHAR(20) CHECK (fee_type IN ('monthly_sub', 'profit_share', 'free')),
    fee_amount DECIMAL(10, 2),
    min_capital DECIMAL(15, 2),
    
    -- Validated Metrics (Cached for Sorting)
    total_return DECIMAL(10, 2),
    cagr DECIMAL(10, 2),
    mdd DECIMAL(10, 2),
    win_rate DECIMAL(5, 2),
    subscriber_count INTEGER DEFAULT 0,
    
    is_public BOOLEAN DEFAULT false,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. strategy_subscriptions (The Link)
-- Records the "Follow" relationship.
CREATE TABLE IF NOT EXISTS strategy_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    follower_id UUID REFERENCES auth.users(id),
    follower_account_id UUID REFERENCES user_trading_accounts(id), -- Where to execute trades
    market_strategy_id UUID REFERENCES strategy_marketplace(id),
    
    -- Copy Trading Config
    allocation_amount DECIMAL(15, 2),
    allocation_type VARCHAR(20) DEFAULT 'fixed_amount', 
    multiplier DECIMAL(4, 2) DEFAULT 1.0, -- Risk scaling
    
    status VARCHAR(20) CHECK (status IN ('active', 'paused', 'expired')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(follower_id, market_strategy_id)
);

-- 4. strategy_daily_performance (The Charting Data)
-- Existing 'backtest_results' is for static tests. This is for live track record.
CREATE TABLE IF NOT EXISTS strategy_daily_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES strategies(id),
    date DATE NOT NULL,
    
    -- Metrics for the day
    daily_return_pct DECIMAL(5, 2),
    total_return_pct DECIMAL(10, 2),
    equity_value DECIMAL(15, 2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(strategy_id, date)
);

-- 5. copy_trading_logs (The Execution History)
CREATE TABLE IF NOT EXISTS copy_trading_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID REFERENCES strategy_subscriptions(id),
    
    -- Traceability
    original_signal_id UUID, -- Can link to trading_signals(id) if needed
    follower_order_id UUID, -- Link to executed order
    
    status VARCHAR(20),
    failure_reason TEXT,
    
    execution_price DECIMAL(10, 2),
    slippage DECIMAL(10, 2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE user_trading_accounts ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own accounts" ON user_trading_accounts;
CREATE POLICY "Users can view own accounts" ON user_trading_accounts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own accounts" ON user_trading_accounts FOR ALL USING (auth.uid() = user_id);

ALTER TABLE strategy_marketplace ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public can view active strategies" ON strategy_marketplace;
CREATE POLICY "Public can view active strategies" ON strategy_marketplace FOR SELECT USING (true);
